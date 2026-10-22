def build_clarification_prompt(
    question: str,
    schema_text: str
) -> str:
    return f"""You are helping a user query a database.
            Decide if their question needs clarification before writing SQL.

            Database schema:
            {schema_text}

            User question: "{question}"

            A question needs clarification when a critical filter is missing that would
            cause SQL to return meaningless or overwhelming results.
            Examples: no date range on time-series data, no status when multiple exist.

            Do NOT ask for clarification if:
            - The question asks for all records intentionally
            - The schema has only one sensible interpretation

            Respond in EXACTLY this format:
            NEEDS_CLARIFICATION: yes or no
            QUESTION: one specific question to ask the user, or NONE"""