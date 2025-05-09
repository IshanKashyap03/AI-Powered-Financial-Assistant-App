import React, {useRef, useState} from 'react';
import { uploadFile } from '../../services/api';
import Button from '../../components/Button';
import './UploadForm.css';

const UploadForm = () => {
    const [income, setIncome] = useState(0);
    const [withdrawals, setWithdrawals] = useState(0);
    const [savings, setSavings] = useState(0);
    const [advice, setAdvice] = useState('');
    const [debitTransactions, setDebitTransactions] = useState([]);
    const [creditTransactions, setCreditTransactions] = useState([]);
    const [categorized, setCategorized] = useState('');

    const fetchGPTAdvice = async (income, withdrawals, savings) => {
      const res = await fetch('/api/v1/insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ income, withdrawals, savings })
      });
      const data = await res.json();
      setAdvice(data.advice);
    }

    const categorizeTransactions = async (debit_transactions, credit_transactions) => {
      const res = await fetch('/api/v1/categorize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          debit_transactions,
          credit_transactions
        })
      });
      const data = await res.json();
      console.log(data);
      setCategorized(data.categorized_transactions);
    }

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
            setDebitTransactions(data.debit_transactions);
            setCreditTransactions(data.credit_transactions);
            await fetchGPTAdvice(data.total_income, data.total_withdrawals, data.net_savings);
            await categorizeTransactions(data.debit_transactions, data.credit_transactions);
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
            <div className='advice-container'>
              {advice && (
                <div className="advice-box box-1">
                  <h3>AI Financial Advice</h3>
                  <div dangerouslySetInnerHTML={{ __html: advice }} />
                </div>
              )}

              {categorized && (
                <div className="advice-box box-2">
                  <h3>Transaction Categories</h3>
                  {Object.entries(categorized).map(([category, amount]) => (
                    <p key={category}><strong>{category}:</strong> ${amount.toFixed(2)}</p>
                  ))}
                </div>
              )}
            </div>
        </div>
      );
}

export default UploadForm;

