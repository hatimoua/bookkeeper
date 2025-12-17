import csv
from models import Account
from database import init_db, insert_account, clear_database, insert_account_embedding, load_all_account_embeddings, get_all_accounts, get_account_by_code
from query import get_account_text, embed_text


def import_coa_from_csv(csv_path: str):
    """Read CSV and insert accounts one by one."""
    print(f"Reading from {csv_path}...")
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # 1. Create the Pydantic Object (The "Nail")
            account = Account(
                account_name=row["Account Name"],
                code=row["Code"],
                financial_stat=row["Financial Statement"],
                group_name=row["Group"],
                normally=row["Normally"],
                description=row["Description"],
            )
            
            # 2. Use the Tool (The "Hammer")
            insert_account(account)
            count += 1
            
    print(f"✅ Imported {count} accounts.")


def embed_all_accounts():
    """Generate and store embeddings for all accounts in the database."""
    accounts = get_all_accounts()
    print(f"Generating embeddings for {len(accounts)} accounts...")

    for acc in accounts:
        text = get_account_text(acc)
        vector = embed_text(text)
        insert_account_embedding(acc.code, vector)

    print("✅ All account embeddings generated and stored.")


def clear_and_setup():
    print("========Setting up the database========")
    init_db()
    print("========Clearing existing data========")
    clear_database()
    print("========Importing Chart of Accounts from CSV========")
    # This function handles the looping and inserting internally
    import_coa_from_csv("data/coav2.csv")
    print("========Generating and storing embeddings========")
    # This function handles the AI work and saving internally
    embed_all_accounts()
    
    print("========Setup Complete========")
    

if __name__ == "__main__":
    clear_and_setup()
