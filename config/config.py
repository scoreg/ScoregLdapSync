import configparser


def create_conf(file):
    config = configparser.ConfigParser()
    config['Default'] = {}
    default = config['Default']
    default['CreateMode'] = 'False'
    config['ldap'] = {}
    ldap = config['ldap']
    ldap['Server'] = '127.0.0.1'
    ldap['Port'] = '389'
    ldap['SSL'] = 'False'
    ldap['User'] = 'cn=admin,dc=example,dc=org'
    ldap['Password'] = 'password'
    ldap['UserDN'] = 'ou=people,dc=example,dc=org'
    ldap['GroupDN'] = 'ou=groups,dc=example,dc=org'
    config['Scoreg'] = {}
    scoreg = config['Scoreg']
    scoreg['RESTUrl'] = 'https://scoreg.at/ScoregWebServer/services/rest'
    scoreg['WebserviceId'] = 'WEB-XXXXXXX'
    scoreg['User'] = 'user'
    scoreg['Password'] = 'password'
    scoreg['OrgAuthId'] = '0'
    scoreg['OrgId'] = 0
    with open(file, 'w') as configfile:
        config.write(configfile)


def read_conf(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config
