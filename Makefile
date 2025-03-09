SHELL=bash

# Note: the dependencies are not very well described. Don't do make -j

run:
	source .venv/bin/activate && ./manage.py runserver

migrate:
	source .venv/bin/activate && ./manage.py makemigrations
	source .venv/bin/activate && ./manage.py migrate

