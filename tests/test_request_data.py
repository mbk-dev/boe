"""Tests for request_data.get_data_frame padding direction.

The official Bank-Rate table is served newest-first; padding must fill each
day from the PREVIOUS rate change (forward-fill in calendar time), not from
the next one (the look-ahead bug found 2026-07-12: every day between two
changes carried the future rate).
"""

import pandas as pd
import pytest

from boe import kr, request_data

# Newest-first, like the real Bank-Rate.asp table.
SAMPLE_HTML = """
<table>
  <thead><tr><th>Date Changed</th><th>Rate</th></tr></thead>
  <tbody>
    <tr><td>16 Dec 21</td><td>0.25</td></tr>
    <tr><td>19 Mar 20</td><td>0.10</td></tr>
    <tr><td>05 Mar 09</td><td>0.50</td></tr>
  </tbody>
</table>
"""


class FakeResponse:
    text = SAMPLE_HTML
    status_code = 200


@pytest.fixture()
def fake_page(monkeypatch):
    monkeypatch.setattr(
        request_data.requests, "get", lambda url, headers=None: FakeResponse()
    )


def test_pads_forward_from_previous_change(fake_page):
    s = request_data.get_data_frame()

    # Ascending daily index from the first change through TODAY (the standing
    # rate stays in effect after the last change).
    assert s.index[0] == pd.Period("2009-03-05", freq="D")
    assert s.index[-1] == pd.Timestamp.today().to_period("D")
    # Between 2009-03-05 and 2020-03-19 the rate WAS 0.50 the whole time.
    assert s[pd.Period("2012-06-01", freq="D")] == 0.50
    assert s[pd.Period("2020-03-18", freq="D")] == 0.50
    # From 2020-03-19 until the 2021-12-16 hike it was 0.10.
    assert s[pd.Period("2020-06-01", freq="D")] == 0.10
    # The last change carries forward to today.
    assert s[pd.Period("2021-12-16", freq="D")] == 0.25
    assert s.iloc[-1] == 0.25


def test_recent_start_period_returns_the_standing_rate(fake_page):
    """A window opening after the last change (the nightly only-last-values
    path) must return the standing rate, not an empty series."""
    start = (pd.Timestamp.today() - pd.DateOffset(months=2)).strftime("%Y-%m-%d")

    s = request_data.get_data_frame(start_period=start)

    assert len(s) > 0
    assert s.index[0] == pd.Period(start, freq="D")
    assert (s == 0.25).all()


def test_start_period_keeps_the_rate_in_effect(fake_page):
    """Slicing must happen AFTER padding: a window opening between two changes
    starts at start_period and carries the rate set by the PREVIOUS change
    (otherwise a recent start_period drops the standing rate entirely)."""
    s = request_data.get_data_frame(start_period="2020-01-01")

    assert s.index[0] == pd.Period("2020-01-01", freq="D")
    assert s[pd.Period("2020-01-01", freq="D")] == 0.50   # set 2009-03-05
    assert s[pd.Period("2020-06-01", freq="D")] == 0.10


def test_get_bank_rate_returns_fractions(fake_page):
    s = kr.get_bank_rate()

    assert s.name == "bank_rate"
    assert s[pd.Period("2012-06-01", freq="D")] == pytest.approx(0.0050)
