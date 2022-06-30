
### Create a new migration
    ```bash
    $ python3 manage.py makemigrations --name changed_my_model your_app_label

    $ python3 manage.py migrate
    ```

### Access the production server
    ```
    $ ssh <username>@69.164.205.120
    ```

### Pull changes from github in prod
  ```bash
  $ source venv/bib/activate
  $ python3 manage.py check --deploy
  $ python3 manage.py migrate # Don't need to makemigrations, because migrations are already in /migrations
  $ sudo service apache2 restart  
  ```

### Test a PR in prod
get fetch
git checkout -b <local_branch_name> origin/<branch_name> # local_branch_name and branch_name can be the same

### Export prod database and restore locally
    ```
    $ sudo -u postgres pg_dump blogthedata > /home/john/blogthedata/backups/blogthedata_db_3_8_22.sql # do this inside prod
    #### The following steps are done on a local dev machine
    $ scp john@198.74.48.211:/home/john/blogthedata/backups/blogthedata_db_6_28_22.sql /Users/johnsolly/Documents/code/blogthedata/backups
    $ psql -U postgres
    postgres=# DROP DATABASE blogthedata;
    postgres=# CREATE DATABASE blogthedata;
    postgres=# exit
    $ psql blogthedata < /Users/johnsolly/Documents/code/blogthedata/backups/blogthedata_db_5_6_22.sql
    $ scp -r john@69.164.205.120:/home/john/blogthedata/django_project/media /Users/johnsolly/Documents/code/blogthedata/django_project # Optionally copy media folder over (to get uploaded images)
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

    ```
    # Troubleshooting
    $ sudo nginx -t # Check Nginx configuration
    $ sudo systemctl restart nginx # Restart Nginx
    ## Restart Gunicorn
    $ sudo systemctl daemon-reload
    $ sudo systemctl restart gunicorn

    # Take a look at gunicorn configuration
    $ cd ~/blogthedta/django_project
    $ gunicorn --print-config django_project.wsgi:application
    ```
    
### Create new venv
    ```
    make sure an up-to-date pip freeze has happened
    make sure you're using the right python version

    $ python3 -m venv ~/venv
    $ source ~/venv/bin/activate
    $ python3 -m pip install --upgrade pip
    $ python3 -m pip install wheel
    $ python3 -m pip install -r ~/blogthedata/django_project/requirements/requirements.txt
    ```

### Manually generated integrity hash values
    ```
        1 - mailchimp/local-mc-validate.js
        2 - Everything in favicon/
    ```

# How to generate integrity hash values
    ```
    openssl dgst -sha384 -binary prism_patched.min.js | openssl base64 -A
    ```

# Configuring Python install on new Mac
    ```
    Install using the regular installer from python.org. Make sure to match the version that is on production.
    The file path should look like:
    /Applications/"Python 3.8"/IDLE.app/Contents/MacOS/Python

    Go into Applications/<Python Directory>
    Open 'Install Certificates.command'
    Open Update Shell Profile.command
    ```


 ### Roll back migration
    ```
    python3 manage.py migrate blog 0011
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

# Not needed anymore
    ```
    python3 manage.py collectstatic
    scp jsolly@69.164.205.120:/home/jsolly/blogthedata/django_project/db.sqlite3 .
    ```

### Upgrade django
    ```
    - Check for depreciations and make sure unit tests are passing
    python3 -Wa manage.py test
    - Freeze dependencies
    pip freeze > requirements_5_4_22.txt
    - Upgrade
    pip install Django==3.2.13
    - Re-run unit tests
    - commit dependencies to source control
    - use dependencies to upgrade prod
    pip install -r requirements_5_4_22.txt
    ```
### Backup Prod
    ```
    $ssh <username>@69.164.205.120 "dd if=/dev/sda " | dd of=/Users/johnsolly/Documents/code/blogthedata/backups/linode.img
    ```

### Resolve django-fastdev template errors on admin page
Might be related to https://code.djangoproject.com/ticket/32681
I logged this one https://github.com/dmpayton/django-admin-honeypot/issues/90 
Add this to
django_project/venv/lib/python3.9/site-packages/django/contrib/admin/sites.py
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


### Stop tracking local db.sqlite3 file
```
$ git update-index --assume-unchanged <file-to-ignore>
```

#### tell Git to stop ignoring this file
```bash
$ git update-index --no-assume-unchanged <file-to-ignore>
```

### Send media files to remote server
scp -r /Users/johnsolly/Documents/code/blogthedata/django_project/media john@198.74.48.211:~/blogthedata/django_project

### Send backup to remote server
$ scp -r /Users/johnsolly/Documents/code/blogthedata/backups/blogthedata_db_6_20_22.sql john@198.74.48.211:~/blogthedata/backups