import { useEffect } from "react";
import API from "../api/api";
import DocumentCard from "./DocumentCard";
import { useDocument } from "../context/DocumentContext";

export default function DocumentList() {

  const { documents, setDocuments } = useDocument();

  const fetchDocuments = async () => {
    const res = await API.get("/api/v1/documents/");
    setDocuments(res.data);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {

  const refreshHandler = () => fetchDocuments();

  window.addEventListener("documentUploaded", refreshHandler);

  return () =>
    window.removeEventListener("documentUploaded", refreshHandler);

}, []);

  return (
    <div className="doc-grid">

      {documents.map(doc => (
        <DocumentCard
          key={doc.id}
          doc={doc}
          refresh={fetchDocuments}
        />
      ))}

    </div>
  );
}