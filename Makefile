build:
		virtualenv env
		. env/bin/activate && env/bin/pip install -r requirements.txt

test:
	PYTHONPATH=spotbox/:$PYTHONPATH
	. env/bin/activate && env/bin/nosetests

unittest:
	PYTHONPATH=spotbox/:$PYTHONPATH
	. env/bin/activate && env/bin/nosetests -I integration_test
