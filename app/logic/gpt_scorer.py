import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# It's better to handle the case where the API key might not be set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=api_key)

def score_article(article: Dict) -> float:
    """
    Scores an article based on its relevance using the OpenAI API.

    Args:
        article: A dictionary representing the article.

    Returns:
        A relevance score between 0.0 and 1.0.
    """
    try:
        prompt = f"""Please rate the relevance of the following news article on a scale from 0.0 to 1.0. 
        Consider factors like global significance, impact, and general interest. 
        Only return a single floating-point number.

        Title: {article['title']}
        Summary: {article['summary']}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rates news articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=5
        )

        score_text = response.choices[0].message.content.strip()
        return float(score_text)

    except Exception as e:
        print(f"Error scoring article with OpenAI: {e}")
        return 0.0 # Return a default low score on error

if __name__ == '__main__':
    # For testing purposes
    sample_article = {
        "title": "Global leaders meet to discuss climate change",
        "summary": "Leaders from around the world are gathering for a summit to address the urgent issue of climate change and discuss potential solutions."
    }
    score = score_article(sample_article)
    print(f"Article Score: {score}")
