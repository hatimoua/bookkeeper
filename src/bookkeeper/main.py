from bookkeeper.invoices import invoice_to_description
from bookkeeper.models import Invoice, InvoiceLine
from bookkeeper.query import suggest_accounts, format_suggestions_for_user, grade_confidence


if __name__ == "__main__":
    invoice = Invoice(
        vendor="lunch",
        invoice_date="2023-01-01",
        total_amount=100,
        currency="USD",
        tax=10,
        lines=[
            InvoiceLine(description="Lunch at restaurant with a client", amount=100),
        ],
    )

text = invoice_to_description(invoice)
print("Generated description:", text)

confidence_score = "high"
suggestions = suggest_accounts(text, k=5)
print("Suggestions:")
for s in suggestions:
    print(f"{s.code}: {s.account_name} (similarity: {s.normalized_similarity:.2f})")
    print("Confidence:", grade_confidence(suggestions))
print("Final answer:", format_suggestions_for_user(suggestions, confidence_score))