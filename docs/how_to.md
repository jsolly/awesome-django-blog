## Create a new migration

    ```bash
    $ python3 manage.py makemigrations --name changed_my_model your_app_label

    $ python3 manage.py migrate
    ```


## Overwrite heroku Postgres database with local database

    ```bash
    # First, list your Heroku apps to find the correct app name
    heroku apps
    
    # Reset the database (replace YOUR_APP_NAME with your actual app name)
    heroku pg:reset DATABASE --app YOUR_APP_NAME --confirm YOUR_APP_NAME
    
    # Get the Postgres URL for your app
    heroku config:get DATABASE_URL --app YOUR_APP_NAME
    
    # Import your local database backup
    psql <heroku_postgres_url>
    \i <path_to_local_db_backup.sql>
    ```



## Export prod database and restore locally (Untested)

    ```bash
    # Get database URL from Heroku
    heroku config:get DATABASE_URL --app your-app-name > ~/.pg_heroku_url

    # Create backup using Heroku Postgres credentials
    pg_dump $(cat ~/.pg_heroku_url) > ~/code/awesome-django-blog/backups/blogthedata_db_$(date +%d_%m_%Y).sql

    # Restore locally
    psql -U postgres
    postgres=# DROP DATABASE blogthedata;
    postgres=# CREATE DATABASE blogthedata;
    postgres=# \q
    psql blogthedata < ~/code/awesome-django-blog/backups/blogthedata_db_$(date +%d_%m_%Y).sql

    # Optionally sync media files from S3 to local (if using S3 for media storage)
    aws s3 sync s3://your-bucket-name/media ~/code/awesome-django-blog/app/media
    ```

## Create manual backup of Heroku database

    ```bash
    # Manual backup using Heroku CLI
    heroku pg:backups:capture --app your-app-name

    # Download latest backup
    heroku pg:backups:download --app your-app-name

    # List existing backups
    heroku pg:backups --app your-app-name
    ```

Note: Heroku Postgres automatically creates periodic backups based on your plan. You can view them in the Heroku dashboard or using `heroku pg:backups --app your-app-name`.


## Send local media files to S3
``` bash
# Upload local media files to S3 bucket
aws s3 sync mediafiles/ s3://your-bucket-name/media

# Verify files were uploaded
aws s3 ls s3://your-bucket-name/media/
```



## Roll back migration

    ```
    python3 manage.py migrate blog 0011
    ```

## Fake Migration

```
python manage.py migrate --fake blog 0011
```

## Create empty migration

    ```
    python3 manage.py migrate --empty --name changed_my_model your_app_label
    ```


## Resolve django-fastdev template errors on admin page

Might be related to https://code.djangoproject.com/ticket/32681 I logged this
one https://github.com/dmpayton/django-admin-honeypot/issues/90 Add this to
venv/lib/python3.9/site-packages/django/contrib/admin/sites.py

```py
    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.

        For sites running on a subpath, use the SCRIPT_NAME value if site_url
        hasn't been customized.
        """
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url
        return {
            'site_title': self.site_title,
            'subtitle': None,
            'site_header': self.site_header,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request),
            'is_popup': False,
            'is_nav_sidebar_enabled': self.enable_nav_sidebar,
        }
```

## Fix Coveralls Badge updating issue
https://github.com/lemurheavy/coveralls-public/issues/971#issuecomment-693623226


## Syntax highlighting link (Prism)

<!--
https://prismjs.com/download.html#themes=prism-dark&languages=markup+css+clike+javascript+apacheconf+bash+git+json+python+sql+typescript+yaml
-->


## Resolve image upload issue (403 from rejected csrf token)

I added the following to
.venv/lib/python3.10/site-packages/django_ckeditor_5/views.py

from django.views.decorators.csrf import csrf_exempt

```py
@csrf_exempt
def upload_file(request):
    if request.method == "POST" and request.user.is_staff:
        form = UploadFileForm(request.POST, request.FILES)
        try:
            image_verify(request.FILES["upload"])
        except NoImageException as ex:
            return JsonResponse({"error": {"message": "{}".format(str(ex))}})
        if form.is_valid():
            url = handle_uploaded_file(request.FILES["upload"])
            return JsonResponse({"url": url})
    raise Http404(_("Page not found."))
```