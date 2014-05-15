test:
	python -m unittest discover tests '*.py'

dist:
	python setup.py sdist upload	

clean:
	rm -rf build dist

.PHONY: dist