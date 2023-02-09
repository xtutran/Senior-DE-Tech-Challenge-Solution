venv:
	/usr/local/anaconda3/bin/python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
run_unit_test:
	source venv/bin/activate && cd test && pytest
run_local:
	./venv/bin/python main.py --input data --output output --stats True >> run.log 2>&1
