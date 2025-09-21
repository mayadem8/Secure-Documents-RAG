import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
  e.preventDefault();
  if (!question.trim()) return;

  setLoading(true);

  try {
    // Send query to Flask backend
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: question }), // send as JSON
    });

    const data = await response.json();
    console.log("Response from backend:", data); // check in browser console

  } catch (error) {
    console.error("Error sending query:", error);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="container">
      <form className="search-bar search-bar-icon" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Type Your Question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          autoComplete="new-password"
          disabled={loading}
        />
        <span className="search-icon-separator"></span>
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

      {answer && <div className="answer-box">{answer}</div>}
    </div>
  );
}

export default App;
