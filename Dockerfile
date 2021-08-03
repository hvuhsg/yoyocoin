FROM python:3.8-alpine

WORKDIR /app

# Install dependencies.

## Install IPFS node
RUN apt install ipfs
RUN ipfs init

## Install python lib's
ADD requirements.txt /app
RUN cd /app && \
    pip install -r requirements.txt

# Add actual source code.
ADD src /app

EXPOSE 6001
EXPOSE 5001
EXPOSE 4001
EXPOSE 8080

CMD [ "ipfs", "daemon", "--enable-pubsub-experiment", "&", "python", "app/manager.py"]
