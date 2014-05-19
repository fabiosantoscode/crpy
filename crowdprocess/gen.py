from itertools import cycle

def genx ():
	for x in range(10):
		yield "x: "+str(x)

def geny ():
	for y in range(20):
		yield "y: "+str(y)

def merge (*args):
	expected_stops = len(args)
	c = cycle(args)
	while True:
		try:
			yield c.next().next()
		except StopIteration:
			print "StopIteration"
			expected_stops -= 1
			if expected_stops == 0:
				print "raising now"
				raise StopIteration

x = merge(genx(), geny())
for xs in x:
	print xs