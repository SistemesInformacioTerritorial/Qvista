import requests
import json

# USUARI = 'qVistaHost'
# PASSWORD = 'HostQVista123'

_TOKEN = '830e8b32793cbc2a16f045549cea95aa25e244e4' # qVistaHost

class QvGithub:

    def __init__(self):
        self.conn = 'https://api.github.com'
        self.headGet = {
            'authorization': "token " + _TOKEN,
            'accept': "application/json",
            'time-zone': "Europe/Madrid",
            'user-agent': "qVista"
        }
        self.headPost = {
            'authorization': "token " + _TOKEN,
            'accept': "application/json",
            'content-type': "application/json"
        }
        self.repo = 'SistemesInformacioTerritorial/QVista'
    
    def getBug(self, title):
        try:
            url = self.conn + '/search/issues?q=repo:' + self.repo + '+state:open+label:bug+' + title + '+in:title'
            response = requests.request('GET', url, headers=self.headGet)
            if response.status_code == 200:
                data = json.loads(response.text)
                num = data['total_count']
                return num
            else:
                return -1
        except:
            return -1
    
    def postBug(self, title, body, user):
        try:
            url = self.conn + '/repos/' + self.repo + '/issues'
            data = {
                "title": title,
                "body": body,
                "assignees": [
                    user
                ],
                "labels": [
                    "bug"
                ]
            }
            response = requests.request('POST', url, json=data, headers=self.headPost)
            if response.status_code == 201:
                return True
            else:
                return False
        except:
            return False

    def getUser(self, path):
        try:
            url = self.conn + '/repos/' + self.repo + '/commits?path=' + path
            response = requests.request('GET', url, headers=self.headGet)
            if response.status_code == 200:
                data = json.loads(response.text)
                item = data[0]
                commit = item['commit']
                author = commit['author']
                committer = commit['committer']
                return committer['name']
            else:
                return None
        except:
            return None

if __name__ == "__main__":

    gh = QvGithub()

    num = gh.getBug('Prueba bug')
    print('Bug:', num)

    user = gh.getUser('moduls/QvLlegenda.py')
    print('Usr:', user)

    ok = gh.postBug('Bug desde app qVista', 'Descripción del error', 'CPCIMI')



