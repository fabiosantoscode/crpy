import crowdprocess
import unittest
from time import sleep
import threading
# get https://github.com/dropbox/responses later

crp = crowdprocess.CrowdProcess(
    username="jj@crowdprocess.com", password="blablabla")
N = 1000
tasksSent = []


class Tests(unittest.TestCase):

    def test_low_level(self):
        job = crp.Job()
        job.create("function Run(d) { return d*2; }")
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

        job = crp.Job(id=job.id)
        s = job.show()
        self.assertEqual(s["total"], N)
        self.assertEqual(s["finished"], N)
        self.assertEqual(s["failed"], 0)
        self.assertEqual(s["id"], job.id)

    def test_streams(self):
        job = crp.Job()
        job.create("function Run(d) { return d; }")

        def get_results():
            left = N
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

    def test_io(self):
        job = crp.Job()
        job.create("function Run(d) { return d*2; }")

        tasks = range(N)

        io = job.io(tasks)
        for result in io:
            self.assertIn(result/2, tasks)

    def test_pipe(self):
        multiply = crp.Job()
        multiply.create("function Run(d) { return d*2; }")

        divide = crp.Job()
        divide.create("function Run(d) { return d/2; }")

        tasks = range(N)
        multiplied = multiply.io(tasks)
        divided = divide.io(multiplied)
        for result in divided:
            self.assertIn(result, tasks)

if __name__ == '__main__':
    unittest.main()
