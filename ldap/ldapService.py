from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, SUBTREE
import logging
import unicodedata, string
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
        if not member_exist('cn= ' + get_username(member) + ',' + config['UserDN']):
            conn.add('cn= ' + get_username(member) + ',' + config['UserDN'], 'inetorgperson',
                 {'givenName': member.get('firstname', ''),
                  'sn': remove_accents(member.get('lastname', '')),
                  'mail': member.get('emailPrimary', ''),
                  'uid': member.get('scoutId', ''),
                  'st': member.get('country', ''),
                  'l': member.get('city'),
                  'street': member.get('street', ''),
                  'postalCode': member.get('postcode', '')})
            logging.info(conn.result)


def create_group(groupname):
    conn.add('cn= ' + groupname + ',' + config['GroupDN'], 'groupofnames',
             {'member': config.get('user', '')})
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
        conn.modify('cn= ' + get_username(member) + ',' + config['UserDN'],
                    {'givenName': (MODIFY_REPLACE, [member.get('firstname', '')]),
                     'sn': (MODIFY_REPLACE, [remove_accents(member.get('lastname', ''))]),
                     'mail': (MODIFY_REPLACE, [member.get('emailPrimary', '')]),
                     'uid': (MODIFY_REPLACE, [member.get('scoutId', '')]),
                     'st': (MODIFY_REPLACE, [member.get('country', '')]),
                     'l': (MODIFY_REPLACE, [member.get('city')]),
                     'street': (MODIFY_REPLACE, [member.get('street', '')]),
                     'postalCode': (MODIFY_REPLACE, [member.get('postcode', '')])})
        logging.info(conn.result)


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
        member['scoutId'] = memldap.get('uid')
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


def unbind():
    conn.unbind()
    logging.info('Ldap Unbind')


# Private functions


def get_username(member):
    return remove_accents(member.get('firstname', '').lower()[0] + member.get('lastname', '')).lower()


def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters)
