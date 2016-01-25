from services import memberService
from ldap import ldapService
from config import config
import logging

conf = config.create_conf('scoregLdapSync.ini')
ldapService.connect(conf['ldap'])
memberService.init(conf['Scoreg'])
logging.basicConfig(filename='ldap.log', level=logging.INFO)

list = memberService.get_all_scoutids(31)
members = memberService.get_all_scouts(list)

if conf['Default'].getboolean('createmode'):
    ldapService.create_database(members)
else:
    ldapService.update_database(members)


ldapService.unbind()