"""한국 공휴일 계산 테스트."""

from datetime import date
from korean_holidays import (
    get_holidays, is_holiday, is_trading_day,
    get_trading_days, count_trading_days, get_holiday_name,
)


class TestFixedHolidays:
    def test_new_year(self):
        assert is_holiday(date(2026, 1, 1))
        assert get_holiday_name(date(2026, 1, 1)) == "신정"

    def test_march_1st(self):
        assert is_holiday(date(2026, 3, 1))

    def test_christmas(self):
        assert is_holiday(date(2026, 12, 25))

    def test_normal_day(self):
        assert not is_holiday(date(2026, 4, 6))  # 월요일, 평일


class TestLunarHolidays:
    def test_seollal_2026(self):
        # 2026 설날: 음력 1/1 = 양력 2/17
        assert is_holiday(date(2026, 2, 16))  # 전날
        assert is_holiday(date(2026, 2, 17))  # 설날
        assert is_holiday(date(2026, 2, 18))  # 다음날

    def test_chuseok_2026(self):
        # 2026 추석: 음력 8/15 = 양력 9/25
        assert is_holiday(date(2026, 9, 24))  # 전날
        assert is_holiday(date(2026, 9, 25))  # 추석
        assert is_holiday(date(2026, 9, 26))  # 다음날

    def test_buddha_birthday_2026(self):
        # 2026 부처님오신날: 양력 5/24 (일요일)
        assert is_holiday(date(2026, 5, 24))

    def test_seollal_2027(self):
        # 2027 설날: 음력 1/1 = 양력 2/7
        assert is_holiday(date(2027, 2, 6))
        assert is_holiday(date(2027, 2, 7))
        assert is_holiday(date(2027, 2, 8))

    def test_any_year(self):
        # 아무 연도든 계산 가능
        h2030 = get_holidays(2030)
        assert len(h2030) > 10  # 최소 10개 이상 공휴일


class TestSubstituteHolidays:
    def test_buddha_substitute_2026(self):
        # 2026 부처님오신날 5/24(일) → 대체휴일 5/25(월)
        assert is_holiday(date(2026, 5, 25))
        assert "대체" in get_holiday_name(date(2026, 5, 25))

    def test_no_substitute_before_2021(self):
        # 2020년에는 삼일절 대체휴일 없음 (3/1이 일요일이라도)
        h2020 = get_holidays(2020)
        # 삼일절 대체휴일이 있으면 안 됨 (2021 이전)
        subs = [n for d, n in h2020.items() if "삼일절 대체" in n]
        assert len(subs) == 0


class TestTradingDay:
    def test_weekday(self):
        assert is_trading_day(date(2026, 4, 6))  # 월요일

    def test_weekend(self):
        assert not is_trading_day(date(2026, 4, 4))  # 토요일
        assert not is_trading_day(date(2026, 4, 5))  # 일요일

    def test_holiday(self):
        assert not is_trading_day(date(2026, 1, 1))
        assert not is_trading_day(date(2026, 12, 25))

    def test_substitute_holiday(self):
        assert not is_trading_day(date(2026, 5, 25))  # 부처님오신날 대체휴일


class TestTradingDays:
    def test_one_week(self):
        days = get_trading_days(date(2026, 4, 6), date(2026, 4, 10))
        assert len(days) == 5  # 월~금

    def test_count(self):
        count = count_trading_days(date(2026, 4, 6), date(2026, 4, 10))
        assert count == 5

    def test_year(self):
        count = count_trading_days(date(2026, 1, 1), date(2026, 12, 31))
        assert 240 <= count <= 252  # 한국 연 거래일 범위


class TestGetHolidays:
    def test_returns_dict(self):
        h = get_holidays(2026)
        assert isinstance(h, dict)
        assert all(isinstance(k, date) for k in h.keys())
        assert all(isinstance(v, str) for v in h.values())

    def test_cached(self):
        # 같은 연도 두 번 호출하면 캐시에서
        h1 = get_holidays(2026)
        h2 = get_holidays(2026)
        assert h1 is h2  # 같은 객체 (캐시)
