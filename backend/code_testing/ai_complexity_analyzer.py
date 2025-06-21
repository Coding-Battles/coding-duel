import os
from groq import Groq

# Load API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def analyze_time_complexity_ai(code: str) -> str:
    """Analyze the time complexity of the provided code using Groq API."""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "If valid input, only return time complexity in big O notation. "
                        "Possible valid outputs: O(1), O(log n), O(n), O(n log n), O(n^2), O(n^3), O(2^n), O(n!), "
                        "or similar standard big O forms. Otherwise, return INVALID INPUT."
                    ),
                },
                {"role": "user", "content": code},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error analyzing code: {str(e)}")
