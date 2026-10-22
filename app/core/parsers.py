def parse_table_list(raw: str) -> list[str]:
    for line in raw.strip().splitlines():
        if line.upper().startswith("TABLES:"):
            value = line.split(":" , 1)[1].strip()
            if value.upper() == "NONE":
                return[]
            return [t.strip() for t in value.split(",") if t.strip()]
    return []


def parse_sql_response(raw: str) -> tuple[str | None, str | None]:
    sql, explanation = None, None
    for line in raw.strip().splitlines():
        if line.upper().startswith("SQL:"):
            sql = line.split(":", 1)[1].strip()
        elif line.upper().startswith("EXPLANATION:"):
            explanation = line.split(":", 1)[1].strip()
    return sql, explanation



