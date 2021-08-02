import uvicorn

from config import API_PORT

from .api import app


def run():
    uvicorn.run(app, host="127.0.0.1", port=API_PORT)
