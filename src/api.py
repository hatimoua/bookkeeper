from fastapi import FastAPI, UploadFile, File
import tempfile
import os
from client_landingai import LandingAIClient
from models import Invoice

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/classify-invoice")
def classify_invoice(file: UploadFile = File(...)):
    # 1) Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        # 2) Create client
        client = LandingAIClient(
            api_key=os.environ["LANDING_AI_API_KEY"],
            base_url="https://api.va.landing.ai",
        )

        # 3) Call LandingAI
        markdown = client.ade_parse(tmp_path)
        extraction = client.ade_extract(markdown)

        # 4) Build Invoice
        invoice = Invoice(**extraction["extraction"])

        return {
            "invoice": invoice.model_dump(),
        }

    finally:
        # 5) Cleanup temp file
        os.remove(tmp_path)


