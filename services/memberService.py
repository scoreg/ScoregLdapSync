import requests
import logging

headers = {'Accept': 'application/json'}
resturl = ''
username = ''
password = ''
authid = ''
webid = ''


def init(conf):
    global resturl
    global username
    global password
    global authid
    global webid
    resturl = conf.get('RESTUrl')
    username = conf.get('User')
    password = conf.get('Password')
    authid = conf.get('OrgAuthId')
    webid = conf.get('WebserviceId')


def get_all_scoutids(org):
    url = '{0}/member/findScoutIdsForOrganization/{1}/{2}/{3}/{4}/{5}'.format(resturl,username,password,authid,webid,org)
    r = requests.get(url,headers=headers)
    json = r.json()
    list = json['ScoutIdList']
    return list['list']


def get_all_scouts(org):
    scoutIds = get_all_scoutids(org)
    members = []
    for id in scoutIds:
        member = get_scout(id)
        if member is not None:
            members.append(member)
    return members


def get_scout(scoutId):
    url = '{0}/member/findMemberByScoutId/{1}/{2}/{3}/{4}/{5}'.format(resturl, username, password, authid, webid, scoutId)
    r = requests.get(url,headers=headers)
    json = r.json()
    if 'MEMBER_FULL' == json['Member']['scoutState']:
        return json['Member']
    return None


def get_scout_complete(scoutId):
    url = '{0}/member/findMemberCompleteByScoutId/{1}/{2}/{3}/{4}/{5}'.format(resturl,username,password,authid,webid,scoutId)
    r = requests.get(url,headers=headers)
    json = r.json()
    if 'MEMBER_FULL' == json['MemberComplete']['scoutState']:
        return json['MemberComplete']
    return None
