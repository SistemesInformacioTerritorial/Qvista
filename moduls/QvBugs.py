import requests
from requests.auth import HTTPBasicAuth

class QvGithub:
    
    __ID = 'qVistaHost'

    def __init__(self):
        self.conn = 'https://api.github.com'
        self.calc = lambda s, n: s[-(n+1):] + s[0].upper() + s[1:n*2]+ str((n*14-1)*n)
        self.headGet = {
            'accept': "application/json",
            'time-zone': "Europe/Madrid",
            'user-agent': "qVista"
        }
        self.headPost = {
            'accept': "application/json",
            'content-type': "application/json"
        }
        self.repo = 'SistemesInformacioTerritorial/QVista'
        self.auth = HTTPBasicAuth(QvGithub.__ID, self.calc(QvGithub.__ID, 3))
        self.timeout = 2
        self.error = ''
    
    def getBug(self, title):
        try:
            url = self.conn + '/search/issues?q=repo:' + self.repo + '+state:open+label:bug+' + title + '+in:title'
            response = requests.get(url, headers=self.headGet, auth=self.auth, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                num = data['total_count']
                self.error = ''
                return num
            else:
                self.error = response.text
                return -1
        except Exception as err:
            self.error = str(err)
            return -1
    
    def postIssue(self, title, body, assignee, label):
        try:
            url = self.conn + '/repos/' + self.repo + '/issues'
            data = {
                "title": title,
                "body": body,
                "assignees": [
                    assignee
                ],
                "labels": [
                    label
                ]
            }
            response = requests.post(url, json=data, headers=self.headPost, auth=self.auth, timeout=self.timeout)
            if response.status_code == 201:
                self.error = ''
                return True
            else:
                self.error = response.text
                return False
        except Exception as err:
            self.error = str(err)
            return False

    def postBug(self, title, body, assignee):
        return self.postIssue(title, body, assignee, "bug")

    def postUser(self, title, body):
        return self.postIssue(title, body, "JCAIMI", "enhancement")

    def getCommitter(self, path):
        try:
            url = self.conn + '/repos/' + self.repo + '/commits?path=' + path
            response = requests.get(url, headers=self.headGet, auth=self.auth, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                item = data[0]
                commit = item['commit']
                author = commit['author']
                committer = commit['committer']
                name = committer['name']
                self.error = ''
                return name
            else:
                self.error = response.text
                return None
        except Exception as err:
            self.error = str(err)
            return None

if __name__ == "__main__":

    gh = QvGithub()

    num = gh.getBug('Bug desde app qVista')
    print('Bug:', num)

    com = gh.getCommitter('moduls/QvLlegenda.py')
    print('Committer:', com)

    # ok = gh.postBug('Bug desde app qVista', 'Descripción del error', 'CPCIMI')

    # ok = gh.postUser('Post de usuario', 'Prueba de sugerencia / petición')



