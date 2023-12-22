import logging
import time
from typing import Tuple

import jwt
from sqlalchemy.exc import SQLAlchemyError

from be.model import db_conn, error
from be.model.tables import UserTable

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str):
    decoded = jwt.decode(encoded_token, key=user_id, algorithms=["HS256"])
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
            return False
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str, username: str = "user"):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            new_user = UserTable(
                user_id=user_id,
                user_name=username,
                password=password,
                balance=0,
                token=token,
                terminal=terminal,
            )
            self.conn.add(new_user)
            self.conn.commit()
        except SQLAlchemyError as e:
            print(e)
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> Tuple[int, str]:
        user = self.conn.query(UserTable).filter_by(user_id=user_id).first()
        if user is None:
            return error.error_authorization_fail()
        db_token = user.token
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> Tuple[int, str]:
        user = self.conn.query(UserTable).filter_by(user_id=user_id).first()
        if user is None or password != user.password:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> Tuple[int, str, str]:
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)

            user = self.conn.query(UserTable).filter_by(user_id=user_id)
            if user is None:
                return error.error_authorization_fail() + ("",)
            user.update({"token": token, "terminal": terminal})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> Tuple[int, str]:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            user = self.conn.query(UserTable).filter_by(user_id=user_id)
            if user is None:
                return error.error_authorization_fail()
            user.update({"token": dummy_token, "terminal": terminal})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> Tuple[int, str]:
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            user = self.conn.query(UserTable).filter_by(user_id=user_id)
            if user is None:
                return error.error_authorization_fail()
            user.delete()
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Tuple[int, str]:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            user = self.conn.query(UserTable).filter_by(user_id=user_id)
            if user is None:
                return error.error_authorization_fail()
            user.update(
                {"password": new_password, "token": token, "terminal": terminal}
            )

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_user_name(
        self, user_id: str, token: str, user_name: str
    ) -> Tuple[int, str]:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            user = self.conn.query(UserTable).filter_by(user_id=user_id)
            if user is None:
                return error.error_authorization_fail()
            user.update({"user_name": user_name})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
