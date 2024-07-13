from decimal import Decimal, ROUND_HALF_UP

def round_currency(amount: Decimal) -> Decimal:
    """
    Round the given amount to two decimal places using banker's rounding.
    """
    return amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

def calculate_split_amounts(total_amount: Decimal, split_type: str, split_details: dict) -> dict:
    """
    Calculate the split amounts based on the given split type and details.
    """
    if split_type == "equal":
        num_members = len(split_details)
        split_amount = round_currency(total_amount / num_members)
        return {member: split_amount for member in split_details}
    elif split_type == "percentage":
        return {member: round_currency(total_amount * Decimal(percentage) / 100) 
                for member, percentage in split_details.items()}
    elif split_type == "fixed":
        return {member: round_currency(Decimal(amount)) 
                for member, amount in split_details.items()}
    else:
        raise ValueError("Invalid split type")

def validate_split_details(total_amount: Decimal, split_type: str, split_details: dict) -> bool:
    """
    Validate the split details based on the split type and total amount.
    """
    if split_type == "equal":
        return len(set(split_details.values())) == 1
    elif split_type == "percentage":
        return sum(split_details.values()) == 100
    elif split_type == "fixed":
        return sum(Decimal(amount) for amount in split_details.values()) == total_amount
    else:
        return False

def simplify_debts(balances: dict) -> list:
    """
    Simplify the debts between group members.
    """
    balance_list = [(person, float(amount)) for person, amount in balances.items()]
    balance_list.sort(key=lambda x: x[1])
    
    transactions = []
    i, j = 0, len(balance_list) - 1
    
    while i < j:
        debtor, debt = balance_list[i]
        creditor, credit = balance_list[j]
        
        if abs(debt) < credit:
            transactions.append((debtor, creditor, abs(debt)))
            balance_list[j] = (creditor, credit + debt)
            i += 1
        elif abs(debt) > credit:
            transactions.append((debtor, creditor, credit))
            balance_list[i] = (debtor, debt + credit)
            j -= 1
        else:
            transactions.append((debtor, creditor, credit))
            i += 1
            j -= 1
    
    return transactions