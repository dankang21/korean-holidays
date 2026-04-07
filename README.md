# korean-holidays

**Korean public holidays calculator with automatic lunar calendar conversion**

A Python library that automatically calculates Korean public holidays. Includes automatic lunar-to-solar conversion for Seollal (설날), Chuseok (추석), and Buddha's Birthday (부처님오신날), plus substitute holiday rules. No hardcoding — works for any year.

[![PyPI](https://img.shields.io/pypi/v/korean-holidays)](https://pypi.org/project/korean-holidays/)
[![Python](https://img.shields.io/pypi/pyversions/korean-holidays)](https://pypi.org/project/korean-holidays/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

- **Automatic lunar conversion** — Seollal (설날), Chuseok (추석), and Buddha's Birthday (부처님오신날) calculated automatically each year
- **Automatic substitute holidays** — Reflects the expanded 2021 substitute holiday rules
- **Any year supported** — No hardcoding, just call `get_holidays(2030)`
- **Trading day calculation** — `is_trading_day()`, `count_trading_days()`
- **Built-in cache** — No recomputation on repeated calls for the same year
- **Zero config** — No API key required, no network required

## Installation

```bash
pip install korean-holidays
```

## Quick Start

```python
from datetime import date
from korean_holidays import get_holidays, is_holiday, is_trading_day, count_trading_days

# All public holidays for 2026
holidays = get_holidays(2026)
for d, name in sorted(holidays.items()):
    print(f"{d} {name}")

# Check a specific date
print(is_holiday(date(2026, 2, 17)))      # True (Seollal)
print(is_holiday(date(2026, 5, 25)))      # True (Buddha's Birthday substitute holiday)
print(is_trading_day(date(2026, 4, 6)))   # True (Monday, weekday)

# Number of trading days in a year
days = count_trading_days(date(2026, 1, 1), date(2026, 12, 31))
print(f"Trading days in 2026: {days}")

# Works for 2030 too (not hardcoded)
holidays_2030 = get_holidays(2030)
```

## API Reference

| Function | Description |
|----------|-------------|
| `get_holidays(year)` | Returns all public holidays for the given year as `{date: name}` |
| `is_holiday(date)` | Returns whether the date is a public holiday |
| `get_holiday_name(date)` | Returns the holiday name, or None if not a holiday |
| `is_trading_day(date)` | Returns whether the date is a stock market trading day (excludes weekends + holidays) |
| `get_trading_days(start, end)` | Returns a list of trading days in the date range |
| `count_trading_days(start, end)` | Returns the number of trading days in the date range |

## Supported Holidays

**Fixed holidays:** New Year's Day (신정), Independence Movement Day (삼일절), Labor Day (근로자의날), Children's Day (어린이날), Memorial Day (현충일), Liberation Day (광복절), National Foundation Day (개천절), Hangul Day (한글날), Christmas

**Lunar holidays (automatically calculated):** Seollal (설날) 3-day holiday, Chuseok (추석) 3-day holiday, Buddha's Birthday (부처님오신날)

**Substitute holidays (automatically applied):**
- Seollal (설날) / Chuseok (추석): If overlapping with Sunday, the next available weekday after the holiday period
- Children's Day (어린이날): If overlapping with Saturday/Sunday (since 2014)
- Independence Movement Day (삼일절) / Liberation Day (광복절) / National Foundation Day (개천절) / Hangul Day (한글날): If overlapping with Saturday/Sunday (since 2021)
- Buddha's Birthday (부처님오신날): If overlapping with Saturday/Sunday (since 2023)

## Disclaimer

Holiday calculations are based on current legislation and may require updates if laws are amended. Ad-hoc public holidays (e.g., election days) are not included.

## License

MIT License. See [LICENSE](LICENSE).
