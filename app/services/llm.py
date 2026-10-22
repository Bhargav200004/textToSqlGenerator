
from app.prompts.clarification import build_clarification_prompt
from app.prompts.sql_generation import build_sql_generation_prompt
from app.models.prompt_type import PROMPT_TYPE
from loguru import logger
from app.prompts.table_selection import build_table_selection_prompt
import httpx
from app.config import Settings


class LLMService:
    def __init__(self, config: Settings):
        self.ollama_url = config.ollama_url
        self.model = config.model_name


    async def generate(self, prompt_type: PROMPT_TYPE , context : dict) -> str:
        if prompt_type == PROMPT_TYPE.TABLE_SELECTION:
            prompt = build_table_selection_prompt(context["question"],context["all_tables"])
        elif prompt_type == PROMPT_TYPE.CLARIFICATION:
            prompt = build_clarification_prompt(context["question"], context["schema"])
        elif prompt_type == PROMPT_TYPE.SQL_GENERATION:
            prompt = build_sql_generation_prompt(
                question=context["question"],
                schema_text=context["schema"],
                clarifications=context.get("clarifications"),
                validation_error=context.get("validation_error")
            )
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}") 
        
        return await self._call_ollama(prompt)


    async def _call_ollama(self, prompt : str) -> str:
        logger.debug(self.ollama_url)
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.ollama_url,
                json={
                    "model": "local-model",
                    "messages" : [{
                        "role": "user",
                        "content" : prompt }]
                }
            )
            response.raise_for_status()
            data = response.json()["choices"][0]["message"]["content"]
            return data