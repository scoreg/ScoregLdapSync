#!/usr/bin/python
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
from services import memberService
from ldap import ldapService, ldaputil
from config import config
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
