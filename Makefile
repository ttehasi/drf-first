PORT ?= 8000

install:
	uv sync

run:
	uv run python web/manage.py runserver

migrate:
	uv run python web/manage.py makemigrations
	uv run python web/manage.py migrate

start:
	uv run gunicorn -w 4 -b 0.0.0.0:$(PORT) app.wsgi:application

collectstatic:
	uv run python web/manage.py collectstatic