# Migrate SQLlite to postgres

## Create empty database in postgres
$ psql -U postgres # Might need sudo -u postgres psql

postgres=# ALTER ROLE postgres WITH PASSWORD 'secret123';

postgres=# CREATE DATABASE blogthedata;

Check settings.py to make sure sqllite db is enabled
## Export data from sqlite to json file
$ python3 manage.py dumpdata > ../datadump.json

Next, Add engine info to settings.py

make sure psycopg2 is installed. You might need to run these commands
sudo apt-get install libpq-dev
pip install psycopg2-binary
pip install psycopg2

## Create empty tables (schema) in postgres
$ python3 manage.py migrate --run-syncdb 

## Troubleshooting

To overcome this error
> django.db.utils.ProgrammingError: relation "blog_category" does not exist

Uncomment line in forms.py so that categories are not fetched before the table is created

To overcome this error
> django.db.utils.IntegrityError: Problem installing fixture Could not load contenttypes.ContentType

Remove auto added contenttypes from django for loading data

$ python3 manage.py shell

from django.contrib.contenttypes.models import ContentType

ContentType.objects.all().delete()

If you run into this error:
> Key (id)=(1) already exists

try commenting out pre-save methods (signals.py)

## Load data into postgres!

$ python3 manage.py loaddata ../datadump.json