import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2>DocuAI</h2>
      <Link to="/dashboard/documents">📁 Documents</Link>
      <Link to="/dashboard/chat">💬 RAG Chat</Link>
    </div>
  );
}