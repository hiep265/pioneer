import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class ScoringRepository:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=api_key)

    def get_score(self, article: Dict) -> float:
        try:
            prompt = f"""Please rate the relevance of the following news article on a scale from 0.0 to 1.0. 
            Consider factors like global significance, impact, and general interest. 
            Only return a single floating-point number.

            Title: {article['title']}
            Summary: {article['summary']}
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
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
            return 0.0
