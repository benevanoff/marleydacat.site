import os
import uuid
import logging
from pydantic import BaseModel

from fastapi import FastAPI, Request, Depends, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware

from .user_routes import user_router
from .posting_routes import posts_router

app = FastAPI()

# CORS
origins = [
    "http://127.0.0.1",
    "http://localhost",
    "http://192.168.1.167",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://192.168.1.167:3000",
    "http://marleydacat.site",
    "https://marleydacat.site",
    "http://http://146.190.141.184",
    "https://www.benevanoff.dev"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie"]
)

# route handlers
@app.get("/")
def root():
    return "Marley says meow"

app.include_router(user_router)
app.include_router(posts_router)