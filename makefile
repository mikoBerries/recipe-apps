server:
	./myDjangoProject/manage.py runserver

migration:
	py ./myDjangoProject/manage.py makemigrations

migrate:
	py ./myDjangoProject/manage.py migrate

shell:
	py ./myDjangoProject/manage.py shell

collectstatic:
	py ./myDjangoProject/manage.py collectstatic

depedency:
	py -m pip freeze > requirement.txt

container:
	docker build .

shell:
	docker exec -it app bin/sh

.phony: server migration migrate shell collectstatic depedency container shell
