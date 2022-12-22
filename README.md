# Depreciation notice
As of the 22nd of December 2022, this project is no longer actively maintained.

## Backend

This is the P&O3-Backend written in Python, with the Django REST framework.

To get started, you have to have a working installation of Python (preferably 3.10).

## MySQL

To install MySQL system-wide, run

```bash
sudo apt-get install mysql-server
```

You first have to set the root password for MySQL:

```bash
sudo mysql
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password by '<Your_password>';
mysql> exit
```

Alter `<Your_password>` with the custom chosen password. It's important to remember this password as it's used to log in to MySQL.

Then run `sudo mysql_secure_installation`. You have to enter the password that you created on the previous step. After that you have to answer a series of questions:

```bash
Change the password for root ? ((Press y|Y for Yes, any other key for No) : n
Remove anonymous users? (Press y|Y for Yes, any other key for No) : n
Disallow root login remotely? (Press y|Y for Yes, any other key for No) : y
Remove test database and access to it? (Press y|Y for Yes, any other key for No) : n
Reload privilege tables now? (Press y|Y for Yes, any other key for No) : y
```

Now, MySQl should be set up correctly. To create the database, enter the MySQL command console:

```bash
sudo mysql -u root -p
```

Create the `po3_database` with the following command:

```bash
mysql>create database po3_database;
```

To make sure that the database is created correctly, enter `show databases`. Normally you should see the `po3_database` in the list. Type `exit` to exit the console.

Then install the `mysql_config`-command which is needed for the MySQL Python client:

```bash
sudo apt-get install libmysqlclient-dev
```

The last step is ot install the MySQL client for Python:

```bash
pip install mysqlclient
```

## Django

Django is a Python framework that's used to build full stack web application, but with the REST framework it can also be used for creating APIs.
To install Django and the Django REST framework run

```bash
pip install Django
pip install djangorestframework
```

Now the final in the root of this repository create a file `.env` with the same elements as the `.env.sample`. Enter your database password of MySQL (see previous paragraph) with `DATABASE_PASSWORD`.

Before starting the server, run

```bash
python manage.py migrate
```

Then start up the server with

```bash
python manage.py runserver
```

To check if everything is set up correctly, go to http://127.0.0.1:8000/. Normally, you shouldn't see any errors.
