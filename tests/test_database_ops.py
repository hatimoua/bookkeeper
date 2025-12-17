from models import Account
from database import insert_account, get_account_by_code

def test_insert_and_retrieve_account(test_db):
    """
    Test that we can save an account and get it back.
    We pass 'test_db' argument to trigger the fixture, 
    even though we don't explicitly use the session object here.
    """
    
    # 1. Define a dummy account
    new_account = Account(
        code="9999",
        account_name="Test Account",
        financial_stat="P&L",
        group_name="Expenses",
        normally="Debit",
        description="A test account"
    )
    
    # 2. Run the function we are testing
    # Because of the fixture, this writes to RAM, not your real file.
    insert_account(new_account)
    
    # 3. Verify
    retrieved = get_account_by_code("9999")
    
    assert retrieved is not None
    assert retrieved.account_name == "Test Account"
    assert retrieved.code == "9999"