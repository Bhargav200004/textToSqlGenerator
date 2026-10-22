import sqlglot
from dataclasses import dataclass
from app.services.schema import SchemaService

BLOCKED_KEYWORDS = {"DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER", "TRUNCATE"}

@dataclass
class ValidationResult:
    valid: bool
    error: str | None = None

class SQLValidator:
    def __init__(self, schema_service: SchemaService):
        self.schema = schema_service

    def validate(self, sql: str, table_names: list[str]) -> ValidationResult:
        if not sql:
            return ValidationResult(valid=False, error="Empty SQL returned")
        tokens = sql.upper().split()
        for kw in BLOCKED_KEYWORDS:
            if kw in tokens:
                return ValidationResult(valid=False, error=f"Blocked keyword found: {kw}")
        try:
            statements = sqlglot.parse(sql)
            if not statements:
                return ValidationResult(valid=False, error="Could not parse SQL")
        except Exception as e:
            return ValidationResult(valid=False, error=f"Syntax error: {e}")
        for table_name in table_names:
            if table_name not in self.schema.registry:
                return ValidationResult(valid=False, error=f"Table not found in schema: {table_name}")
        return ValidationResult(valid=True)