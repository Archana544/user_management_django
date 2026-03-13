import { useEffect } from "react";
import { useDocument } from "../context/DocumentContext";
import DocumentCard from "../components/DocumentCard";
import "../styles/documents.css";

export default function DocumentsPage() {
  const { documents, fetchDocuments } = useDocument();

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return (
    <div>
      <h2>Your Documents</h2>
      <div className="documents-grid">
        {documents.map((doc) => (
          <DocumentCard key={doc.id} doc={doc} refresh={fetchDocuments} />
        ))}
      </div>
    </div>
  );
}