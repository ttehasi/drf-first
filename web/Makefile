PORT ?= 8000

install:
	uv sync

run:
	uv run python manage.py runserver

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

start:
	uv run gunicorn -w 4 -b 0.0.0.0:$(PORT) app.wsgi:application

collectstatic:
	uv run python manage.py collectstatic

loaddb: migrate
	uv run python manage.py loaddata yard_control_data user_data