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
$ python3 -m pip install wheel
$ python3 -m pip install -r ~/blogthedata/django_project/requirements/requirements.txt
$ touch ~/blogthedata/.env
$ nano ~/blogthedata/.env
# copy over parameters from blogthedata/sample.env and set them as needed
$ python3 ~/blogthedata/django_project/manage.py runserver 0.0.0.0:8000
# in a browser navigate to <ip_address>:8000
# You should see an error in the console that the server cannot be accesed via HTTP (but this means we were able to connect to it)
```

### Install dependencies
```
$ 
