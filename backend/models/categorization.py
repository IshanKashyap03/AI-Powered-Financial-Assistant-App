from pydantic import BaseModel
from typing import List
from models.transaction import Transaction

class CategorizeRequest(BaseModel):
    debit_transactions: List[Transaction]
    credit_transactions: List[Transaction]