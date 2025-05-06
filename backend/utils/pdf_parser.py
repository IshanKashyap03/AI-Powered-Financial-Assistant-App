def extract_debit_totals(text):
    lines = text.splitlines()
    total_deposits, total_withdrawals = 0.0, 0.0

    for i, line in enumerate(lines):
        if "Plus total deposits" in line:
            try:
                next_line = lines[i + 1]
                amount_str = next_line.strip().replace('$', '').replace(',', '')
                total_deposits = float(amount_str)
            except (IndexError, ValueError):
                print("Failed to parse deposits from line:", line)

        if "Minus total withdrawals" in line:
            try:
                next_line = lines[i + 1]
                amount_str = next_line.strip().replace('$', '').replace(',', '')
                total_withdrawals = float(amount_str)
            except (IndexError, ValueError):
                print("Failed to parse withdrawals from line:", line)

    return total_deposits, total_withdrawals

def extract_credit_totals(text):
    lines = text.splitlines()
    total_credit_spending = 0.0

    for i, line in enumerate(lines):
        if "Purchases/charges +" in line:
            try:
                next_line = lines[i + 1].strip()
                amount_str = next_line.replace('$', '').replace(',', '')
                total_credit_spending = float(amount_str)
            except (IndexError, ValueError):
                print("Failed to parse credit spending from line:", line)

    return total_credit_spending