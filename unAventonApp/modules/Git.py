import subprocess
import os
import re


class runCommand:

    def execute(self, *command):
        command = list(command)
        return subprocess.run(command, stdout=subprocess.PIPE)


class Git(runCommand):
    def __init__(self, path):
        os.chdir(path)

    def git(self, *args):
        return self.execute('git', *args).stdout.decode()

    def branch(self, name):
        return self.execute('git', 'branch', name)

    def getActuallBranch(self):
        stdout = self.execute('git', 'branch').stdout.decode()
        rBranch = re.compile(r'\*.*')
        branch = rBranch.findall(stdout)[0]
        return branch.replace('*', '')

    def checkout(self, name):
        return self.execute('git', 'checkout', name)

    def update(self):
        return self.execute('git', 'update')

    def fetch(self):
        return self.execute('git', 'fetch')

    def status(self):
        return self.execute('git', 'status')

    def resetHard(self, branch):
        return self.execute('git', 'reset', '--hard', 'origin/' + branch)

    def pull(self, origin='master'):
        return self.execute('git', 'pull', 'origin', origin)

