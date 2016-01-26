#!/usr/bin/python
from services import memberService
from ldap import ldapService, ldaputil
from config import config
from operator import itemgetter, attrgetter
from passlib.hash import ldap_sha1 as lls
import logging

logging.basicConfig(filename='ldap.log', level=logging.INFO)
conf = config.read_conf('scoregLdapSync.ini')
ldapService.connect(conf['ldap'])
memberService.init(conf['Scoreg'])

print(lls.encrypt("password"))


list = memberService.get_all_scoutids(31)
members = memberService.get_all_scouts(list)

sorted(members,key=attrgetter('scoutId'))

if conf['Default'].getboolean('createmode'):
    ldapService.create_database(members)
else:
    ldapService.update_database(members)


ldapService.unbind()