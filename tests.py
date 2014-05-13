import crowdprocess
import unittest
from time import sleep
import threading
# get https://github.com/dropbox/responses later

crp = crowdprocess.CrowdProcess(
    username="jj@crowdprocess.com", password="blablabla")
N = 4000
tasksSent = []


class Tests(unittest.TestCase):

    def est_low_level(self):
        job = crp.Job()
        job.create("function Run(d) { return d*2; }")
        self.assertIsNotNone(job.id)

        def tasks():
            for x in range(0, N):
                tasksSent.append(x)
                yield x

        job.create_tasks(tasks)

        sleep(2)

        results_got = 0
        for result in job.get_results():
            self.assertTrue(result / 2 in tasksSent)
            results_got += 1

        self.assertEqual(results_got, N)

        # reference by id
        job = crp.Job(id=job.id)
        s = job.show()
        self.assertEqual(s["total"], N)
        self.assertEqual(s["finished"], N)
        self.assertEqual(s["failed"], 0)
        self.assertEqual(s["id"], job.id)

    def est_streams(self):
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

        job.create_tasks(tasks)

        t.join()

    def test_io(self):
        job = crp.Job()
        job.create("function Run(d) { return d; }")

        io = job.io(range(N))
        for result in io:
            print(result)

if __name__ == '__main__':
    unittest.main()
