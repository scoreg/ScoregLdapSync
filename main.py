#!/usr/bin/python
from services import memberService
from ldap import ldapService, ldaputil
from config import config
from operator import attrgetter
import logging

logging.basicConfig(filename='ldap.log', level=logging.INFO)
conf = config.read_conf('scoregLdapSync.ini')
ldapService.connect(conf['ldap'])
memberService.init(conf['Scoreg'])

members = memberService.get_all_scouts(conf['Scoreg']['OrgId'])

#sorted(members,key=attrgetter('scoutId'))

if conf['Default'].getboolean('createmode'):
    ldapService.create_database(members)
else:
    ldapService.update_database(members)


ldapService.unbind()