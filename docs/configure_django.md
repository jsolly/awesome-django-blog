- create linode
- local$ ssh root@<ip_address> (from local)

### Initial Hardening

```sh
$ apt update -y
$ apt dist-upgrade -y
$ reboot
$ apt update -y
$ apt install unattended-upgrades
$ dpkg-reconfigure --priority=low unattended-upgrades
$ useradd -m -s /bin/bash john && passwd john
$ ls /home # should show new user's folder
$ cat /etc/passwd # New user should be at the bottom of the file
$ which sudo # Should output /usr/bin/sudo. If not, run apt install sudo
$ visudo # See groups
$ usermod -aG sudo john # Add john to sudo group
$ groups john # Should show that he is in the sudo group
$ su - john # Switch to john user
john$ sudo apt update # Make sure john can run a sudo command
$ exit # You might need to do this twice to get back to local machine
local$ ssh-copy-id -i ~/.ssh/id_rsa.pub john@<ip_address>
local$ ssh john@<ip_address>
john$ sudo nano /etc/ssh/sshd_config
# Change PermitRootLogin to <no>
# Uncomment PasswordAuthentication and change to no
# Add <AllowUsers john> bellow MaxSessions
$ sudo systemctl restart sshd
$ sudo service ssh status # Make sure it is running
local$ ssh john@<ip_address> # make sure you can still ssh in, in a new tab
john$ ss -atpu # Observe open ports to make sure it's all good!
$ hostnamectl set-hostname django-server
$ nano /etc/hosts # add a line of <<ip_address> blogthedata.com django-server>
# TODO: Add firewall rules
```

### Configuring App

```sh
$ sudo apt update -y
$ sudo apt-get install python3-venv -y
# Follow tutorial to get ssh keys on the server
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
$ git clone git@github.com:jsolly/blogthedata.git
$ python3 -m venv ~/venv
$ source ~/venv/bin/activate
$ python3 -m pip install --upgrade pip
$ python3 -m pip install -r ~/blogthedata/django_project/requirements/requirements.txt
$ nano ~/blogthedata/.env
# copy over parameters from blogthedata/sample.env and set them as needed
$ sudo ufw allow 8000 # We will turn this off later. It's just for testing.
$ python3 manage.py check # Check for any issues
$ python3 ~/blogthedata/django_project/manage.py runserver 0.0.0.0:8000
# in a browser navigate to <ip_address>:8000
# App should be loading
```

### Install dependencies

```bash
$ sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx
# Follow directions on https://launchpad.net/~ubuntugis/+archive/ubuntu/ppa?field.series_filter=focal to install postgis. I did:
$ sudo add-apt-repository ppa:ubuntugis/ppa
$ sudo apt update
$ apt install postgis
$ sudo -U postgres psql
postgres=# CREATE USER blogthedatauser WITH PASSWORD 'password';
postgres=# ALTER ROLE blogthedatauser SET client_encoding TO 'utf8';
postgres=# ALTER ROLE blogthedatauser SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE blogthedatauser SET timezone TO 'UTC';
postgres=# CREATE DATABASE blogthedata WITH OWNER blogthedatauser;
postgres=# \c blogthedata
postgres=# CREATE extension postgis;
postgres=# SELECT PostGIS_version();
```

### A note on an existing database being imported. You may need to run these commands:

```
$ sudo su postgres
$ psql blogthedata -c "GRANT ALL ON ALL TABLES IN SCHEMA public to blogthedatauser;"
$ psql blogthedata -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to blogthedatauser;"
$ psql blogthedata -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to blogthedatauser;"
```

### Restore existing DB (If needed)

```
# Copy db into server
postgres=# exit
$ sudo su postgres
$ psql blogthedata < ~/blogthedata/backups/blogthedata_db_6_20_22.sql
```

### Continue working on Gunicorn and Nginx

```
# Follow a guide on Gunicorn/Nginx
$ sudo ufw delete allow 8000
```

### Pre-live

Make sure ALLOWED_HOSTS is correct (remove localhost)

```
$ python3 manage.py check --deploy

# Check this issue for getting media uploads working https://github.com/hvlads/django-ckeditor-5/issues/63
```
