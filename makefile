server:
	./app/manage.py runserver

migration:
	py ./app/manage.py makemigrations

migrate:
	py ./app/manage.py migrate

shell:
	py ./app/manage.py shell

collectstatic:
	py ./app/manage.py collectstatic

depedency:
	py -m pip freeze > requirement.txt

container:
	docker build .

shells:
	docker exec -it app bin/sh

dockerbuild:
	docker-compose build

dockerup:
	docker-compose up

dockerdown:
	docker-compose down

.phony: server migration migrate shell collectstatic depedency container shell
