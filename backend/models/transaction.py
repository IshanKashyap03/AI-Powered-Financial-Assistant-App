from pydantic import BaseModel

class Transaction(BaseModel):
    description: str
    amount: float