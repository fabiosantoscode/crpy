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
divide_results_fixture = "\n".join([str(x) for x in range(N)])+"\n"
tasksSent = []
baseAPIUrl = "https://api.crowdprocess.com/jobs/"

class Tests(unittest.TestCase):

    @httpretty.activate
    def test_io(self):
        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id"
                      }),
                      status=201,
                      content_type='application/json')

        job = crpself._headers(program_fixture)

        tasks = range(N)

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/results",
                      status=200,
                      body=results_fixture,
                      streaming=True,
                      content_type='application/json')

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id/tasks",
                      status=201)

        for result in job(tasks):
            self.assertIn(result/2, tasks)

    @httpretty.activate
    def test_pipe(self):
        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id1"
                      }),
                      status=201,
                      content_type='application/json')
        
        multiply = crp.job(program_fixture)

        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id2"
                      }),
                      status=201,
                      content_type='application/json')

        divide = crp.job("function Run(d) { return d/2; }")

        tasks = range(N)

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id1/tasks",
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id1/results",
                      status=200,
                      body=results_fixture,
                      stream=True,
                      content_type='application/json')

        multiplied = multiply(tasks)

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id2/tasks",
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id2/results",
                      status=200,
                      body=divide_results_fixture,
                      stream=True,
                      content_type='application/json')

        divided = divide(multiplied)

        for result in divided:
            self.assertIn(result, tasks)

if __name__ == '__main__':
    unittest.main()
