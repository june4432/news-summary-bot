# ✅ pip install pyjwt
import jwt
import datetime

from batch.common.config import (
    secret_token_for_login
)

SECRET_TOKEN_FOR_LOGIN = secret_token_for_login

# 사용자 정보 셋업을 위한 로그인 토큰 생성기
def generate_token(user_id: str, is_email=True, expires_in_minutes=60*24*30):
    """
    user_id: 이메일 또는 텔레그램 chat_id
    is_email: True면 이메일, False면 텔레그램 chat_id
    """
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)
    }

    if is_email:
        payload["email"] = str(user_id)
    else:
        payload["chat_id"] = str(user_id)

    token = jwt.encode(payload, SECRET_TOKEN_FOR_LOGIN, algorithm="HS256")

    # ✅ bytes → str 변환 (PyJWT 버전에 따라 다를 수 있음)
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token

# 토큰을 디코드하는 역할 수행
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