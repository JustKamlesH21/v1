from typing import List, Dict, Any


class DBConnector:
    """A minimal database connector wrapper that lazily imports SQLAlchemy.

    This avoids import-time failures when SQLAlchemy isn't installed in the
    test environment. Attempting to actually connect will raise a clear
    ImportError instructing the developer to install dependencies.
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None

    def get_engine(self):
        try:
            from sqlalchemy import create_engine  # type: ignore
        except Exception as e:  # pragma: no cover - dev dependency missing
            raise ImportError(
                "SQLAlchemy is required to use DBConnector. Install it with `pip install sqlalchemy`."
            ) from e
        self.engine = create_engine(self.db_url)
        return self.engine

    def get_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            from sqlalchemy import inspect  # type: ignore
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "SQLAlchemy is required to inspect schemas. Install it with `pip install sqlalchemy`."
            ) from e

        if self.engine is None:
            self.get_engine()

        inspector = inspect(self.engine)
        schema: Dict[str, List[Dict[str, Any]]] = {}
        for table_name in inspector.get_table_names():
            schema[table_name] = []
            for column in inspector.get_columns(table_name):
                schema[table_name].append(
                    {
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column.get("nullable"),
                        "default": column.get("default"),
                        "primary_key": column.get("primary_key"),
                    }
                )
        return schema