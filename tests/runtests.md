Running the automated tests

Place the supplied file here:

schedule-app/
├── app.py
├── database.py
├── helpers.py
├── requirements.txt
└── tests/
    └── test_database.py

1. Install pytest

From the schedule-app folder:

pip install pytest

For an optional coverage report:

pip install pytest-cov

You may also add these development dependencies to requirements.txt:

pytest
pytest-cov

2. Run the tests

python -m pytest -v

Run only this file:

python -m pytest tests/test_database.py -v

Stop after the first failure:

python -m pytest -x -v

Show printed output:

python -m pytest -s -v

Generate a coverage report:

python -m pytest --cov=database --cov=helpers --cov-report=term-missing

Safety

The tests do not use your real database. Each test changes into a temporarydirectory and creates a disposable schedule_app.db there. Pytest deletes thetemporary data after the test run.

Important

This suite was written against the current public version of yourdatabase.py and helpers.py. A failed test does not automatically mean thetest is wrong. It may reveal a real bug, an undocumented rule, or a behaviorthat needs a clearer decision.