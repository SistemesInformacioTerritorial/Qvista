import requests

# USUARI = 'qVistaHost'
# PASSWORD = '123-Host-QVista-123'

# https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/

class QvGithub:
    
    __TOKEN = '7c0e7237075add68733dce460ba1d8d72f5f54ab' # qVistaHost

    def __init__(self):
        self.conn = 'https://api.github.com'
        self.headGet = {
            'authorization': "token " + QvGithub.__TOKEN,
            'accept': "application/json",
            'time-zone': "Europe/Madrid",
            'user-agent': "qVista"
        }
        self.headPost = {
            'authorization': "token " + QvGithub.__TOKEN,
            'accept': "application/json",
            'content-type': "application/json"
        }
        self.repo = 'SistemesInformacioTerritorial/QVista'
        self.timeout = 2
        self.error = ''
    
    def getBug(self, title):
        try:
            url = self.conn + '/search/issues?q=repo:' + self.repo + '+state:open+label:bug+' + title + '+in:title'
            response = requests.get(url, headers=self.headGet, timeout=self.timeout)
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
            response = requests.post(url, json=data, headers=self.headPost, timeout=self.timeout)
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
        self.postIssue(title, body, assignee, "bug")

    def postUser(self, title, body):
        self.postIssue(title, body, "JCAIMI", "enhancement")

    def getCommitter(self, path):
        try:
            url = self.conn + '/repos/' + self.repo + '/commits?path=' + path
            response = requests.get(url, headers=self.headGet, timeout=self.timeout)
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

    ok = gh.postBug('Bug desde app qVista', 'Descripción del error', 'CPCIMI')

    ok = gh.postUser('Post de usuario', 'Prueba de sugerencia / petición')



