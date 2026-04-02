import httpx
import json
from core.config import settings
from core.logger import logger

class SwarmEngine:
    """
    Main Neural Swarm Engine using Groq Cloud (Llama 3.1 70B).
    Provides high-speed, zero-cost professional market reasoning.
    """
    def __init__(self):
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.api_key = settings.groq_api_key
        self.model = settings.llm_model

    async def get_consensus(self, seed_text: str) -> str:
        """Call Groq to perform a virtual agent simulation and return the final consensus report."""
        if not self.api_key:
            logger.warning("GROQ_API_KEY missing. Swarm falls back to synthetic logic.")
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Professional prompt for Multi-Agent Swarm Simulation
        system_prompt = (
            "You are a Collective Intelligence Engine. You simulate a swarm of 20 elite virtual analysts "
            "debating market conditions. Your output MUST be a single consensus report (approx 2 sentences) "
            "that identifies the most likely price direction based on technical indicators and institutional sentiment. "
            "Use professional terminal terminology. Be objective."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": seed_text}
            ],
            "temperature": 0.5,
            "max_tokens": 150
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    report = result["choices"][0]["message"]["content"]
                    return report.strip()
                else:
                    logger.error(f"Groq API Error: {resp.status_code} - {resp.text}")
                    return ""
        except Exception as e:
            logger.error(f"Swarm engine failure: {e}")
            return ""

swarm_engine = SwarmEngine()
