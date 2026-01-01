import os
import json
import requests
from config import settings
from bookkeeper.models import Invoice
from bookkeeper.invoices import invoice_to_description
from bookkeeper.agent_graph import create_graph


class LandingAIClient:
    """
    A client for interacting with the Landing AI API to parse and extract structured data from documents.

    This class provides methods to:
    - Parse a document (e.g., PDF) and retrieve its markdown representation.
    - Extract structured data from the parsed markdown using a predefined schema.

    Attributes:
        api_key (str): The API key for authenticating requests to the Landing AI API.
        base_url (str): The base URL for the Landing AI API endpoints.
        invoice_schema (dict): The JSON schema used for extracting structured data from invoices.

    Methods:
        ade_parse(file_path: str) -> str:
            Parses a document and returns its markdown representation.
        ade_extract(markdown_text: str) -> dict:
            Extracts structured data from a markdown representation.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.va.landing.ai"):
        """
        Initialize the LandingAIClient with the provided API key and base URL.

        Args:
            api_key (str): The API key for authenticating requests to the Landing AI API.
            base_url (str): The base URL for the Landing AI API endpoints. Defaults to "https://api.va.landing.ai".
        """
        self.api_key = settings.LANDING_AI_API_KEY
        self.base_url = base_url
        
        self.invoice_schema = {
            "type": "object",
            "properties": {
                "vendor": {"type": "string"},
                "invoice_date": {"type": "string"},
                "total_amount": {"type": "number"},
                "currency": {"type": "string"},
                "tax": {"type": "number"},
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "amount": {"type": "number"},
                        },
                        "required": ["description", "amount"],
                    },
                },
            },
            "required": ["vendor", "invoice_date", "total_amount", "currency", "tax", "lines"],
        }
    
    def _headers(self) -> dict:
        """
        Generate the headers required for API requests.

        Returns:
            dict: A dictionary containing the authorization header with the API key.
        """
        return {"Authorization": f"Bearer {self.api_key}"}
    
    def ade_parse(self, file_path: str) -> str:
        """
        Parse a document using the Landing AI API and return its markdown representation.

        Args:
            file_path (str): The path to the document file to be parsed.

        Returns:
            str: The markdown representation of the parsed document.

        Raises:
            RuntimeError: If no markdown is found in the API response.
            requests.exceptions.RequestException: If the HTTP request fails.
        """
        url = f"{self.base_url}/v1/ade/parse"
        headers = self._headers()
        
        with open(file_path, "rb") as f:
            files ={"document": f}
            response = requests.post(url, headers=headers, files=files, timeout=120)
            response.raise_for_status()
            payload = response.json()
            markdown = (payload.get("data") or {}).get("markdown") or payload.get("markdown")
            if not markdown:
                raise RuntimeError(f"No markdown found in response keys={list(payload.keys())}")
            return markdown
            
    
    def ade_extract(self, markdown_text: str) -> dict:
        """
        Extract structured data from a markdown representation using the Landing AI API.

        Args:
            markdown_text (str): The markdown text to be processed.

        Returns:
            dict: The extracted structured data as a dictionary.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
        """
        url = f"{self.base_url}/v1/ade/extract"
        headers = self._headers()
        
        data = {"schema": json.dumps(self.invoice_schema),
                "model": "extract-latest"}
        
        files = {
            "markdown": ("document.md", markdown_text.encode("utf-8"), "text/markdown"),
        }
        
        response = requests.post(url, headers=headers, data=data, files=files, timeout=120)
        response.raise_for_status()
        payload = response.json()
        
        return payload




