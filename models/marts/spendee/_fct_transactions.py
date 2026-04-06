from models.intermediate.spendee._int_spendee__transactions import int_spendee__transactions

def fct_transactions():
    """
    Fact table for transactions. 
    Now simply calls the intermediate model to maintain the standard pipeline flow.
    """
    return int_spendee__transactions()