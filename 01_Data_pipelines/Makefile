venv:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
run_unit_test:
	source venv/bin/activate && cd test && pytest
run_local:
	./venv/bin/python main.py --input data --output output --stats True >> run_log.txt 2>&1
