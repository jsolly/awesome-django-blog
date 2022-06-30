# https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/ (See this for the most up-to-date-info)
#!/bin/bash
sudo apt update -y        # Fetches the list of available updates
sudo apt upgrade -y       # Installs some updates; does not remove packages
sudo apt full-upgrade -y  # Installs updates; may also remove some packages, if needed
sudo apt autoremove -y    # Removes any old packages that are no longer needed
sudo apt-get install sqlite3 # Allows you to interact with sqllite db with Python
sudo reboot

### Hostname Configuration
hostnamectl set-hostname <server_name>


## add server ip and new host name to file and save
<server_ip>    <server_name>

adduser <username>
adduser <username> sudo # Add user to sudo group
exit
## Try ssh-ing again as <username>
## If you get a 'Warning about Remote Host Identification has changed', you will have to delete the ip address from
## your hosts file
# sudo nano ~/.ssh/known_hosts # delete the offending line

### SSH Key setup
mkdir -p ~/.ssh

# Now move over to your local machine and follow these directions to generate SSH keys.
# https://docs.github.com/en/enterprise-server@3.0/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys

# Open a seperate terminal (without closing the one connected to the server!)
scp ~/.ssh/id_ed25519.pub <username>@<server_ip>:~/.ssh/authorized_keys # Copy public key to server

# File permissions to .ssh folder (on server)
sudo chmod 700 ~/.ssh/
sudo chmod 600 ~/.ssh/*
exit
# Now log in as new user. You should be able to get in without a password

sudo nano /etc/ssh/sshd_config # disable logging in as root user and password authentication
# Change PermitRootLogin to no
# Change PasswordAuthentication to no
sudo systemctl restart sshd # restart ssh service
sudo service ssh status # Make sure it is running before ya go!
exit

## Set up firewall
sudo apt-get install ufw -y
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable # put all the previous rules into effect
sudo ufw status
exit


## Github
# Generate ssh key and add to Github
# clone django repo to machine


# Create Python Environment
#TODO Take a second look at installing python
sudo apt-get install python3-pip -y
sudo apt-get install python3-venv -y
python3 -m venv ~/blogthedata/django_project/venv
source venv/bin/activate
which python3 #Make sure Python is pointing to the new virtual environment
python3 --version
python3 -m pip install --upgrade pip
python3 -m pip install wheel # needed for other packages
python3 -m pip install -r requirements.txt

sudo nano /etc/django_config.json
# Copy contents of file from local machine. Make sure debug is set to false and the server ip is added to ALLOWED_HOSTS


# apply migrations to database and start server for the first time
python3 manage.py migrate # Apply all the migration code to the database
python3 manage.py runserver 0.0.0.0:8000
# Do some testing on port 8000 to verify things looks okay (Smoke QA)
# You can test from a browser with <ip_address>:8000

### Create a Snapshot!


## Apache stuff
sudo apt-get install apache2 -y
sudo apt-get install libapache2-mod-wsgi-py3 -y
sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/django_project.conf #Copy the default conf as a boilerplate
# copy info from django_project.conf to /etc/apache2/sites-available/django_project.conf (add to the end before <VirtualHost>)
sudo nano /etc/apache2/sites-available/django_project.conf

cd /etc/apache2
sudo apache2ctl configtest #Check config file to make sure it's formatted correctly..should see 'Syntax OK'

sudo a2ensite django_project # enable site
sudo a2dissite 000-default.conf #disable default site


sudo chown :www-data ~/blogthedata/django_project/db.sqlite3
sudo chmod 664 ~/blogthedata/django_project/db.sqlite3

sudo chown :www-data ~/blogthedata/django_project/
sudo chmod 775 ~/blogthedata/django_project/

sudo chown -R :www-data ~/blogthedata/django_project/media/
sudo chmod -R 775 ~/blogthedata/django_project/media
sudo chmod -R 775 /user # This seems super bad, but I was getting permissions denied until I did this
sudo service apache2 restart
sudo service apache2 status # Make sure it is running
sudo tail -f /var/log/apache2/error.log # Check error logs

sudo ufw allow http/tcp
sudo service apache2 restart
# Do some more testing on port 80. If all looks good, remove incomming on port 8000
sudo ufw delete allow 8000


# Create admin user for django
python3 manage.py createsuperuser

# Add this code to 
config.extraPlugins = 'scayt';

/home/jsolly/blogthedata/django_project/static/ckeditor/ckeditor/config.js

### Create another snapshot!

# Buy domain 
# Follow linode doc on configuring reverse DNS
# Make sure to add an AAA record for the domain with www and without
# Use Certbot (let's encrypt to enable https)


# important paths
become root user -> sudo -i

sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log
sudo nano /etc/django_config.json 
sudo nano -c /etc/apache2/sites-available/django_project.conf

