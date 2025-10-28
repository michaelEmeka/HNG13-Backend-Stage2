from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="cache"), name="static")