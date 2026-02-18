import pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    # docstringを取得してレポートに追加する
    if report.when == 'call':
        report.description = str(item.function.__doc__)

def pytest_html_results_table_header(cells):
    # レポートに Description（説明）列を追加
    cells.insert(2, "<th>Description</th>")

def pytest_html_results_table_row(report, cells):
    # Description 列に docstring を挿入
    cells.insert(2, f"<td>{getattr(report, 'description', '')}</td>")