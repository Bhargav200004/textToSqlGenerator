import yaml
from pathlib import Path
from app.models.domain import TableMeta, ColumnMeta

class SchemaService:
    def __init__(self, schema_path: str):
        self.schema_path = schema_path
        self.registry: dict[str , TableMeta] = {}


    def load(self):
        path = Path(self.schema_path)
        with open(path) as f:
            raw_yaml_file = yaml.safe_load(f)

        for table_name, table_data in raw_yaml_file.items():
            columns = [
                ColumnMeta(
                    name = col_name,
                    type=col_data.get("type" , "TEXT"),
                    nullable=col_data.get("nullable", True),
                    description=col_data.get("description", ""),
                    primary_key=col_data.get("primary_key", False)
                )
                for col_name, col_data in table_data.get("columns", {}).items()
            ]

            self.registry[table_name] = TableMeta(
                name=table_name,
                description=table_data.get("description", ""),
                columns=columns,
                foreign_key=[
                    c["fk"].split(".")[0]
                    for c in table_data.get("columns", {}).values()
                    if c.get("fk")
                ]
            )


    def get_schema_text(self, table_name : list[str]) -> str:
        lines = []
        for name in table_name:
            meta = self.registry.get(name)
            if meta:
                header = f"Table: {name} — {meta.description}" if meta.description else f"Table: {name}"
                lines.append(header)
                for col in meta.columns:
                    pk = " [PK]" if col.primary_key else ""
                    desc = f" - {col.description}" if col.description else ""
                    lines.append(f"  - {col.name} ({col.type}){pk}{desc}")
        return "\n".join(lines)


    def get_all_table_names(self) -> list[str]:
        return list(self.registry.keys())

    