from utils.helpers import parse_duration_days

def test_parse_duration_days_direct_days():
    assert parse_duration_days("15 dias") == 15
    assert parse_duration_days("5 dias") == 5
    assert parse_duration_days("10d") == 10
    assert parse_duration_days("  8 dias   ") == 8

def test_parse_duration_days_weeks():
    assert parse_duration_days("2 semanas") == 14
    assert parse_duration_days("3 semanas") == 21
    assert parse_duration_days("1 sem") == 7

def test_parse_duration_days_months():
    assert parse_duration_days("1 mês") == 30
    assert parse_duration_days("2 meses") == 60
    assert parse_duration_days("1 mes") == 30

def test_parse_duration_days_date_range():
    # de 01/06 a 15/06 -> Junho tem 30 dias, mas sem ano assume 2026.
    # Diferença: 15/06/2026 - 01/06/2026 = 14 dias + 1 (inclusivo) = 15 dias.
    assert parse_duration_days("de 01/06 a 15/06") == 15
    # 01/06/2026 a 30/06/2026 -> 30 dias.
    assert parse_duration_days("01/06/2026 a 30/06/2026") == 30
    # de 28/05/2026 até 02/06/2026 -> 28, 29, 30, 31, 01, 02 -> 6 dias.
    assert parse_duration_days("de 28/05/2026 até 02/06/2026") == 6

def test_parse_duration_days_fallback():
    assert parse_duration_days("") == 30
    assert parse_duration_days(None) == 30
    assert parse_duration_days("período indeterminado") == 30
