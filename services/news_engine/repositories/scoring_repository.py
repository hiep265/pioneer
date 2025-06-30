# scoring_repository.py
import os, json, re
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ScoringRepository:
    """
    • relevance (0-1)   – mức liên quan keywords
    • sensational (0-1) – mức giật gân
    Điểm cuối  = 0.6*sensational + 0.4*relevance
    Trả về (score, reason)
    """

    _SYS_PROMPT = (
        "You are a senior news editor.  For every article you receive, do ALL of:\n"
        "1. Rate **relevance** to the provided topic keywords on a scale 0.0-1.0.\n"
        "2. Rate **sensational / eye-catching quality** of headline+summary on 0.0-1.0.\n"
        "3. Give a **one-sentence reason** (8-25 words) explaining your ratings – mention *why* it is or isn't relevant AND what makes it sensational or not.\n"
        "\n"
        "⚠️ Respond with COMPACT JSON on ONE line, NO markdown fences.\n"
        'Format EXACTLY: {"relevance":<float>,"sensational":<float>,"reason":"<one sentence>"}\n'
        "Example output:\n"
        '{"relevance":0.85,"sensational":0.90,"reason":"Mentions Trump tariffs directly and uses dramatic wording, making it highly relevant and sensational."}'
    )

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    # --------------------------- public ---------------------------
    def get_score(
        self,
        article: Dict,
        keywords: List[str] | None = None,
    ) -> Tuple[float, str]:
        try:
            analysis = self._ask_llm(
                title=article["title"],
                summary=article["summary"],
                keywords=keywords or [],
            )
            rel  = float(analysis.get("relevance", 0))
            sens = float(analysis.get("sensational", 0))
            score = 0.6 * sens + 0.4 * rel
            return score, analysis.get("reason", "no reason")
        except Exception as e:
            print(f"[ScoringRepository] {e}")
            return 0.0, "scoring failed"

    # --------------------------- private --------------------------
    def _ask_llm(self, title: str, summary: str, keywords: List[str]) -> Dict:
        user_prompt = (
            f"Topic keywords: {', '.join(keywords) if keywords else 'N/A'}\n"
            f"Title: {title}\nSummary: {summary}"
        )

        rsp = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._SYS_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=120,
        )

        raw = rsp.choices[0].message.content.strip()

        # ‼️ bóc ```json … ```
        cleaned = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # fallback: trích số & ghi reason
            nums = list(map(float, re.findall(r"\d\.\d+", cleaned)))
            return {
                "relevance": nums[0] if len(nums) > 0 else 0.0,
                "sensational": nums[1] if len(nums) > 1 else 0.0,
                "reason": "LLM returned malformed JSON",
            }
