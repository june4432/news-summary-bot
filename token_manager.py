# ✅ pip install pyjwt
import jwt
import datetime
from config import (
    secret_token_for_login
)

SECRET_TOKEN_FOR_LOGIN = secret_token_for_login

def generate_token(email: str, expires_in_minutes=60*24*30):  # 30일짜리
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)
    }
    token = jwt.encode(payload, SECRET_TOKEN_FOR_LOGIN, algorithm="HS256")

    # ✅ bytes → str 변환
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token

def decode_token(token: str):
    try:
        # ✅ 바이트 문자열인 경우 처리
        if isinstance(token, bytes):
            token = token.decode()

        # ✅ 문자열이 b'abc' 형식으로 들어온 경우 (실수로 str(token)된 경우) 처리
        if token.startswith("b'") or token.startswith('b"'):
            token = token[2:-1]

        decoded = jwt.decode(token, SECRET_TOKEN_FOR_LOGIN, algorithms=["HS256"])
        return decoded["email"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None