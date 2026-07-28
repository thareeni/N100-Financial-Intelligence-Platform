.PHONY: load ratios test clean format lint

load:
	python -m src.etl.loader

ratios:
	python -m src.analytics.runner

test:
	pytest tests/ --html=output/pytest_report.html --self-contained-html

clean:
	python -c "import os, glob; [os.remove(f) for f in glob.glob('*.pyc') + glob.glob('**/__pycache__', recursive=True)]"

format:
	black src/ tests/

lint:
	ruff check src/ tests/
