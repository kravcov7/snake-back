from jose import jwt
from models import User
from typing import Annotated
from starlette import status
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, root_validator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from settings import SECRET_KEY, ALGORITHM
from dependencies import bcrypt_context, db_dependency_type

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


class CreateUserModel(BaseModel):
    username: str
    email: str
    password: str
    hashed_password: str = Field(...)

    @root_validator(pre=True)
    def password_hasher(cls, values):
        password = values.get('password')
        if password:
            hashed_password = bcrypt_context.hash(password)
            values['hashed_password'] = hashed_password
        return values


class TokenModel(BaseModel):
    access_token: str
    token_type: str


async def authenticate_user(username: str, password: str, db):
    user = await db.get(User, User.username == username)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM[0])


@router.post('/register')
async def register_user(user: CreateUserModel, db: db_dependency_type):
    user_to_create = User(**user.dict(exclude={'password'}))

    db.add(user_to_create)
    await db.commit()
    await db.refresh(user_to_create)

    return {'username': user_to_create.username, 'hashed_password': user_to_create.hashed_password}


@router.post('/token', response_model=TokenModel)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency_type):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

    token = create_access_token(username=user.username, user_id=user.id, expires_delta=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
