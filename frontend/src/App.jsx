import { useState } from "react";
import "./App.css";
import ReactMarkdown from 'react-markdown';

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(""); // GPT answer
  const [docIds, setDocIds] = useState([]);

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setDocIds([]); // clear old doc ids


    try {
      const response = await fetch("http://127.0.0.1:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: question }),
      });

      const data = await response.json();
      console.log("Response from backend:", data);

      if (data.ok) {
        if (data.gpt_answer) {
          setAnswer(data.gpt_answer); // show GPT answer
        }
        if (data.source_docs) {
  setDocIds(data.source_docs);
}
      } else {
        setAnswer("No answer found.");
      }
    } catch (error) {
      console.error("Error sending query:", error);
      setAnswer("Error: Could not retrieve answer.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion("");
    setAnswer("");
    setDocId("");
  };

  return (
    <div className="container">
      {/* Logo */}
      <img
        className="logo"
        src="https://emcos.com/wp-content/themes/EMC/img/logo.png"
        alt="EMCoS Logo"
      />

      {/* Search Bar */}
      <form className="search-bar search-bar-icon" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Type Your Question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          autoComplete="new-password"
          disabled={loading}
        />

        {/* Clear button */}
        {(question || answer) && (
          <button
            type="button"
            className="clear-btn"
            onClick={handleClear}
            aria-label="Clear"
          >
            ×
          </button>
        )}

        <span className="search-icon-separator"></span>

        {/* Search button */}
        <button
          type="submit"
          className="search-icon-btn"
          disabled={loading || !question.trim()}
          tabIndex={-1}
          aria-label="Ask"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#b0b0b0"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </button>
      </form>

      {/* Answer box */}
      {(loading || answer || docIds.length > 0) && (
  <div className="answer-box">
    {loading ? (
      <p>Loading...</p>
    ) : (
      <>
        <ReactMarkdown>{answer}</ReactMarkdown>
        {docIds.length > 0 && (
          <div style={{ marginTop: '8px' }}>
            <strong>Source Documents:</strong>
            <ul>
              {docIds.map((id, index) => (
                <li key={index} style={{ wordBreak: "break-all" }}>
                  {id}
                </li>
              ))}
            </ul>
          </div>
        )}
      </>
    )}
  </div>
)}

    </div>
  );
}

export default App;
