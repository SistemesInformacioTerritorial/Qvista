import requests

# USUARI = 'qVistaHost'
# PASSWORD = 'HostQVista123'

_TOKEN = '7c0e7237075add68733dce460ba1d8d72f5f54ab' # qVistaHost

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
        self.timeout = 2
    
    def getBug(self, title):
        try:
            url = self.conn + '/search/issues?q=repo:' + self.repo + '+state:open+label:bug+' + title + '+in:title'
            response = requests.get(url, headers=self.headGet, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                num = data['total_count']
                return num
            else:
                return -1
        except:
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
                return True
            else:
                return False
        except:
            return False

    def postBug(self, title, body, assignee):
        self.postIssue(title, body, assignee, "bug")

    def postUser(self, title, body):
        self.postIssue(title, body, "JCAIMI", "enhancement")

    def getCommitter(self, path):
        # try:
            url = self.conn + '/repos/' + self.repo + '/commits?path=' + path
            response = requests.get(url, headers=self.headGet, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                item = data[0]
                commit = item['commit']
                author = commit['author']
                committer = commit['committer']
                return committer['name']
            else:
                return None
        # except:
        #     return None

if __name__ == "__main__":

    gh = QvGithub()

    num = gh.getBug('Bug desde app qVista')
    print('Bug:', num)

    com = gh.getCommitter('moduls/QvLlegenda.py')
    print('Committer:', com)

    ok = gh.postUser('Post de usuario', 'Prueba de sugerencia / petición')

    ok = gh.postBug('Bug desde app qVista', 'Descripción del error', 'CPCIMI')



