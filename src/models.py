from pydantic import BaseModel
from typing import List, Dict, Optional


"""# ==========================================
# 2. DATA MODELS
# ==========================================
"""

class Account(BaseModel):
  """
  This is a Pydantic model. Think of it as a strict form validator.
  If you try to create an Account without a 'code', this will error out
  immediately, saving you from bugs later.
  """

  account_name: str           # e.g. "Travel Expenses"
  code: str                   # e.g. "5400"
  financial_stat: str         # e.g. "Balance Sheet"
  group_name: str             # e.g. "Current Assets" or "Long-Term Assets" or "Cost Of Sales"
  normally: str               # e.g. "Debit" or "Credit"
  description: str            # optional description of the account


class AccountSuggestion(BaseModel):
  code: str  
  account_name: str
  similarity: float
  normalized_similarity: float


class InvoiceLine(BaseModel):
    description: str
    amount: float 

class Invoice(BaseModel):
    vendor: str
    invoice_date: str
    total_amount: float 
    currency: str 
    tax: float 
    lines: List[InvoiceLine]





    