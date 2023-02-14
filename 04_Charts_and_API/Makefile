venv:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
app:
	source venv/bin/activate && streamlit run app.py
build_image:
	docker build -t covid19_streamlit .
run_app:
	docker run -p 8501:8501 covid19_streamlit