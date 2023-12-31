# Recipe-Apps
-------------
* advanced REST API with Python, Django REST Framework and Docker using Test Driven Development (TDD).
* Tech Stack :
    1. Python & Django.
    2. PostgreSQL database.
    3. Swagger-ui documentation.
    4. GitHub Action CI/CD.
    5. TDD test approch.

* Django project strucute:
    1. app/ : Django project.
    2. app/core/ : Core Code shared between other apps (Database Django.Model).
    3. app/user/ : Populate User related code (user regisration & Auth Token).
    4. app/recipe/ : Populate Recipe related code (CRUD Recipe).

* flake8 linting for python.

* postgrsql adapter for django to connect: (https://pypi.org/project/psycopg2/)
    - psycopg2-binary: good for development only & work in many machine like alpine
    - psycopg2 : compiles from source & required depedency

* Django rest framework documentation (https://www.django-rest-framework.org/)
* Django Database using ORM - Object Rlational Mapper.

* Django model already come with base user with many fucntion to use for managing user in aplication.

* Creating API documentation with drf-spectacular to create API Schema and server it as swagger.

* APIView:
    - focused for HTTP methods.
    - Class methods for HTTP method(GET, POST, PUT, PATCH, DELETE).
    - Provide felixibility over URLs and logic.
    - Useful for non CRUD APIs:
        1. Avoid for simple CRUD APIs.
        2. for bespoke logic (auth, jobs, external apis).

* Viewsets:
    - Focused around actions (Retrieve, list, update, partial update, destroy)
    - Map to Django models.
    - Use Router to generate URLs.
    - Great for CRUD operations on modles.

* viewsets.GenericViewSet with mixins:
    - viewsets.GenericViewSet are empty class used to colabroate with mixins for making a views that accept mixins we want. 

* rest_framework router will mapping default Route for get,put,patch,delete in Viewset declared function(retrive, update, partial_update, destroy):
```code
    mapping={
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }
```
* working with models.ImageField / models.FileField : (https://docs.djangoproject.com/en/4.2/ref/models/fields/#filefield)

* django model for times for create_at & update_on data : https://www.hacksoft.io/blog/timestamps-in-django-exploring-auto-now-auto-now-add-and-default


# Deployment on django
----------------------
![Django architechture](https://robotforestio.files.wordpress.com/2020/08/wsgi-nginx-uwsgi.png)

* static files in django better to server in diffrent services
* Django & uWSGI : (https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/uwsgi/)
    - uWSGI operates on a client-server model. Your web server (e.g., nginx, Apache) communicates with a django-uwsgi “worker” process to serve dynamic content.
    - uWSGI params for server (https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html#what-is-the-uwsgi-params-file)

# ETC
------
* Django & mongo DB (https://www.mongodb.com/compatibility/mongodb-and-django).

* Chanching with django (https://docs.djangoproject.com/en/4.2/topics/cache/#:~:text=redis%2Dpy%20is%20the%20binding,Set%20BACKEND%20to%20django.)
* Django memchace support string vs redis support map with many data set and easy to manage with aplication redis db.(https://awstip.com/django-caching-with-redis-c66ab2126c8a).