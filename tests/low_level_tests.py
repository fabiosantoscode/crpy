from crowdprocess import CrowdProcess
import unittest
from time import sleep
import threading
import json
import httpretty

crp = CrowdProcess('username', 'password')

N = 10
program_fixture = "function Run(d) { return d*2; }"
results_fixture = "\n".join([str(x*2) for x in range(N)])+"\n"
tasksSent = []
baseAPIUrl = "https://api.crowdprocess.com/jobs/"

class Tests(unittest.TestCase):

    @httpretty.activate
    def test_low_level(self):
        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id"
                      }),
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id/tasks",
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id",
                      status=200,
                      body=json.dumps({
                          "id": "job_id",
                          "total": 10,
                          "finished": 10,
                          "failed": 0
                      }),
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/results",
                      status=200,
                      body=results_fixture,
                      streaming=True,
                      content_type='application/json')

        job = crp.job(program_fixture)
        self.assertIsNotNone(job.id)

        tasks = range(N)
        job.create_tasks(tasks)

        while True:
            s = job.show()
            if s["total"] > 0 and s["total"] == s["finished"] + s["failed"]:
                break
            sleep(1)

        results_got = 0
        for result in job.get_results():
            self.assertTrue(result / 2 in tasks)
            results_got += 1

        self.assertEqual(results_got, N)

        job = crp.job(id=job.id)
        s = job.show()
        self.assertEqual(s["total"], N)
        self.assertEqual(s["finished"], N)
        self.assertEqual(s["failed"], 0)
        self.assertEqual(s["id"], job.id)

    @httpretty.activate
    def test_streams(self):
        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id"
                      }),
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id/tasks",
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/results",
                      status=200,
                      body=results_fixture,
                      streaming=True,
                      content_type='application/json')

        job = crp.job("function Run(d) { return d; }")

        def get_results():
            left = N
            httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/results",
                          status=200,
                          body=results_fixture,
                          streaming=True,
                          content_type='application/json')
            for result in job.get_results_stream():
                left = left - 1
                if left is 0:
                    break

        t = threading.Thread(target=get_results)
        t.start()

        def tasks():
            for x in range(N):
                yield x

        job.create_tasks(tasks())

        t.join()

if __name__ == '__main__':
    unittest.main()
