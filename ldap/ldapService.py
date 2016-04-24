"""
This file is part of Scoreg Ldap Sync.

Copyright (c) 2015, Vinzenz Stadtmueller
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, SUBTREE
import logging, unicodedata, string, codecs, base64
from ldap import ldaputil

conn = None
config = {}


def connect(conf):
    global conn
    global config
    server = Server(conf.get('Server', '127.0.0.1'),
                    port=conf.getint('Port', 389),
                    use_ssl=conf.getboolean(conf['SSL'], False),
                    get_info=ALL)
    conn = Connection(server,
                      conf.get('User', 'admin'),
                      conf.get('Password', 'admin'),
                      auto_bind=True)
    config = conf
    logging.info(conn.result)


def create_database(members):
    for member in members:
        adduser(member)


def create_group(groupname):
    conn.add('cn= ' + groupname + ',' + config['GroupDN'], 'groupofnames',
             {'member': config.get('user', '')})
    logging.info(conn.result)


def adduser(member):
    if member_exist(__get_cn(member)):
        conn.modify('cn= ' + __get_cn(member) + ',' + config['UserDN'],
                    {'givenName': (MODIFY_REPLACE, [member.get('firstname', '')]),
                     'sn': (MODIFY_REPLACE, [__remove_accents(member.get('lastname', ''))]),
                     'mail': (MODIFY_REPLACE, [member.get('emailPrimary', '')]),
                     'st': (MODIFY_REPLACE, [member.get('country', '')]),
                     'l': (MODIFY_REPLACE, [member.get('city')]),
                     'street': (MODIFY_REPLACE, [member.get('street', '')]),
                     'postalCode': (MODIFY_REPLACE, [member.get('postcode', '')])})

    else:
        conn.add('cn= ' + __get_cn(member) + ',' + config['UserDN'], 'inetorgperson',
                 {'givenName': member.get('firstname', ''),
                  'sn': __remove_accents(member.get('lastname', '')),
                  'mail': member.get('emailPrimary', ''),
                  'description': member.get('scoutId', ''),
                  'uid': __get_username(member),
                  'st': member.get('country', ''),
                  'l': member.get('city'),
                  'street': member.get('street', ''),
                  'postalCode': member.get('postcode', '')})
    if conn.result['result'] > 0:
        logging.error(conn.result)
        logging.error(member)
    else:
        logging.info(conn.result)

    if member.get('emailSecondary') is not None:
        conn.modify('cn= ' + __get_cn(member) + ',' + config['UserDN'],
                    {
                        'mail': (MODIFY_ADD, [member.get('emailSecondary', ''), ]),
                    })
        if conn.result['result'] > 0:
            logging.error(conn.result)
            logging.error(member)
        else:
            logging.info(conn.result)


def adduser_group(cn, groupname):
    conn.modify('cn= ' + groupname + ',' + config['GroupDN'],
                {'member': (MODIFY_ADD, [cn])})
    logging.info(conn.result)


def removeuser_group(cn, groupname):
    conn.modify('cn= ' + groupname + ',' + config['GroupDN'],
                {'member': (MODIFY_DELETE, [cn])})
    logging.info(conn.result)


def update_database(members):
    for member in members:
        adduser(member)


def update_password(cn, newpw):
    conn.modify('cn= ' + cn + ',' + config['UserDN'],
                {'userPassword': (MODIFY_REPLACE, ldaputil.make_secret(newpw))})
    logging.info(conn.result)


def find_member(cn):
    member = {}
    conn.search(search_base=config['UserDN'],
                search_filter='(&(objectClass=inetOrgPerson)(cn=' + cn + '))',
                search_scope=SUBTREE,
                attributes=['cn', 'givenName', 'sn', 'mail', 'uid', 'st', 'l',
                            'street', 'postalCode'],
                paged_size=5)
    if conn.result['description'] == 'success':
        memldap = conn.response[0]['attributes']
        member['firstname'] = memldap.get('givenName')
        member['lastname'] = memldap.get('sn')
        member['emailPrimary'] = memldap.get('mail')
        member['scoutId'] = cn
        member['country'] = memldap.get('st')
        member['city'] = memldap.get('l')
        member['street'] = memldap.get('street')
        member['postcode'] = memldap.get('postalcode')
        return member
    return None


def member_exist(cn):
    conn.search(search_base=config['UserDN'],
                search_filter='(&(objectClass=inetOrgPerson)(cn=' + cn + '))',
                search_scope=SUBTREE,
                attributes=['cn'],
                paged_size=5)
    if len(conn.response) > 0:
        return True
    return False


def uid_exist(uid):
    conn.search(search_base=config['UserDN'],
                search_filter='(&(objectClass=inetOrgPerson)(uid=' + uid + '))',
                search_scope=SUBTREE,
                attributes=['cn'],
                paged_size=5)
    if len(conn.response) > 0:
        return True
    return False


def unbind():
    conn.unbind()
    logging.info('Ldap Unbind')


# region Private Functions
def __get_username(member):
    return __generate_username(member.get('firstname', ''), member.get('lastname', ''))


def __get_cn(member):
    return __remove_accents("{0}{1}".format(
        member.get('firstname', '')[0],
        member.get('lastname', ''))).lower() + "-" + member.get('scoutId', '');


def __generate_username(first_name, last_name):
    val = __remove_accents("{0}{1}".format(first_name[0], last_name).lower())
    x = 1
    while True:
        if x == 1 and not uid_exist(val):
            return val
        else:
            new_val = "{0}{1}".format(val, x)
            if uid_exist(val):
                return new_val
        x += 1
        if x > 1000000:
            raise Exception("Name is super popular!")


def __remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters)
# endregion
