from pydantic import BaseModel


class BearerRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
