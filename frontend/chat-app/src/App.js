// App.js
import React, { useState } from 'react';
import axios from 'axios';
import './style.css';

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');

  const handleFileChange = (event) => {
    setPdfFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (pdfFile) {
      const formData = new FormData();
      formData.append('file', pdfFile);

      try {
        // Upload PDF file to the backend
        await axios.post('http://localhost:8000/upload_pdf/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        alert(`PDF uploaded successfully: ${pdfFile.name}`);
      } catch (error) {
        console.error('Error uploading PDF:', error);
        alert('Error uploading PDF');
      }
    }
  };

  const handleQuestionSubmit = async () => {
    if (pdfFile && question) {
      const formData = new FormData();
      formData.append('file', pdfFile);
      formData.append('question', question); // Fix: 'query' to 'question'

      try {
        // Ask a question about the uploaded PDF
        const res = await axios.post('http://localhost:8000/ask_question/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        setResponse(res.data.answer); // Fix: 'response' to 'answer'
      } catch (error) {
        console.error('Error asking question:', error);
        alert('Error asking question');
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF Question Answering</h1>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload PDF</button>
        <br />
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
        />
        <button onClick={handleQuestionSubmit}>Ask</button>
        <br />
        {response && <div className="response"><strong>Response:</strong> {response}</div>}
      </header>
    </div>
  );
}

export default App;
