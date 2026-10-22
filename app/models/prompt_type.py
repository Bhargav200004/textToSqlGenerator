from enum import Enum

class PROMPT_TYPE(str , Enum):
    TABLE_SELECTION = "table_selection"
    CLARIFICATION = "clarification"
    SQL_GENERATION = "sql_generation"

