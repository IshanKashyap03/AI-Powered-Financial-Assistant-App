from fastapi import FastAPI, UploadFile, File
import fitz
from io import BytesIO
from utils.pdf_parser import extract_debit_totals, extract_credit_totals
from fastapi import APIRouter
import openai
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from services.transactions import parse_debit_transactions
from services.transactions import parse_credit_transactions
from models.categorization import CategorizeRequest
import re


load_dotenv()
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/api/v1")
def root():
    return {"message": "Backend is working!"}

@app.post("/api/v1/upload")
async def upload_file(debitCardFile: UploadFile = File(...), creditCardFile: UploadFile = File(...)):
    debitCardFileContent = await debitCardFile.read()
    creditCardFileContent = await creditCardFile.read()

    try:
        debitPdf = fitz.open(stream=debitCardFileContent, filetype="pdf")
        creditPdf = fitz.open(stream=creditCardFileContent, filetype="pdf")
    except Exception as e:
        return {"error": f"Failed to read PDFs: {str(e)}"}

    debit_text = "\n".join([page.get_text() for page in debitPdf])
    credit_text = "\n".join([page.get_text() for page in creditPdf])

    debit_transactions = parse_debit_transactions(debit_text)
    credit_transactions = parse_credit_transactions(credit_text)

    debit_deposits, debit_withdrawals = extract_debit_totals(debit_text)
    credit_withdrawals, credit_payments = extract_credit_totals(credit_text)

    deposits = debit_deposits
    withdrawals = debit_withdrawals + credit_withdrawals - credit_payments
    net_savings = deposits - withdrawals

    return {
        "total_income": deposits,
        "total_withdrawals": withdrawals,
        "net_savings": net_savings,
        "debit_transactions": debit_transactions,
        "credit_transactions": credit_transactions
    }

@app.post("/api/v1/insights")
async def generate_financial_insights(data: dict):
    income = data.get("income")
    withdrawals = data.get("withdrawals")
    savings = data.get("savings")

    prompt = (
        f"A user uploaded their bank statements.\n"
        f"Here is their monthly summary:\n"
        f"- Total Income: ${income:.2f}\n"
        f"- Total Spending: ${withdrawals:.2f}\n"
        f"- Net Savings: ${savings:.2f}\n\n"
        f"Based on common budgeting principles (like the 50/30/20 rule or personalized advice), "
        f"tell the user:\n"
        f"1. Whether their current split is healthy or not.\n"
        f"2. What an ideal breakdown of income vs spending vs savings could be for them.\n"
        f"3. Provide 2–3 helpful, specific financial tips to improve their budget.\n"
        f"Respond like a friendly financial assistant."
        f"Return the advice as raw HTML only (no markdown, no code block, no triple backticks). "
        f"Use <h4>, <ul>, <li>, and <p> for structure."
    )
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
        ]
    )   

    return {"advice": response.choices[0].message.content}

@app.post("/api/v1/categorize")
async def categorize_expenses(data: CategorizeRequest):
    descriptions = [txn.description for txn in data.debit_transactions + data.credit_transactions]
    
    prompt = (
        "Categorize the following bank transactions. Respond only with a JSON object mapping categories to total amounts. "
        "Use categories: Food & Dining, Transportation, Shopping, Fitness & Wellness, Entertainment, Utilities, "
        "Subscription, Healthcare, Insurance, Investment, Withdrawal, Refund and Other.\n\n"
        "Transactions:\n" +
        "\n".join([f"- {txn.description}: ${txn.amount}" for txn in data.debit_transactions + data.credit_transactions])
    )
    

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

     # Extract JSON block from GPT response
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            categories = json.loads(match.group(1))
            return {"categorized_transactions": categories}
        except Exception as e:
            return {"error": "Failed to parse extracted JSON", "raw": match.group(1)}
    else:
        return {"error": "Failed to parse GPT response", "raw": raw_content}
