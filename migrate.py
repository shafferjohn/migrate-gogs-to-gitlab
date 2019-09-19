import json
import requests
import os

# gogs api: https://github.com/gogs/docs-api
# gitlab api: https://docs.gitlab.com/ee/api/README.html

GOGS_URL = "https://gogs.example.com/api/v1/"
GOGS_ACCESS_TOKEN = "your_gogs_access_token"
GOGS_GIT_URL = "https://%s@gogs.example.com/%s/%s.git"

GITLAB_URL = "https://gitlab.example.com/api/v4/"
GITLAB_ACCESS_TOKEN = "your_gitlab_access_token"
GITLAB_GIT_URL = "https://oauth2:%s@gitlab.example.com/%s/%s.git"


def resolve(c, o):
    if type(o) in dict:
        c.__dict__ = o
    else:
        c.__dict__ = json.loads(o)


class Gogs:
    def __init__(self, url, access_token):
        self.url = url.strip("/")
        self.access_token = access_token
        self.headers = {"Authorization": "token %s" % self.access_token}

    def get(self, url):
        r = requests.get(self.url + url, headers=self.headers)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def getUsers(self):
        """
        [{
          "id": 1,
          "username": "unknwon",
          "full_name": "",
          "email": "fake@local",
          "avatar_url": "/avatars/1"
        }]
        """
        return self.get("/users/search?q=%&limit=100")["data"]

    def getRepos(self):
        """
        [{
            "id": 3,
            "owner": {
                "id": 12,
                "login": "Pomelo",
                "full_name": "\u9752\u67da\u5de5\u4f5c\u5ba4",
                "email": "",
                "avatar_url": "https://qingyou.njupt.edu.cn/git/avatars/12",
                "username": "Pomelo"
            },
            "name": "Graduate_BE",
            "full_name": "Pomelo/Graduate_BE",
            "description": "\u7814\u7a76\u751f\u7248\u5c0f\u7a0b\u5e8f\u540e\u7aef",
            "private": true,
            "fork": false,
            "parent": null,
            "empty": false,
            "mirror": false,
            "size": 24576,
            "html_url": "https://qingyou.njupt.edu.cn/git/Pomelo/Graduate_BE",
            "ssh_url": "ssh://gogs@qingyou.njupt.edu.cn:2222/Pomelo/Graduate_BE.git",
            "clone_url": "https://qingyou.njupt.edu.cn/git/Pomelo/Graduate_BE.git",
            "website": "",
            "stars_count": 3,
            "forks_count": 0,
            "watchers_count": 5,
            "open_issues_count": 0,
            "default_branch": "master",
            "created_at": "2017-11-07T18:06:24+08:00",
            "updated_at": "2017-11-07T20:43:11+08:00"
        }]
        """
        return self.get("/repos/search?q=%&limit=100")["data"]


class Gitlab:
    def __init__(self, url, access_token):
        self.url = url.strip("/")
        self.access_token = access_token
        self.headers = {"Authorization": "Bearer %s" % self.access_token}

    def get(self, url):
        r = requests.get(self.url + url, headers=self.headers)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def post(self, url, json_data):
        r = requests.post(self.url + url, headers=self.headers, json=json_data)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def createUser(self, gogs):
        user = {
            "email": gogs["email"],
            "username": gogs["username"],
            "name": gogs["username"],
            "reset_password": True
        }
        return self.post("/users", user)

    def createProject(self, gogs):
        self.headers.update({"Sudo": gogs["owner"]["username"]})
        project = {
            "name": gogs["name"],
            "visibility": "internal"
        }
        return self.post("/projects", project)

    def copyRepo(self, gogs):
        username = gogs["owner"]["username"]
        reponame = gogs["name"]
        fullname = gogs["full_name"]
        dirname = "tmp/%s" % fullname
        gogs_repo_git_url = GOGS_GIT_URL % (GOGS_ACCESS_TOKEN, username, reponame)
        gitlab_repo_git_url = GITLAB_GIT_URL % (GITLAB_ACCESS_TOKEN, username, reponame)
        commands = [
            "git clone --mirror %s %s" % (gogs_repo_git_url, dirname),
            "pushd %s" % dirname,
            "git remote set-url origin %s" % gitlab_repo_git_url,
            "git push --mirror",
            "popd"
        ]
        print(commands)
        command = " && ".join(commands)
        os.system(command)


if __name__ == '__main__':
    gogs = Gogs(GOGS_URL, GOGS_ACCESS_TOKEN)
    gitlab = Gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN)

    gogs_users = gogs.getUsers()
    for gogs_user in gogs_users:
        print(json.dumps(gogs_user, indent=4))
        print(gitlab.createUser(gogs_user))

    # 不迁移issue之类的东西的话，可以不创建project
    # git push --mirror的话，gitlab会自动创建
    gogs_repos = gogs.getRepos()
    for gogs_repo in gogs_repos:
        print(json.dumps(gogs_repo, indent=4))
        print(gitlab.createProject(gogs_repo))

    for gogs_repo in gogs_repos:
        gitlab.copyRepo(gogs_repo)
