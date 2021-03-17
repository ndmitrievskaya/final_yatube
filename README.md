# Yatube - social network 

Yatube is a social network for posting diaries and sharing thoughts with subscribers. 

## Getting Started

You may clone the repository and run it on your local machine.


### Installing

After cloning the repository you should install requirements.

```
pip install -r requirements.txt
```

### How to use
To start the app you need only one simple command, but first you need to collect static. 
You may do it with the command below

```
python manage.py collectstatic
```

You will also need to make migrations and create superuser using commands below

```
python manage.py migrate
python manage.py createsuperuser 
```

Finally, for running the service you may use the command below

```
python manage.py runserver
```

Then it will be callable on the host [localhost:8000/](localhost:8000/)

## Built With

* [Django](https://docs.djangoproject.com/en/3.1/) - The web framework

## Authors

* **Nika Dmitrievskaya** - *Initial work* - [ndmitrievskaya](https://github.com/ndmitrievskaya)
