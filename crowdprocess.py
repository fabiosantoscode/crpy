import requests
import json
from base64 import b64encode
import threading

baseAPIUrl = "https://api.crowdprocess.com/jobs/"


class CrowdProcess(object):

    """docstring for CrowdProcess"""

    def __init__(self, username=None, password=None, token=None):
        super(CrowdProcess, self).__init__()
        if (username is None or password is None) and token is None:
            raise Exception("Needs either username and password or token")

        if (username is not None and password is not None):
            c = b64encode(('%s:%s' % (username, password))
                          .encode('latin1')).strip().decode('latin1')
            self.headers = {
                "Authorization": "Basic " + c
            }

        if (token is not None):
            self.headers = {"Authorization": "Token " + token}

    def list_jobs(self):
        res = requests.get(baseAPIUrl, headers=self.headers)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            res.raise_for_status()

    def Job(self, id=None):
        return Job(self, id)


class Job(object):

    """docstring for Job"""

    def __init__(self, CrowdProcess, id=None):
        super(Job, self).__init__()
        self.headers = CrowdProcess.headers
        self.id = id

    def show(self):
        if self.id is None or self.id is "":
            raise Exception("Need a self.id")

        res = requests.get(baseAPIUrl + self.id,
                           headers=self.headers)
        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        return res.json()

    def create(self, program, bid=1.0, group=None):
        if self.id is not None:
            raise Exception("Job " + self.id + " was already created")

        payload = {
            "program": program,
            "bid": bid,
            "group": group
        }

        res = requests.post(baseAPIUrl,
                            data=json.dumps(payload),
                            headers=self.headers)

        if res.status_code != requests.codes.created:
            res.raise_for_status()

        self.id = res.json()["id"]

    def delete(self):
        if self.id is None:
            raise Exception("This job was not created (self.id not present)")

        res = requests.delete(baseAPIUrl + "/" + self.id,
                              headers=self.headers)
        if res.status_code != requests.codes.no_content:
            res.raise_for_status()

    def create_tasks(self, iterable):
        def genwrapper():
            for n in iterable:
                yield json.dumps(n).encode() + b"\n"

        res = requests.post(baseAPIUrl + self.id + "/tasks",
                            data=genwrapper(),
                            headers=self.headers)

        if res.status_code != requests.codes.created:
            res.raise_for_status()

    def get_results(self):
        res = requests.get(baseAPIUrl + self.id + "/results",
                           stream=True,
                           headers=self.headers)
        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            for line in res.iter_lines():
                if line:
                    yield json.loads(line.decode())

        return gen(res)

    def get_results_stream(self):
        res = requests.get(baseAPIUrl + self.id + "/results?stream",
                           stream=True,
                           headers=self.headers)
        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            while True:
                line = res.raw.readline()
                yield json.loads(line.decode())
                if line is None:
                    break

        return gen(res)

    def get_errors(self):
        res = requests.get(baseAPIUrl + self.id + "/errors",
                           stream=True,
                           headers=self.headers)
        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            for line in res.iter_lines():
                if line:
                    yield json.loads(line.decode())

        return gen(res)

    def get_errors_stream(self):
        res = requests.get(baseAPIUrl + self.id + "/errors?stream",
                           stream=True,
                           headers=self.headers)
        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            for line in res.iter_lines():
                if line:
                    yield json.loads(line.decode())

        return gen(res)

    def io(self, iterable):
        expected_results = 0
        def genwrapper():
            for n in iterable:
                yield n
                expected_results += 1

        t = threading.Thread(target=self.create_tasks, args=(genwrapper()))
        t.start()

        def results_gen():
            for result in self.get_results_stream():
                expected_results = expected_results - 1
                if expected_results is 0:
                    break

        return results_gen()