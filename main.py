#!/usr/bin/python
from services import memberService
from ldap import ldapService, ldaputil
from config import config
from operator import attrgetter
import logging


def main():
    logging.basicConfig(handlers=[logging.FileHandler('log/ldap.log', 'w', 'utf-8')],
                        format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.INFO)

    conf = config.read_conf('scoregLdapSync.ini')
    ldapService.connect(conf['ldap'])
    memberService.init(conf['Scoreg'])

    scoutIds = memberService.get_all_scoutids(conf['Scoreg']['OrgId'])

    #sorted(members,key=attrgetter('scoutId'))

    if conf['Default'].getboolean('createmode'):
        for id in scoutIds:
            member = memberService.get_scout_complete(id)
            if member is not None:
                ldapService.adduser(member)
    else:
        for id in scoutIds:
            member = memberService.get_scout_complete(id)
            if member is not None:
                ldapService.adduser(member)

    ldapService.unbind()

if __name__ == '__main__':
    main()
