from typing import Optional

from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users import exceptions, models
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema, MessageType

from models import User
from database import get_user_db, MySQLAlchemyUserDatabase
from config import settings
from uuid import UUID
from mail_sender import get_reset_message, conf
from schemas.user import UserCreate

SECRET = settings.auth.secret_key


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)
        details = []

        existing_user_by_email = await self.user_db.get_by_email(user_create.email)
        if existing_user_by_email is not None:
            details.append("User with this email already exists.")

        existing_user_by_phone = await self.user_db.get_by_phone(user_create.phone)
        if existing_user_by_phone is not None:
            details.append("User with this phone already exists.")

        existing_user_by_name = await self.user_db.get_by_name(user_create.name)
        if existing_user_by_name is not None:
            details.append("User with this name already exists.")

        if details:
            raise HTTPException(status_code=400, detail=details)

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # print(f"User {user.id} has forgotten their password. Reset token: {token}")
        text = get_reset_message(token)
        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=[user.email],
            body=text,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[models.UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.user_db.get_by_login(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        if not user:
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user


async def get_user_manager(user_db: MySQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
