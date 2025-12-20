from typing import List
from models import InvoiceLine, Invoice
from query import suggest_accounts, grade_confidence

def invoice_to_description(invoice: Invoice) -> str:
    """ Turn a structured Invoice into a single text description 
    that can be used to suggest_accounts().
    """
    line_summaries : List[str] = []
    for line in invoice.lines: 
        line_summaries.append(line.description)

    lines_text = "; ".join(line_summaries)

    description = (
        f"Invoice from {invoice.vendor} on {invoice.invoice_date}. "
        f"Total: {invoice.total_amount} {invoice.currency}. "
        f"Lines: {lines_text}"
    )
    return description

def needs_manual_review(invoice: Invoice, confidence: str) -> bool:

    if invoice.total_amount > 1000:
        return True
    
    vendor = invoice.vendor.lower() 
    if "cra" in vendor or "revenu" in vendor:
        return True

    if confidence == "high" or confidence == "medium":
        return False
    
    return False