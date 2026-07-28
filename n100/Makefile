<<<<<<< HEAD
.PHONY: load ratios screener peer test clean format lint
=======
.PHONY: load ratios test clean format lint
>>>>>>> f81a2dbcaaaeea2037fd8e762649a9c1a489d5d3

load:
	python -m src.etl.loader

ratios:
	python -m src.analytics.runner

<<<<<<< HEAD
screener:
	python -m src.screener.engine

peer:
	python -m src.analytics.peer

=======
>>>>>>> f81a2dbcaaaeea2037fd8e762649a9c1a489d5d3
test:
	pytest tests/ --html=output/pytest_report.html --self-contained-html

clean:
	python -c "import os, glob; [os.remove(f) for f in glob.glob('*.pyc') + glob.glob('**/__pycache__', recursive=True)]"

format:
	black src/ tests/

lint:
	ruff check src/ tests/
