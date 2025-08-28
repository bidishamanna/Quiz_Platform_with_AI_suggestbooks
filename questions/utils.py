import json
import re
from google import genai
from django.conf import settings

def get_books_from_ai(subject_name, max_books=5):
    """
    Fetch book suggestions from Gemini AI based on the subject.
    Returns a list of dictionaries:
    [{"title": ..., "price": ..., "rating": ..., "description": ...}, ...]
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Improved prompt to enforce clean JSON output
    prompt = f"""
    You are an API. Respond ONLY with a valid JSON array.

    Suggest {max_books} books for the subject "{subject_name}".
    Each book must include: title, price (USD), rating (out of 5), and a short description.

    Format:
    [
      {{
        "title": "Book Title",
        "price": 19.99,
        "rating": 4.5,
        "description": "Short description here"
      }},
      ...
    ]
    """

    try:
        # Request Gemini to generate content
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Debug print to inspect raw Gemini response
        print("Raw Gemini response:", response.text)

        # Extract JSON array from response using regex
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            json_data = match.group()
            books = json.loads(json_data)

            # Validate that we got a list of dictionaries
            if not isinstance(books, list) or not all(isinstance(b, dict) for b in books):
                raise ValueError("Parsed data is not a valid list of dictionaries")

        else:
            raise ValueError("No JSON array found in Gemini response")

    except Exception as e:
        print(f"Error fetching books from AI: {e}")
        books = []  # Fallback to empty list if something goes wrong

    return books
