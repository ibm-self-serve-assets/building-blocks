from pydantic import BaseModel, Field
from typing import Optional, List

class queryRequest(BaseModel):
    query: str = Field(title="SQL Query", description="SQL Query")
    dbtype: str = Field(title="Database Type", description="Database Type for Text To SQL. Options: MYSQL, MONGODB, DB2")