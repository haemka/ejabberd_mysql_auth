#!/usr/bin/python

import MySQLdb
import logging
import re
import sys
import yaml
from struct import pack, unpack
from passlib.hash import md5_crypt

configfile = '/etc/ejabberd/auth_mysql.yml'
logging.basicConfig(level=logging.INFO, filename='/var/log/ejabberd/sso-auth.log',
                    format='%(asctime)s [%(levelname)s] %(message)s')

try:
    with open(configfile, 'r') as cf:
        try:
            config = yaml.load(cf)
        except yaml.YAMLError:
            logging.error('Unable to load configuration data from file at {0!s}!'.format(configfile))
except IOError:
    logging.error('Unable to open configuration file at {0!s}!'.format(configfile))


def from_ejabberd():
    input_length = sys.stdin.read(2)

    (size,) = unpack('>h', input_length)

    d = re.match(r'^(?P<command>(auth|isuser|setpass)):(?P<username>\w+):(?P<domain>[\w.]+):(?P<password>.*)$',
                 sys.stdin.read(size))
    if d is None:
        logging.error('Received incorrect request format from ejabberd!')
        return False
    return d.groupdict()


def to_ejabberd(r):
    logging.debug('Writing token to stdout.')
    token = pack('>hh', 2, int(r))
    sys.stdout.write(token)
    sys.stdout.flush()


def get_data(username, server):
    try:
        logging.debug('Connecting to database.')
        database = MySQLdb.connect(config['db']['host'], config['db']['user'], config['db']['pass'],
                                   config['db']['name'])
        dbcur = database.cursor()
        dbcur.execute("SELECT {0!s},{1!s} FROM {2!s} WHERE {3!s}='{4!s}' AND {5!s}='{6!s}'".format(
            config['db']['fields']['username'], config['db']['fields']['password'], config['db']['table'],
            config['db']['fields']['localpart'], username, config['db']['fields']['domain'], server))
        d = dbcur.fetchone()
        dbcur.close()
        database.close()
    except MySQLdb.Error, e:
        logging.error('MySQL Error [{0!d}]: {1!s}'.format(e.args[0], e.args[1]))
        d = None
    return d

def auth(username, server, password):
    logging.info('auth request for {0!s}@{1!s}.'.format(username, server))
    d = get_data(username, server)
    if data is None:
        logging.info('Unknown user: {0!s}@{1!s}.'.format(username, server))
        return False
    if '{0!s}@{1!s}'.format(username, server) == d[0]:
        if md5_crypt.verify(password, d[1]):
            logging.info('correct password for {0!s}@{1!s}.'.format(username, server))
            return True
        else:
            logging.warning('Wrong password for {0!s}@{1!s}.'.format(username, server))
            return False
    else:
        logging.error('Database did not return the correct data. This should not happen!')
        return False


def isuser(username, server):
    logging.info('isuser request for {0!s}@{1!s}.'.format(username, server))
    d = get_data(username, server)
    if d is None:
        logging.warning('Wrong username: {0!s}@{1!s}.'.format(username, server))
        return False
    if '{0!s}@{1!s}'.format(username, server) == d[0]:
        logging.info('Correct username: {0!s}@{1!s}.'.format(username, server))
        return True
    return False


def setpass(username, server, password):
    # TODO: not implemented
    logging.info('setpass request for {0!s}@{1!s}.'.format(username, server))
    return False


while True:
    data = from_ejabberd()
    if not data:
        to_ejabberd(False)
    elif data['command'] == "auth":
        to_ejabberd(auth(data['username'], data['domain'], data['password']))
    elif data['command'] == "isuser":
        to_ejabberd(isuser(data['username'], data['domain']))
    elif data['command'] == "setpass":
        to_ejabberd(setpass(data['username'], data['domain'], data['password']))
