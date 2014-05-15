import requests
import json
from base64 import b64encode
import threading
from time import time

baseAPIUrl = "https://api.crowdprocess.com/jobs/"


class CrowdProcess(object):

    def __init__(self, username=None, password=None, token=None):
        super(CrowdProcess, self).__init__()
        if (username is None or password is None) and token is None:
            raise Exception("Needs either username and password or token")

        if (username is not None and password is not None):
            c = b64encode(('%s:%s' % (username, password))
                          .encode('latin1')).strip().decode('latin1')
            self._headers = {
                "Authorization": "Basic " + c
            }

        if (token is not None):
            self._headers = {"Authorization": "Token " + token}

    def list_jobs(self):
        res = requests.get(baseAPIUrl, headers=self._headers)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            res.raise_for_status()

    def job(self, program=None, bid=1.0, group=None, id=None):
        return Job(self, program=program, bid=bid, group=group, id=id)


class Job(object):

    def __init__(self, CrowdProcess, program=None,
                 bid=1.0, group=None, id=None):
        super(Job, self).__init__()
        self._headers = CrowdProcess._headers
        self._batch_out = {}

        if id is not None:
            self.id = id
        elif program is not None:
            self._create(program, bid, group)

    def _create(self, program, bid=1.0, group=None):
        payload = {
            "program": program,
            "bid": bid,
            "group": group
        }

        res = requests.post(baseAPIUrl,
                            data=json.dumps(payload),
                            headers=self._headers)

        if res.status_code != requests.codes.created:
            res.raise_for_status()

        self.id = res.json()["id"]

    def show(self):
        res = requests.get(baseAPIUrl + self.id,
                           headers=self._headers)

        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        return res.json()

    def delete(self):
        res = requests.delete(baseAPIUrl + "/" + self.id,
                              headers=self._headers)

        if res.status_code != requests.codes.no_content:
            res.raise_for_status()

    def create_tasks(self, iterable):
        def genwrapper():
            for n in iterable:
                yield json.dumps(n).encode() + b"\n"

        res = requests.post(baseAPIUrl + self.id + "/tasks",
                            data=genwrapper(),
                            headers=self._headers)

        if res.status_code != requests.codes.created:
            res.raise_for_status()

    def get_results(self):
        res = requests.get(baseAPIUrl + self.id + "/results",
                           stream=True,
                           headers=self._headers)

        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            while True:
                line = res.raw.readline()
                if len(line) is 0:
                    break
                yield json.loads(line.decode())

        return gen(res)

    def get_results_stream(self):
        res = requests.get(baseAPIUrl + self.id + "/results?stream",
                           stream=True,
                           headers=self._headers)

        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            while True:
                line = res.raw.readline()
                if len(line) is 0:
                    break
                yield json.loads(line.decode())

        return gen(res)

    def get_errors(self):
        res = requests.get(baseAPIUrl + self.id + "/errors",
                           stream=True,
                           headers=self._headers)

        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            while True:
                line = res.raw.readline()
                if len(line) is 0:
                    break
                yield json.loads(line.decode())

        return gen(res)

    def get_errors_stream(self):
        res = requests.get(baseAPIUrl + self.id + "/errors?stream",
                           stream=True,
                           headers=self._headers)

        if res.status_code != requests.codes.ok:
            res.raise_for_status()

        def gen(iter):
            while True:
                line = res.raw.readline()
                if len(line) is 0:
                    break
                yield json.loads(line.decode())

        return gen(res)

    def __call__(self, iterable):
        batch = str(time())
        self._batch_out[batch] = 0

        def genwrapper():
            for n in iterable:
                yield n
                self._batch_out[batch] += 1

        t = threading.Thread(target=self.create_tasks, args=(genwrapper(),))

        results = self.get_results_stream()
        t.start()

        def results_gen():
            for result in results:
                yield result
                self._batch_out[batch] -= 1
                while self._batch_out[batch] == 0 and t.isAlive():
                    t.join(0.1)

                if self._batch_out[batch] == 0 and not t.isAlive():
                    break
            t.join()

        return results_gen()
