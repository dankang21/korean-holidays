"""Automatic Korean public holiday calculation.

Automatically computes public holidays for any given year by applying
fixed holidays + lunar holidays (Seollal/Chuseok/Buddha's Birthday)
+ substitute holiday rules.
"""

from datetime import date, timedelta
from functools import lru_cache

from korean_lunar_calendar import KoreanLunarCalendar


# ── Fixed holidays (same date every year) ──
FIXED_HOLIDAYS = [
    (1, 1, "신정"),
    (3, 1, "삼일절"),
    (5, 1, "근로자의날"),
    (5, 5, "어린이날"),
    (6, 6, "현충일"),
    (8, 15, "광복절"),
    (10, 3, "개천절"),
    (10, 9, "한글날"),
    (12, 25, "크리스마스"),
]

# Substitute holiday targets (enacted 2014, expanded 2021)
# Seollal (설날) / Chuseok (추석): substitute holiday if overlaps with Sunday
# Children's Day (어린이날): substitute if overlaps with Sat/Sun (2014~)
# March 1st Movement Day (삼일절) / Liberation Day (광복절) /
# National Foundation Day (개천절) / Hangul Day (한글날):
#   substitute if overlaps with Sat/Sun (2021~)
SUBSTITUTE_HOLIDAY_TARGETS = {"삼일절", "광복절", "개천절", "한글날", "어린이날"}


def _lunar_to_solar(year: int, lunar_month: int, lunar_day: int) -> date:
    """Convert a lunar date to a solar (Gregorian) date."""
    cal = KoreanLunarCalendar()
    cal.setLunarDate(year, lunar_month, lunar_day, False)
    iso = cal.SolarIsoFormat()
    return date.fromisoformat(iso)


@lru_cache(maxsize=50)
def get_holidays(year: int) -> dict[date, str]:
    """Return all Korean public holidays for the given year.

    Args:
        year: The year to compute holidays for (e.g. 2026).

    Returns:
        A dict mapping each holiday date to its Korean name.
    """
    holidays: dict[date, str] = {}

    # 1. Fixed holidays
    for month, day, name in FIXED_HOLIDAYS:
        d = date(year, month, day)
        holidays[d] = name

    # 2. Lunar holidays
    # Seollal (설날) — Lunar New Year (lunar 1/1) + day before + day after
    try:
        seollal = _lunar_to_solar(year, 1, 1)
        holidays[seollal - timedelta(days=1)] = "설날 연휴"
        holidays[seollal] = "설날"
        holidays[seollal + timedelta(days=1)] = "설날 연휴"
    except Exception:
        pass

    # Chuseok (추석) — Korean Thanksgiving (lunar 8/15) + day before + day after
    try:
        chuseok = _lunar_to_solar(year, 8, 15)
        holidays[chuseok - timedelta(days=1)] = "추석 연휴"
        holidays[chuseok] = "추석"
        holidays[chuseok + timedelta(days=1)] = "추석 연휴"
    except Exception:
        pass

    # Buddha's Birthday (부처님오신날) — lunar 4/8
    try:
        buddha = _lunar_to_solar(year, 4, 8)
        holidays[buddha] = "부처님오신날"
    except Exception:
        pass

    # 3. Apply substitute holidays
    substitutes: dict[date, str] = {}

    # Seollal (설날) / Chuseok (추석) substitute:
    # if any day in the holiday cluster falls on Sunday, add the next weekday after the cluster
    for base_name in ["설날", "추석"]:
        cluster = [d for d, n in holidays.items() if base_name in n]
        if cluster:
            cluster.sort()
            has_sunday = any(d.weekday() == 6 for d in cluster)
            if has_sunday:
                next_day = max(cluster) + timedelta(days=1)
                while next_day in holidays or next_day.weekday() >= 5:
                    next_day += timedelta(days=1)
                substitutes[next_day] = f"{base_name} 대체휴일"

    # Fixed holiday substitutes (from 2021)
    if year >= 2021:
        for month, day, name in FIXED_HOLIDAYS:
            if name not in SUBSTITUTE_HOLIDAY_TARGETS:
                continue
            d = date(year, month, day)
            if name == "어린이날":
                # Children's Day (어린이날): substitute for both Sat and Sun
                if d.weekday() == 5:  # Saturday
                    sub = d + timedelta(days=2)  # Monday
                    while sub in holidays or sub in substitutes:
                        sub += timedelta(days=1)
                    substitutes[sub] = f"{name} 대체휴일"
                elif d.weekday() == 6:  # Sunday
                    sub = d + timedelta(days=1)
                    while sub in holidays or sub in substitutes:
                        sub += timedelta(days=1)
                    substitutes[sub] = f"{name} 대체휴일"
            else:
                # March 1st Movement Day / Liberation Day /
                # National Foundation Day / Hangul Day: substitute for Sat/Sun
                if d.weekday() == 5:  # Saturday
                    sub = d + timedelta(days=2)
                    while sub in holidays or sub in substitutes:
                        sub += timedelta(days=1)
                    substitutes[sub] = f"{name} 대체휴일"
                elif d.weekday() == 6:  # Sunday
                    sub = d + timedelta(days=1)
                    while sub in holidays or sub in substitutes:
                        sub += timedelta(days=1)
                    substitutes[sub] = f"{name} 대체휴일"

    # Buddha's Birthday (부처님오신날) substitute (from 2023)
    if year >= 2023:
        buddha_dates = [d for d, n in holidays.items() if n == "부처님오신날"]
        for d in buddha_dates:
            if d.weekday() == 5:  # Saturday
                sub = d + timedelta(days=2)
                while sub in holidays or sub in substitutes:
                    sub += timedelta(days=1)
                substitutes[sub] = "부처님오신날 대체휴일"
            elif d.weekday() == 6:  # Sunday
                sub = d + timedelta(days=1)
                while sub in holidays or sub in substitutes:
                    sub += timedelta(days=1)
                substitutes[sub] = "부처님오신날 대체휴일"

    holidays.update(substitutes)
    return holidays


def is_holiday(d: date) -> bool:
    """Check whether the given date is a Korean public holiday."""
    return d in get_holidays(d.year)


def get_holiday_name(d: date) -> str | None:
    """Return the holiday name for the given date, or None if not a holiday."""
    return get_holidays(d.year).get(d)


def is_trading_day(d: date) -> bool:
    """Check whether the given date is a Korean stock market trading day."""
    if d.weekday() >= 5:
        return False
    return not is_holiday(d)


def get_trading_days(start: date, end: date) -> list[date]:
    """Return a list of Korean stock market trading days between two dates."""
    days = []
    current = start
    while current <= end:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
    return days


def count_trading_days(start: date, end: date) -> int:
    """Count the number of Korean stock market trading days between two dates."""
    return len(get_trading_days(start, end))
