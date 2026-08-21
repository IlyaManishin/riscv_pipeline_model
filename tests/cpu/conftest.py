import pytest

from reports import reports

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    reports.build_reports()


