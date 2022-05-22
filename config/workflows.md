
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

### Export prod database and restore locally
    ```
    $ sudo -u postgres pg_dump blogthedata > blogthedata_db_3_8_22.sql # do this inside prod
    #### The following steps are done on a local dev machine
    $ scp jsolly@69.164.205.120:/home/jsolly/backups/blogthedata_db_3_8_22.sql .
    $ psql -U postgres
    postgres=# DROP DATABASE blogthedata;
    postgres=# CREATE DATABASE blogthedata;
    postgres=# exit
    $ psql blogthedata < blogthedata_db_5_6_22.sql
    $ scp -r jsolly@69.164.205.120:/home/jsolly/blogthedata/django_project/media /Users/johnsolly/Documents/code/blogthedata/django_project # Optionally copy media folder over (to get uploaded images)
    ```

### useful commands and paths
    ```
    $ psql -U postgres # log into postgres
    $ ngrok http 8000 # Test on mobile locally
    $ sudo tail -f /var/log/apache2/access.log
    $ sudo tail -f /var/log/apache2/error.log
    $ sudo nano /etc/django_config.json 
    $ sudo nano -c /etc/apache2/sites-available/django_project.conf
    $ sudo nano /var/log/postgresql/postgresql-13-main.log
    $ sudo nano /etc/postgresql-common/createcluster.conf 
    $ sudo nano /etc/apache2/apache2.conf
    $ sudo service postgresql restart
    $ sudo chmod -R XXX blogthedata
    $ sudo -i # become root user
    
    ```

### Create new venv
    ```
    make sure an up-to-date pip freeze has happened
    make sure you're using the right python version

    $ python3 -m pip install virtualenv
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
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
    /Applications/"Python 3.9"/IDLE.app/Contents/MacOS/Python

    Go into Applications/<Python Directory>
    Open 'Install Certificates.command'
    ```


 ### Roll back migration
    ```
    python3 manage.py migrate blog 0011
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