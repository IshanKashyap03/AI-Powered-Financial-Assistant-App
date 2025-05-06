from fastapi import FastAPI, UploadFile, File
import fitz
from io import BytesIO
from utils.pdf_parser import extract_debit_totals, extract_credit_totals

app = FastAPI()

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

    debit_deposits, debit_withdrawals = extract_debit_totals(debit_text)
    credit_withdrawals = extract_credit_totals(credit_text)

    deposits = debit_deposits
    withdrawals = debit_withdrawals + credit_withdrawals
    net_savings = deposits - withdrawals

    return {
        "total_income": deposits,
        "total_withdrawals": withdrawals,
        "net_savings": net_savings
    }

