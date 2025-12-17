import math 
from typing import List, Tuple, Dict 
from models import Account, AccountSuggestion 
from database import get_account_by_code, load_all_account_embeddings
from openai import OpenAI
from dotenv import load_dotenv
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)    

# ===== TEXT PROCESSING =====
def get_account_text(account: Account) -> str:
    """
    Combine all the account fields into one long string.

    Args:
        account (Account): The account object containing various fields.

    Returns:
        str: A concatenated string of all account fields, separated by periods.
    """
    return (
    f"{account.account_name}."
    f"{account.code}."
    f"{account.financial_stat}."
    f"{account.group_name}."
    f"{account.normally}."
    f"{account.description}"
    )



#Sends text to OpenAI and gets back a list of numbers (the vector).
def embed_text(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text using OpenAI's embedding model.

    Args:
        text (str): The input text to be embedded.

    Returns:
        list[float]: A list of floating-point numbers representing the embedding vector.
    """
    embedding = client.embeddings.create(
        model = "text-embedding-3-small",
        input = text
    )
    return embedding.data[0].embedding



# ===== MATH FUNCTIONS =====

#Calculates how similar two lists of numbers are.

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    # 1. dot product
    dot = sum( a * b for a, b in zip(vec1, vec2))

    # 2. magnitudes
    mag1 = math.sqrt(sum( a**2 for a in vec1))
    mag2 = math.sqrt(sum( b**2 for b in vec2))

    # 3. avoid divide-by-zero
    if mag1 == 0 or mag2 == 0:
        return 0.0

    # 4. cosine similarity
    return dot / (mag1 * mag2)


# ===== SEARCH LOGIC =====

def find_top_k_account_codes(query_embedding: list[float], k: int = 5) -> List[Tuple[str, float]]:
    """
    The Search Engine Logic:
    1. Load all account vectors.
    2. Compare the query vector to every account vector.
    3. Sort by the highest score.
    4. Return the top k results.
    """
    # 1. Load all (code, embedding) pairs
    all_embeddings = load_all_account_embeddings()

    #2 prepare an empty list to collect (code, score)
    all_scores: List[Tuple[str, float]] = []

    # 3. Loop through each stored account embedding
    for code, emb in all_embeddings:
        score = cosine_similarity(query_embedding, emb)
        all_scores.append((code, score))

    # 4. Sort the scores in descending order
    all_scores.sort(key=lambda x: x[1], reverse=True)

    #5 take top k
    top_k_scores = all_scores[:k]
    return top_k_scores



def search_account(client, query_text: str):
    """
    Orchestrator function:
    1. Converts text -> Vector
    2. Finds best match (Math)
    3. Fetches details (Database)
    4. Returns a clean dictionary
    """
    # 1. Embed the query
    query_vector = embed_text(client, query_text)

    # 2. Get the top 1 result (returns a list like [('1000', 0.89)])
    results = find_top_k_account_codes(query_vector, k=1)

    # 3. Check if we found anything
    if not results:
        return None

    # 4. Unpack the first result from the list
    best_code, best_score = results[0]

    # 5. Get the full details
    account_details = get_account_by_code(best_code)

    # 6. Add the score to the details (useful for debugging confidence)
    if account_details:
        account_details['match_score'] = best_score

    return account_details


def retrieve_top_k_accounts(
    text_description: str,
    k: int = 5
    ) -> List[Dict]:
    """
    Given a transaction description, return the top-k matching accounts
    with their similarity scores and normality. 
    """

    # 1) Turn text into an embedding
    query_embedding = embed_text(text_description)

    # 2) Find top-k (code, score) pairs
    top_codes_and_scores = find_top_k_account_codes(
        query_embedding=query_embedding,
        k=k,
    )

    # 3) For each code, fetch account info and attach similarity
    results: List[Dict] = []

    for code, score in top_codes_and_scores:
        account_obj = get_account_by_code(code)  # Return Account object

        if account_obj is None:
            continue  # safety check

        # NEW: Convert to dictionary so we can add temporary fields
        account_info = account_obj.model_dump()
        
        # attach similarity
        account_info["similarity"] = score
        results.append(account_info)

    # 4) Normalize similarity values relative to the top score
    if results:
        top_score = results[0]["similarity"]
        for r in results:
            r["normalized_similarity"] = r["similarity"] / top_score

    return results

def suggest_accounts(
    text_description: str,
    k: int = 5
    ) -> List["AccountSuggestion"]:

    rows = retrieve_top_k_accounts(text_description, k=k)
    
    suggestions: List[AccountSuggestion] = []
    
    for row in rows:
        suggestions.append(AccountSuggestion(
        code=row["code"],
        account_name=row["account_name"],
        similarity=row["similarity"],
        normalized_similarity=row["normalized_similarity"],
            )
        )
    
    return suggestions


def format_suggestions_for_user(
    suggestions: List[AccountSuggestion], 
    confidence: str     
    ) -> str:
    
    if not suggestions:
        return "I could not find any matching accounts. Please choose one manually."

    other_count = len(suggestions) - 1

    if other_count == 0:
        extra = "There are no other suggestions."
    elif other_count == 1:
        extra = "There is 1 other suggestion."
    else:
        extra = f"There are {other_count} other suggestions."
    
    #Take the best suggestion
    best_suggestion = suggestions[0]
    formatted_suggestion = (
        f"{best_suggestion.account_name} with code {best_suggestion.code} "
        f"is the best suggestion. The confidence is {confidence}.{extra}"   
    )

    return formatted_suggestion 

def format_needs_review(
    suggestions: List[AccountSuggestion], 
    confidence: str     
    ) -> str:
    
    return "Confidence too low - Please review manually"
    
    

def grade_confidence(
    suggestions: List[AccountSuggestion]
    ) -> str :
    
    top_norm = suggestions[0].normalized_similarity
    
    if top_norm < 0.65:
        return "low"
    elif top_norm < 0.85:
        return "medium"
    else:
        return "high"







