import uvicorn

from config import Config

from .api import app


def run():
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
