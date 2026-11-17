def format_indian_currency(amount: float, symbol: str = "₹") -> str:
    """
    Format a monetary amount in Indian numbering format (e.g. ₹3,87,122.80).
    Rule: Last three digits grouped, then groups of two digits.
    """
    try:
        amt = float(amount)
        is_neg = amt < 0
        amt = abs(amt)
        parts = f"{amt:.2f}".split(".")
        integer_part = parts[0]
        decimal_part = parts[1]

        if len(integer_part) <= 3:
            grouped = integer_part
        else:
            last_three = integer_part[-3:]
            remainder = integer_part[:-3]
            rev = remainder[::-1]
            groups = [rev[i:i+2] for i in range(0, len(rev), 2)]
            grouped = ",".join(groups)[::-1] + "," + last_three

        sign = "-" if is_neg else ""
        return f"{symbol}{sign}{grouped}.{decimal_part}"
    except Exception:
        return f"{symbol}{amount}"
