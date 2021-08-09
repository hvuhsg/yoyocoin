import uvicorn

from config import API_PORT, API_HOST

from .api import app


def run():
    uvicorn.run(app, host=API_HOST, port=API_PORT)
