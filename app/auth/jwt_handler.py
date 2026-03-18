from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
    
EXPIRY_TIME = 3600
def create_token(user_id: int):
    payload = {"user_id" : user_id,
               "exp" :  datetime.utcnow() + timedelta(seconds= EXPIRY_TIME)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token