from crowdprocess import CrowdProcess
import unittest
from time import sleep
import threading
import json
import httpretty

crp = CrowdProcess('username', 'password')

N = 10
program_fixture = "function Run(d) { if (d % 17 === 0) { throw 'oh no it is '+d; } return d; }"
results_fixture = "\n".join([str(x*2) for x in range(N)])+"\n"
divide_results_fixture = "\n".join([str(x) for x in range(N)])+"\n"
tasksSent = []

results_no4_fixture = "\n".join([str(x*2) for x in range(N) if x not in [4]])+"\n"
errors_fixture = json.dumps({"stack": "oops it's 4"})+ "\n"

baseAPIUrl = "https://api.crowdprocess.com/jobs/"

import select

def select_mock (rlist, wlist, xlist, timeout=0):
  inputready = [r for r in rlist if r.closed is not True]
  return inputready, [], []

select.select = select_mock

class Tests(unittest.TestCase):

    @httpretty.activate
    def test_io(self):
        httpretty.register_uri(httpretty.POST, baseAPIUrl,
                      body=json.dumps({
                        "id": "job_id"
                      }),
                      status=201,
                      content_type='application/json')

        job = crp.job(program_fixture)

        tasks = range(N)

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/results",
                      status=200,
                      body=results_no4_fixture,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id/errors",
                      status=200,
                      body=errors_fixture,
                      content_type='application/json')

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id/tasks",
                      status=201)

        results = job(tasks).results
        for result in results:
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
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id1/errors",
                      status=200,
                      body="",
                      content_type='application/json')

        multiplied = multiply(tasks).results

        httpretty.register_uri(httpretty.POST, baseAPIUrl+"job_id2/tasks",
                      status=201,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id2/results",
                      status=200,
                      body=divide_results_fixture,
                      content_type='application/json')

        httpretty.register_uri(httpretty.GET, baseAPIUrl+"job_id2/errors",
                      status=200,
                      body="",
                      content_type='application/json')

        divided = divide(multiplied).results

        for result in divided:
            self.assertIn(result, tasks)

if __name__ == '__main__':
    unittest.main()
