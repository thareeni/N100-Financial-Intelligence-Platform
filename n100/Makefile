.PHONY: run dashboard load ratios screener peer health dupont valuation investment test clean format lint

run:
	python src/main.py

dashboard:
	streamlit run dashboard/app.py

load:
	python -m src.etl.loader

ratios:
	python -m src.analytics.runner

screener:
	python -m src.screener.engine

peer:
	python -m src.analytics.peer

health:
	python -m src.analytics.financial_health

dupont:
	python -m src.analytics.dupont

valuation:
	python -m src.analytics.valuation

investment:
	python -m src.analytics.investment_score

test:
	pytest tests/ --html=output/pytest_report.html --self-contained-html

clean:
	python -c "import os, glob; [os.remove(f) for f in glob.glob('*.pyc') + glob.glob('**/__pycache__', recursive=True)]"

format:
	black src/ tests/ dashboard/

lint:
	ruff check src/ tests/ dashboard/
