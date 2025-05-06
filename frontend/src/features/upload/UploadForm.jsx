import React, {useRef, useState} from 'react';
import { uploadFile } from '../../services/api';
import Button from '../../components/Button';
import './UploadForm.css';

const UploadForm = () => {
    const[income, setIncome] = useState(0);
    const[withdrawals, setWithdrawals] = useState(0);
    const[savings, setSavings] = useState(0);

    const debitFile = useRef();
    const creditFile = useRef();

    const handleUpload = async () => {
        const debitCardFile = debitFile.current?.files[0];
        const creditCardFile = creditFile.current?.files[0];
        if (!debitCardFile) return alert("Please select the debit card statement file.");
        if (!creditCardFile) return alert("Please select the credit card statement file.");

        const formData = new FormData();
        formData.append('debitCardFile', debitCardFile);
        formData.append('creditCardFile', creditCardFile);

        try {
            const data = await uploadFile(formData);
            setIncome(data.total_income);
            setWithdrawals(data.total_withdrawals);
            setSavings(data.net_savings);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    }

    return (
        <div className="upload-form">
          <h2>Upload Your Bank Statements</h2>
          <div className="statement-container">
            <div className="statement-box">
              <label htmlFor="debit">Debit Card Statement</label>
              <input id="debit" type="file" ref={debitFile} accept=".pdf" />
            </div>
            <div className="statement-box">
              <label htmlFor="credit">Credit Card Statement</label>
              <input id="credit" type="file" ref={creditFile} accept=".pdf" />
            </div>
          </div>
          <Button onClick={handleUpload} className="analyze-btn">
            Analyze
          </Button>

          {income !== null && income !== undefined &&
            withdrawals !== null && withdrawals !== undefined &&
            savings !== null && savings !== undefined && (
              <div className="summary">
                <h3>Monthly Summary</h3>
                <p><strong>Total Income:</strong> ${income.toFixed(2)}</p>
                <p><strong>Total Spending:</strong> ${withdrawals.toFixed(2)}</p>
                <p><strong>Net Savings:</strong> ${savings.toFixed(2)}</p>
              </div>
            )}
        </div>
      );
}

export default UploadForm;

