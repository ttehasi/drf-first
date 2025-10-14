PORT ?= 8000
run:
	uv run python manage.py runserver

migrate:
	uv run python manage.py makemigration
	uv run python manage.py migrate

start:
    uv run gunicorn -w 4 -b 0.0.0.0:$(PORT) app.wsgi