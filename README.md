# ejabberd MySQL authentication module

This is a module for ejabberd to to authenticate against a MySQL database. The intent was to use the same database for postfix and ejabberd, while using [Postfix Admin](http://postfixadmin.sourceforge.net/) as a simple interface for account administration. Originally I was using the [authentication module by Mattias Hemmingsson](http://lifeandshell.com/ejabber-users-from-postfixadmin-pythonmysqlmd5crypt/), but this was quite hacky and not able to fetch passwords for users on different domain names. Also it broke on specific passwords and kept the database connection open.

Therefore this implementation fixes those issues and implements an external config file for easy configuration. Also the logging was rewritten in order to have a better filtering of debug messages if needed.

## Installation

1. copy `auth_mysql.py` anywhere on your ejabberd host (i.e. `/etc/ejabberd/auth_mysql.py`).
2. set permissions for the script, so that the ejabberd user can execute it:
    ```
    chown ejabberd:ejabberd /etc/ejabberd/auth_mysql.py
    chmod 775 /etc/ejabberd/auth_mysql.py
    ```
3. create a config file (use auth_mysql.example.py as guidance).
4. configure `ejabberd.yml` to use the script as external authentication method:
    ```
    auth_method: external
    extauth_program: "/etc/ejabberd/auth_mysql.py"
    ```
5. Restart ejabberd

## Hints

- The configuration files path is statically set to `/etc/ejabberd/auth_mysql.yml`.
- The log files path is statically set to `/var/log/ejabberd/sso-auth.log`.

If you need or want to change these paths, edit the script.

## License

GPL-2