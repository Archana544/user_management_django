import API from "../api/api";
import { useNavigate } from "react-router-dom";

export default function DocumentCard({ doc, refresh }) {

  const navigate = useNavigate();

  const handleDelete = async () => {
    await API.delete(`/api/v1/documents/${doc.id}/`);
    refresh();
  };

  const askAI = () => {
    navigate("/dashboard/chat");
  };

  const downloadCSV = () => {
    const blob = new Blob([doc.extracted_content], {
      type: "text/csv"
    });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${doc.title}.csv`;
    a.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="doc-card">

      <h4>{doc.title}</h4>
      <p>{doc.file_type}</p>
      <p>{new Date(doc.uploaded_at).toLocaleString()}</p>

      <div className="doc-actions">


        <button onClick={handleDelete}>
          Delete
        </button>

        <button className="ask-ai-btn" onClick={askAI}>
          🤖 Ask AI
        </button>
        <button onClick={downloadCSV}>
          📥 Download CSV
        </button>

      </div>
    </div>
  );
}