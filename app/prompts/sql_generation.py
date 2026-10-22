def build_sql_generation_prompt(
    question: str,
    schema_text: str,
    clarifications: list[dict] | None = None,
    validation_error: str | None = None
) -> str:
    clarification_block = ""
    if clarifications:
        lines = [f"Q: {c['question']}\nA: {c['answer']}" for c in clarifications]
        clarification_block = "\nClarifications from user:\n" + "\n".join(lines)

    error_block = ""
    if validation_error:
        error_block = f"\nPrevious SQL failed validation: {validation_error}\nPlease fix this error."

    return f"""You are a SQL expert. Generate a valid SQL SELECT query.

    Database schema:
    {schema_text}
    {clarification_block}
    {error_block}
    User question: "{question}"

    Rules:
    - Only use tables and columns listed in the schema above
    - Only generate SELECT statements — no INSERT, UPDATE, DELETE, DROP, CREATE
    - If the question cannot be answered from the schema, say so clearly

    Respond in EXACTLY this format:
    SQL: <your query here>
    EXPLANATION: <one sentence describing what the query returns>"""


#  - Only generate SELECT statements — no INSERT, UPDATE, DELETE, DROP, CREATE