import subprocess
import os

GIT_BRANCH = 'stable'
DEBUG = True

class runCommand:

    def execute(self, *command):
        command = list(command)
        return subprocess.run(command, stdout=subprocess.PIPE)


class Git(runCommand):
    def __init__(self, path):
        os.chdir(path)

    def branch(self, name):
        return self.execute('git', 'branch', name)

    def checkout(self, name):
        return self.execute('git', 'checkout', name)

    def update(self):
        return self.execute('git', 'update')

    def fetch(self):
        return self.execute('git', 'fetch')

    def resetHard(self,branch):
        return self.execute('git', 'reset', '--hard', 'origin/'+branch )

    def pull(self, origin='master'):
        return self.execute('git', 'pull', 'origin', origin)


def logInfoExec(msg):
    if DEBUG:
        print("UPDATER INFO: about tu run: {0}  STDOUT = {1}".format(" ".join(msg.args), msg.stdout.decode()))

cmd = runCommand()
git = Git('src/')
logInfoExec(git.fetch())
logInfoExec(git.checkout(GIT_BRANCH))
x = git.pull(GIT_BRANCH)
if str(x.stdout.decode()).count('up-to-date'):
    exit(0)
logInfoExec(git.resetHard(GIT_BRANCH))
cmd.execute('killall', 'uwsgi')
os.chdir('src/')
cmd.execute('pip3', 'install', '-r','requirements.txt')
cmd.execute('python3', 'manage.py', 'makemigrations','--no-input')
cmd.execute('python3', 'manage.py', 'migrate','--no-input')
cmd.execute('python3', 'manage.py', 'collectstatic','--no-input')
#cmd.execute('./../server.sh', 'start')
exit(0)
