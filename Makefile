test:
	python -m unittest discover tests '*.py'

dist:
	python setup.py sdist upload

rst:
	pandoc --from=markdown --to=rst --output=README.rst README.md

clean:
	rm -rf build dist

.PHONY: dist