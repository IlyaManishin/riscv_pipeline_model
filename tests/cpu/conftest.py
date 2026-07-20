import pytest
from pathlib import Path
from tests_config import *
from tests.cpu.reports.perf_reports import gen_compare_performance_report


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    summary_inputs = {
        "sc": Path(SC_TRACE_DIR) / PERF_SUMMARY_NAME,
        "pl": Path(PL_TRACE_DIR) / PERF_SUMMARY_NAME,
    }

    full_report_path = Path(TRACE_DIRNAME) / "global_performance_report.csv"
    compact_report_path = Path(TRACE_DIRNAME) / \
        "global_performance_compact_report.csv"

    gen_compare_performance_report(
        summaries=summary_inputs,
        output_path=full_report_path,
        columns=FULL_PERF_REPORT_COLS
    )

    gen_compare_performance_report(
        summaries=summary_inputs,
        output_path=compact_report_path,
        columns=COMPACT_PERF_REPORT_COLS
    )
