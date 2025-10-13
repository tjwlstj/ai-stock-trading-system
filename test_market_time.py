import datetime

from backend.app.utils.market_time import MarketSession


def _localize(session: MarketSession, dt: datetime.datetime) -> datetime.datetime:
    return session.timezone.localize(dt)


def test_next_market_open_rolls_over_month_end():
    session = MarketSession('NYSE')
    dt = datetime.datetime(2024, 1, 31, 17, 0)

    next_open = session.next_market_open(dt)

    expected = _localize(session, datetime.datetime(2024, 2, 1, 9, 30))
    assert next_open == expected


def test_next_market_open_skips_year_end_holiday():
    session = MarketSession('NYSE')
    dt = datetime.datetime(2024, 12, 31, 17, 0)

    next_open = session.next_market_open(dt)

    expected = _localize(session, datetime.datetime(2025, 1, 2, 9, 30))
    assert next_open == expected


def test_next_market_open_skips_independence_day():
    session = MarketSession('NYSE')
    dt = datetime.datetime(2024, 7, 3, 17, 0)

    next_open = session.next_market_open(dt)

    expected = _localize(session, datetime.datetime(2024, 7, 5, 9, 30))
    assert next_open == expected
