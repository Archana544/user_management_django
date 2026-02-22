import React, { useState } from "react";
import axios from "axios";

const API_FLASK = "http://127.0.0.1:5000/api/flask-predict";

export default function FlaskAPIComponent({ token }) {
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCallFlask = async () => {
    if (!inputText) return alert("Enter some text");

    setLoading(true);
    try {
      const res = await axios.post(
        API_FLASK,
        { text: inputText },
        {
          headers: {
            Authorization: `Bearer ${token}`, // if Flask expects JWT
          },
        }
      );
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Flask API call failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Call Flask API</h3>
      <input
        type="text"
        value={inputText}
        placeholder="Enter input for Flask"
        onChange={(e) => setInputText(e.target.value)}
      />
      <button onClick={handleCallFlask} disabled={loading}>
        {loading ? "Processing..." : "Send to Flask"}
      </button>

      {result && (
        <div style={{ marginTop: "1rem" }}>
          <strong>Result:</strong> {JSON.stringify(result)}
        </div>
      )}
    </div>
  );
}
