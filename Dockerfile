FROM python:3.8-alpine

WORKDIR /app

# Install dependencies.

## Install python lib's
ADD requirements.txt /app
RUN cd /app && \
    pip install -r requirements.txt

# Add actual source code.
ADD src /app

EXPOSE 6001

CMD ["echo", "$pwd"]
