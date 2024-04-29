### Create a new migration

    ```bash
    $ python3 manage.py makemigrations --name changed_my_model your_app_label

    $ python3 manage.py migrate

    $ python3 manage.py migrate --settings=django_project.settings.ci
    ```

### Access the production server

    ```
    ssh john@198.74.48.211
    ```

### Pull changes from github in prod

```bash
$ source venv/bin/activate
$ python3 manage.py check --deploy
$ python3 manage.py migrate # Don't need to makemigrations, because migrations are already in /migrations
$ sudo service apache2 restart
```

### Test a PR in prod

get fetch git checkout -b <local_branch_name> origin/<branch_name> #
local_branch_name and branch_name can be the same

### Export prod database and restore locally

    ```
    sudo -u postgres pg_dump blogthedata > ~/blogthedata/backups/blogthedata_db_DD_MM_YYYY.sql # do this inside prod
    #### The following steps are done on a local dev machine
    scp john@198.74.48.211:~/blogthedata/backups/blogthedata_db_DD_MM_YYYY.sql ~/code/awesome-django-blog/backups
    psql -U postgres
    postgres=# DROP DATABASE blogthedata;
    postgres=# CREATE DATABASE blogthedata;
    postgres=# exit
    psql blogthedata < ~/code/awesome-django-blog/backups/blogthedata_db_DD_MM_YYYY.sql
    # Optionally copy media folder over (to get uploaded images)
    scp -r john@198.74.48.211:~/blogthedata/app/media ~/code/awesome-django-blog/app 
    ```

### useful commands and paths

    ```
    $ sudo -u postgres psql # Log into postgres (remote)
    $ psql -U postgres -h 127.0.0.1 # log into postgres (remote option 2)
    $ \c DBNAME # Switch databases while in postgres shell
    $ ngrok http 8000 # Test on mobile locally
    $ sudo journalctl -u nginx # Check the Nginx process logs
    $ sudo less /var/log/nginx/access.log # Check the Nginx access logs
    $ sudo less /var/log/nginx/error.log # Check the Nginx error logs
    $ sudo journalctl -u gunicorn # Check the Gunicorn application logs by typing:
    $ sudo journalctl -u gunicorn.socket # Check the Gunicorn socket logs by typing: s
    $ sudo nano /etc/nginx/sites-available/django_project # congigure Nginx
    $ sudo service postgresql restart
    $ sudo chmod -R XXX blogthedata
    $ sudo -i # become root user
    $ sudo do-release-upgrade -c # Check for new Ubutu version

    ```

### Troubleshooting

    ```
    $ sudo nginx -t
    $ sudo systemctl restart nginx
    $ sudo systemctl restart gunicorn

    # If you If you change Gunicorn socket or service files, reload the daemon and restart the process by typing:
    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn.socket gunicorn.service

    # Take a look at gunicorn configuration
    $ cd ~/blogthedta/django_project
    $ gunicorn --print-config django_project.wsgi:application

    $ sudo nano /etc/systemd/system/gunicorn.socket
    $ sudo nano /etc/systemd/system/gunicorn.service
    /home/john/blogthedata/venv/bin

    The following logs may be helpful:

    Check the Nginx process logs by typing: sudo journalctl -u nginx
    Check the Nginx access logs by typing: sudo less /var/log/nginx/access.log
    Check the Nginx error logs by typing: sudo less /var/log/nginx/error.log
    Check the Gunicorn application logs by typing: sudo journalctl -u gunicorn
    Check the Gunicorn socket logs by typing: sudo journalctl -u gunicorn.socket

    ```

# How to generate integrity hash values

    ```
    openssl dgst -sha384 -binary prism_patched.min.js | openssl base64 -A
    ```

### Roll back migration

    ```
    python3 manage.py migrate blog 0011
    ```

### Fake Migration

```
python manage.py migrate --fake blog 0011
```

### Create empty migration

    ```
    python3 manage.py migrate --empty --name changed_my_model your_app_label
    ```

### Roll back a currupt db on production

    ```
    #### Log into postgres
    psql -U postgres
    #### drop existing database
    postgres=# DROP DATABASE blogthedata;
    #### Create an empty db
    postgres=# CREATE DATABASE blogthedata;
    type <exit> and hit enter to go back to the terminal
    #### Cd to the backups folder and restore the db
    psql blogthedata < blogthedata_db_5_5_22.sql
    #### If that doesn't work, try
    sudo -u postgres psql blogthedata < blogthedata_db_5_5_22.sql
    ```

### Backup Prod

    ```
    $ssh <username>@69.164.205.120 "dd if=/dev/sda " | dd of=/Users/johnsolly/Documents/code/blogthedata/backups/linode.img
    ```

### Resolve django-fastdev template errors on admin page

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

### Send media files to remote server

scp -r /Users/johnsolly/Documents/code/blogthedata/django_project/media
john@198.74.48.211:~/blogthedata/django_project

### Send backup to remote server

```
$ scp -r
/Users/johnsolly/Documents/code/blogthedata/backups/blogthedata_db_6_20_22.sql
john@198.74.48.211:~/blogthedata/backups
```

## Port mapping

```shell
ssh -N -L 10000:127.0.0.1:80 john@198.74.48.211
```

### Resolve image upload issue (403 from rejected csrf token)

I added the following to
venv/lib/python3.8/site-packages/django_ckeditor_5/views.py

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

### Syntax highlighting link (Prism)

<!--
https://prismjs.com/download.html#themes=prism-dark&languages=markup+css+clike+javascript+apacheconf+bash+git+json+python+sql+typescript+yaml
-->

## Misc
env EDITOR=nano crontab -e

## Fix Coveralls Badge updating issue
https://github.com/lemurheavy/coveralls-public/issues/971#issuecomment-693623226