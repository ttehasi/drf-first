FROM python:3.12.2-slim

RUN apt-get update && apt-get install -yq make \
                && pip install uv

WORKDIR /app

COPY . .

RUN uv sync

RUN make migrate

CMD ["make", "start"]