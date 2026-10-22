def build_table_selection_prompt(question: str, all_tables: list[str]) -> str:
    table_list = "\n".join(f"- {t}" for t in all_tables)
    return f"""You are helping select relevant database tables for a SQL query.

    Available tables:
    {table_list}

    User question: "{question}"

    Return ONLY the names of relevant tables as a comma-separated list.
    Include a table if it might contain data needed to answer the question.
    If no tables are relevant, return NONE.

    Respond in EXACTLY this format:
    TABLES: table1, table2"""