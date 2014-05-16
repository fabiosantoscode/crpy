# CrowdProcess API Client for Python

This is a client for [CrowdProcess](https://crowdprocess.com/)'s [REST API](https://crowdprocess.com/rest).

It works in python 2.7 and 3.4+.

## Installing

	pip install crowdprocess

or

	easy_install crowdprocess

## Usage example

```python
>>> from crowdprocess import CrowdProcess
>>> crp = CrowdProcess('username', 'password')

>>> x2 = crp.job('function Run (d) { return d*2; }')
>>> results = x2(range(5))
>>> list(results)
[0, 2, 4, 6, 8, 10] # comes in a random order
```

## More detailed use

### Importing and instanciating
```python
>>> from crowdprocess import CrowdProcess
>>> crp = CrowdProcess('username@email.com', 'password')
```

To get those credentials you must [register](https://crowdprocess.com/register) with CrowdProcess.

You can also instanciate it with a token instead of a username and password:

```python
>>> crp = CrowdProcess(token='3c46d593-5435-47c5-92aa-1613ade978c2')
```

### Jobs

#### Creating a job

With the `CrowdProcess` class instanciated above,

```python
>>> program='function Run (d) { return d }'
>>> job = crp.job(program)
>>> job.id
'3c46d593-5435-47c5-92aa-1613ade978c2'
```

Invoking `crp.job` with the `program` parameter automatically creates a job in CrowdProcess and returns an instanciated `Job`. 

After you get a `job.id`, you can use it to get a `Job` again, without creating it:

```python
>>> job = crp.job(id='3c46d593-5435-47c5-92aa-1613ade978c2')
```

#### Listing jobs

```python
>>> crp.list_jobs()
[{u'status': u'active', u'failed': 0, u'bid': 1, u'created': u'2014-05-14T10:07:52.747503Z', u'modified': u'2014-05-14T10:07:53.716147Z', u'browserHours': 137, u'finished': 1000, u'lastResult': u'2014-05-14T10:07:59.06Z', u'total': 1000, u'id': u'3c46d593-5435-47c5-92aa-1613ade978c2'}]
```

Prettier:

```python
>>> jobs = crp.list_jobs()
>>> print(json.dumps(jobs, sort_keys=True, indent=2))
[
  {
    "bid": 1, 
    "browserHours": 137, 
    "created": "2014-05-14T10:07:52.747503Z", 
    "failed": 0, 
    "finished": 1000, 
    "id": "3c46d593-5435-47c5-92aa-1613ade978c2", 
    "lastResult": "2014-05-14T10:07:59.06Z", 
    "modified": "2014-05-14T10:07:53.716147Z", 
    "status": "active", 
    "total": 1000
  }
]
```

#### Deleting a job

```python
>>> job = crp.job(id='3c46d593-5435-47c5-92aa-1613ade978c2')
>>> job.delete()
```

#### Deleting all jobs

```python
>>> crp.delete_jobs()
```

## Tasks and Results

After creating a job, you're all set to send it tasks and get back results.

`tasks` can be any iterable object, `results` will be a generator:

```python
>>> job = crp.job('function Run (d) { return Math.pow(d, 2); }')
>>> tasks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> results = job(tasks)
>>> list(results)
[49, 64, 16, 25, 9, 36, 4, 81, 0, 1]
```

which would be the same as,

```python
>>> job = crp.job('function Run (d) { return Math.pow(d, 2); }')
>>> list(job(range(10)))
[49, 64, 16, 25, 9, 36, 4, 81, 0, 1]
```

which would also be the same as,

```python
>>> job = crp.job('function Run (d) { return Math.pow(d, 2); }')
>>> def tasks():
...     for i in range(10):
...             yield i
... 
>>> list(job(tasks))
[25, 64, 49, 16, 36, 9, 0, 81, 1, 4]
```

Notice that the results never come in order.

### Pro tip: you can use the results of one job as tasks of another job

```python
>>> multiply = crp.job('function Run (d) { return d*2 }')
>>> divide = crp.job('function Run (d) { return d/2 }')
>>> numbers = range(10)
>>> multiplied = multiply(numbers)
>>> divided = divide(multiplied)
>>> list(divided)
[7, 2, 6, 1, 5, 9, 8, 4, 3, 0]
```

## Tasks and Results, lower level

### Submitting tasks

Once again, tasks may be any iterable:

```python
>>> multiply = crp.job('function Run (d) { return d*2 }')
>>> multiply.submit_tasks(range(10))
```

### Getting results

```python
>>> results = multiply.get_results()
>>> list(results)
[18, 8, 10, 4, 6, 16, 14, 0, 2, 12]
```

This delivers all the job's computed results at the moment, but you should in fact get every result as soon as it's computed, in a stream:

### Streaming results

You can also iterate through every result as soon as it comes in:

```python
>>> expected_results = 10
>>> results = multiply.get_results_stream()
>>> for result in results:
...     print(result)
...		expected_results -= 1
...		if expected_results == 0:
...			break
```

The stream does not know if or when a result might be computed and delivered, so you must count how many results you still expect to break the loop.

To use this properly you should start listening for streaming results before sending tasks, probably a separate thread:

```python
>>> import threading
>>> job = crp.job("function Run(d) { return d; }")
>>> def get_results():
...		expected_results = 10
...     for result in job.get_results_stream():
...             print(result)
...				expected_results -= 1
...				if expected_results == 0:
...					break
... 
>>> t = threading.Thread(target=get_results)
>>> t.start()
>>> job.submit_tasks(range(10))
>>> 7
9
6
2
3
8
1
4
0
5
>>> t.join()
```

Sometimes your tasks will have uncaught exceptions and those will cause a result to not be delivered, so you must account for those as well to decrease your expected_results counter.

### Errors and streaming errors

Sometimes your tasks throw uncaught exceptions, and you should get them:

```python
>>> program = """
... function Run (d) {
...     if (d === 4) {
...             throw new Error("oops, it's "+d);
...     } else {
...             return d;
...     }
... }
... """
>>> job = crp.job(program)
>>> job.submit_tasks(range(10))
>>> list(job.get_results())
[1, 6, 9, 8, 5, 7, 2, 3, 0] # oh no, 4 is missing...
>>> list(job.get_errors())
[{u'message': u"oops, it's 4", u'type': u'program', u'name': u'Error', u'stack': u'Run@blob:9a4029f7-fff7-4da8-b552-92507e341749:5\n[2]</</self.onmessage@blob:9a4029f7-fff7-4da8-b552-92507e341749:9\n'}]
>>> print(json.dumps(list(job.get_errors()), sort_keys=True, indent=2)) # prettier
[
  {
    "message": "oops, it's 4", 
    "name": "Error", 
    "stack": "Run@blob:9a4029f7-fff7-4da8-b552-92507e341749:5\n[2]</</self.onmessage@blob:9a4029f7-fff7-4da8-b552-92507e341749:9\n", 
    "type": "program"
  }
]
```

The same way you get streaming results, you can (and should) get streaming errors:

```python
>>> errors = multiply.get_errors_stream()
>>> for error in errors:
...     print(error)
```