import { createContext, useContext, useState, useCallback } from "react";
import API from "../api/api";

const DocumentContext = createContext();

export function DocumentProvider({ children }) {

  const [uploadedFileName, setUploadedFileName] = useState("");
  const [documents, setDocuments] = useState([]);

  const fetchDocuments = useCallback(async () => {
    const res = await API.get("/api/v1/documents/");
    setDocuments(res.data);
  }, []);

  return (
    <DocumentContext.Provider
      value={{
        uploadedFileName,
        setUploadedFileName,
        documents,
        fetchDocuments
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocument() {
  return useContext(DocumentContext);
}