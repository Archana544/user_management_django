import { useState, useRef, useEffect } from "react";
import API from "../api/api";
import { useDocument } from "../context/DocumentContext";
import "../styles/chat.css";

export default function ProfessionalChatPage() {

  const { uploadedFileName } = useDocument();   // ✅ get from context

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async () => {

    if (!query.trim()) return;

    const userMsg = { role: "user", content: query };

    setMessages(prev => [...prev, userMsg]);
    setQuery("");
    setTyping(true);

    try {

      const res = await API.post("/chat/", { query });

      setMessages(prev => [...prev,
        {
          role: "assistant",
          content: res.data.answer || "I don't know"
        }
      ]);

    } catch {
      setMessages(prev => [...prev,
        {
          role: "assistant",
          content: "Unable to generate response."
        }
      ]);
    }

    setTyping(false);
  };

  return (
    <div className="chat-page">

      <header className="chat-header">
        <h2>AI Document Assistant</h2>
        <p>Enterprise Knowledge Retrieval System</p>
      </header>

      {uploadedFileName && (
        <div className="attachment-card">
          📎 {uploadedFileName}
        </div>
      )}

      <main className="chat-body">

        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            {msg.content}
          </div>
        ))}

        {typing && (
          <div className="typing">
            Generating response...
          </div>
        )}

        <div ref={chatEndRef} />
      </main>

      <footer className="chat-footer">

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about your documents..."
        />

        <button onClick={sendMessage}>
          Send
        </button>

      </footer>
    </div>
  );
}