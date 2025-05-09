import re

def parse_debit_transactions(text):
    lines = text.splitlines()
    transactions = []
    i = 0

    while i < len(lines) - 3:
        date = lines[i].strip()

        # Check if it's a date like "Apr 19"
        if re.match(r"^[A-Z][a-z]{2} \d{1,2}$", date):
            txn_type = lines[i + 1].strip()
            amount_str = lines[i + 2].strip()

            # Check if amount is a float
            if re.match(r"^\$?\d{1,3}(,\d{3})*\.\d{2}$", amount_str) or re.match(r"^\d+\.\d{2}$", amount_str):
                try:
                    amount = float(amount_str.replace("$", "").replace(",", ""))
                    description = lines[i + 4].strip() if i + 4 < len(lines) else ""
                    transactions.append({
                        "date": date,
                        "type": txn_type,
                        "amount": amount,
                        "description": description
                    })
                    i += 5  # skip to next transaction
                except:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    filtered_transactions = filter_debit_transactions(transactions)
    return filtered_transactions

def filter_debit_transactions(transactions):
        excluded_types = ["Opening Balance", "Closing Balance", "Deposit", "Payroll dep.", "GST"]
        credit_payment_keywords = ["credit card"]

        expenses = []

        for txn in transactions:
            if(txn["type"] not in excluded_types):
                if txn["type"] == "MB-Transfer to" and any(k in txn["description"].lower() for k in credit_payment_keywords):
                    continue
                expenses.append(txn)
        return expenses


def is_valid_amount(s):
    """Checks if the string is a valid decimal amount (e.g., 12.95)"""
    return re.match(r"^\d+\.\d{2}$", s.strip())

def parse_amount(amount_str, next_line):
    """
    Converts the amount string to float, applying minus sign if next line is '-'.
    """
    try:
        raw = amount_str.strip().replace(",", "")
        amount = float(raw)
        if next_line.strip() == "-":
            amount = -amount
        return amount
    except ValueError:
        return None

def parse_credit_transactions(text):
    lines = text.splitlines()
    transactions = []
    i = 0

    while i < len(lines) - 4:
        if re.match(r"^\d{3}$", lines[i].strip()):
            ref = lines[i].strip()
            trans_date = lines[i + 1].strip()
            post_date = lines[i + 2].strip()
        else:
            i += 1
            continue

        # Case 1: 6-line transaction
        if i + 5 < len(lines) and is_valid_amount(lines[i + 5]):
            desc_line1 = lines[i + 3].strip()
            desc_line2 = lines[i + 4].strip()
            description = f"{desc_line1} {desc_line2}"
            amount_str = lines[i + 5].strip()
            next_line = lines[i + 6].strip() if i + 6 < len(lines) else ""
            next_i = i + 6

        # Case 2: 5-line transaction
        elif is_valid_amount(lines[i + 4]):
            description = lines[i + 3].strip()
            amount_str = lines[i + 4].strip()
            next_line = lines[i + 5].strip() if i + 5 < len(lines) else ""
            next_i = i + 6 if next_line == "-" else i + 5
        else:
            i += 1
            continue

        # Skip "PAYMENT FROM", but NOT refunds
        if "payment from" in description.lower():
            i = next_i
            continue

        # Parse amount (handle trailing minus)
        amount = parse_amount(amount_str, next_line)
        if amount is None:
            i = next_i
            continue

        # Only include if ref is a valid transaction ID (e.g. '001', '045')
        if re.match(r"^\d{3}$", ref):
            transactions.append({
                "ref": ref,
                "trans_date": trans_date,
                "post_date": post_date,
                "description": description,
                "amount": amount
            })

        i = next_i
    return transactions