import os
import uuid
import json
import redis
import logging
import nacl.pwhash.argon2id
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter
from fastapi import FastAPI, Request, Depends, HTTPException, Response, Cookie, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .dependencies import get_db

user_router = APIRouter()

class UserSession:
    def __init__(self):
        self.session_storage_client = redis.StrictRedis(host=os.environ.get("CACHE_HOST", "localhost"), port=6379, db=0, password="yourpasswordkkfkfa")

    def makeNewUserSession(self, username):
        session_id = str(uuid.uuid4())
        self.session_storage_client.set(session_id, json.dumps({"username": username}))
        return session_id

    def getUserFromSession(self, session_id):
        return json.loads(self.session_storage_client.get(session_id).decode())["username"]

def get_sessions():
    session_storage = UserSession()
    yield session_storage

def hash_password(password:str):
    return nacl.pwhash.argon2id.str(password.encode('utf-8')).decode('utf-8')

# User Login Route
class LoginRequest(BaseModel):
    username: str
    password: str
@user_router.post("/users/login")
async def user_login(request:LoginRequest, response:Response, rds_client=Depends(get_db), session_storage=Depends(get_sessions)):
    # search for the user in the database
    async with rds_client.cursor() as cur:
        await cur.execute("""
            SELECT * FROM users
            WHERE (username) = (%s)
            """, (request.username))
        user_result_row = await cur.fetchone()
    if not user_result_row:
        raise HTTPException(status_code=401)
    # verify password is correct
    try:
        nacl.pwhash.argon2id.verify(user_result_row['password'].encode('utf-8'), request.password.encode('utf-8'))
    except nacl.exceptions.InvalidkeyError:
        raise HTTPException(status_code=401)
    # add Redis entry {session_id:username} with 2 hour timeout
    session_id = session_storage.makeNewUserSession(request.username)
    # return session id in response body and cookie
    response.set_cookie(key="session_id", value=session_id)

@user_router.post("/users/logout")
async def users_logout(response:Response, session_id:str=Cookie(None), session_storage=Depends(get_sessions)):
    # destroy sessioroutern by deleting session entry from Redis
    if not session_id:
        return
    session_storage.session_storage_client.delete(session_id)
    # and deleting the session cookie from the client
    response.delete_cookie(key="session_id")

@user_router.get("/users/whoami")
async def users_whoami(session_id:str=Cookie(None), rds_client=Depends(get_db), session_storage=Depends(get_sessions)):
    if not session_id:
        return
    username = session_storage.getUserFromSession(session_id)
    async with rds_client.cursor() as cur:
        await cur.execute("""
            SELECT username, email
            FROM users
            WHERE username = %s
            """, (username))
    return await cur.fetchone()