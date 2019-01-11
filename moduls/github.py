import http.client

# Settings
# https://github.com/settings/developers
# Token:
# afc732614d157af0773ebd2f851fd49cd7b11c4c

token = 'afc732614d157af0773ebd2f851fd49cd7b11c4c'
userAgent = 'qVista'

conn = http.client.HTTPSConnection("api.github.com")
headers = { 'Authorization': 'token ' + token,
            'User-Agent'   : userAgent }

conn.request('GET', '/user', headers=headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8")) 

f = open('C:/Users/cpret/Dropbox/GIT/qVista/codi/moduls/github.json', 'w')
f.write(data.decode("utf-8"))
f.close()

conn.request('GET', '/repos/JCAIMI/Qvista/issues?assignee=CPCIMI&label=bug', headers=headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8")) 

f = open('C:/Users/cpret/Dropbox/GIT/qVista/codi/moduls/github_bugs.json', 'w')
f.write(data.decode("utf-8"))
f.close()


conn.close()
