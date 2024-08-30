from config import settings


def get_reset_message(token):
    url = f"{settings.front.url}{settings.front.reset_password_path}?token={token}"
    text = f"""<html>
      <body>
      <p>Здравствуйте. Поступил запрос на смену пароля в приложении.</p>
      <p>
        Перейдите по ссылке, если вы и вправду хотите поменять свой пароль: {url}
      </p>
      <p> Если вы не делали запрос, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""

    return text


def get_login_message(code):
    text = f"""<html>
      <body>
      <p>Здравствуйте. Поступил запрос на аутентификацию в приложении.</p>
      <p>
        Введите следующий код, для того чтобы зайти: {code}
      </p>
      <p> Если вы не делали запрос, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""

    return text
