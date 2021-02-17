# Chef's Hat Card Game

Webserver for the Chef's Hat Card Game.

Visit [Chef's Hat Card Game original repository](https://github.com/pablovin/ChefsHatGYM) for more information.

| Dependencies | Version |
| ------------ | ------- |
| Python | [3.x](https://www.python.org/downloads/) |
| NodeJS (LTS) | [14.x](https://nodejs.org/en/download/) |
| npm | [6.x](https://www.npmjs.com/) |

----------

## Pre-requisites

## PostgresSQL

Install Postgressql and libpq-dev

```sh
sudo apt install postgresql postgresql-contrib
sudo apt install libpq-dev
```

create a database and user
```sh
sudo su - postgres psql
create database dbName;
create user userName with password 'password';
```

Adjust tsome settings to speedup the query process

```sh
ALTER ROLE userName SET client_encoding TO 'utf8';
ALTER ROLE userName SET default_transaction_isolation TO 'read committed';

```

Grant the user access to the database
```sh
grant all privileges on database dbName to userName;
```



### NodeJS

In order to install NodeJS from binary source run the following commands.

**Note**: npm is installed along with NodeJS.

From the project folder run the following command:

```sh
curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
```

Run the next commands to add PPA. Please note that is a **system wide** installation:

```sh
bash nodesource_setup.sh
rm nodesource_setup.sh
```

Finally run this command to install NodeJS:

```sh
apt-get install -y nodejs
```

Now that NodeJS is installed you can install projects dependencies with the next command from `ChefsHat` folder run :

```sh
npm install
```

### Django

Install the requirements from the `requirements.txt` file with this command:

```python
pip3 install -r requirements.txt
```

If runing on a server, you might be able to run:
```python
sudo apt-get install libsm6 libxrender1 libfontconfig1
```

Configure the ChefsHat/ChefsHat/settings.py to allow your host. Change the following line:

```python
ALLOWED_HOSTS = ["hostAddress"]
```
Configure the ChefsHat/ChefsHat/settings.py to use the dataset:

```python
DATABASES = {
        'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': "dbName",

        'USER': "userName",

        'PASSWORD': "password",

        'HOST': 'localhost',

        'PORT': '',

    }

}
```

You can access yourhost/admin to check the dataset entires. You will need to create a superuser:

```python
python manage.py createsuperuser
```

Run the following command to setup database and create the models:

```python
python3 ChefsHat/manage.py migrate
python3 ChefsHat/manage.py makemigrations
```



## Assets

Project's frontend is based on **TypeScript** and **SCSS**. These assets must be compiled (into Javascript and CSS) in order to be interpreted from browsers.

Assets sources are placed into `ChefsHat/static/src`. 
Results of compilation tasks are targeted to the following folders:
* `ChefsHat/static/css` for Stylesheet;
* `ChefsHat/static/js` for Javascript;

**Warning**: modifying target assets will results in a data loss at next compilation task. Note that target assets aren't versioned.

Compilation tasks are defined into `ChefsHat/package.json` file. 

In order to add new files to compilation tasks alter `entry` array defined at the begin of `ChefsHat/webpack.config.js` file.

### Commands


All the following commands must be run from `ChefsHat` folder:

| Environments | Command | Task |
| ------------ | ------- | -----|
| Development | `npm run watch` | Watch assets for change and compile |
| Development | `npm run build:dev` | Compile assets not compressed |
| **Production** | `npm run build:prod` | Compile assets compressed |

## Run the game

From `ChefsHat` folder run the following command in order to start server:
   
```python
python3 manage.py runserver
```

The game will be at the following link: 

```http
http://127.0.0.1:8000/SingleGame
```

After playing, collect the dataset folder from:

```sh
ChefsHat/static
```

## Run on an Apache2 server

Install Apache

```python
sudo apt-get install apache2 libapache2-mod-wsgi-py3
```

Update Apache configuration

```python
sudo nano /etc/apache2/sites-available/000-default.conf
```

Configuration example
```python
<VirtualHost *:80>
	

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined


	Alias /static /projectRootFolder
    <Directory /projectRootFolder>
        Require all granted
    </Directory>

	WSGIProcessGroup %{GLOBAL}
	WSGIApplicationGroup %{GLOBAL}

    <Directory /projectRootFolder/ChefsHat>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess ChefsHat python-home=/virtualenvFolder/ python-path=/projectRootFolder/
    WSGIProcessGroup ChefsHat
    WSGIScriptAlias /   /projectRootFolder/ChefsHat/wsgi.py



</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

Update the permissions on the folders and files from the project root

```python
chmod 664 ChefsHat/db.sqlite3
sudo chown :www-data db.sqlite3

chmod -R 664 ChefsHat/static
sudo chown :www-data static

```

Update the ChefsHat/ChefsHat/settings.py and add the host dns on the "allowed hosts" vector.



Restart apache

```python
sudo service apache2 restart
```