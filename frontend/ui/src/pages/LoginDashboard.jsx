import React, { useState, useEffect } from "react";
import axios from "axios";
import FlaskAPIComponent from "./FLaskAPIComponent";
import "./dashboard.css";

const API_BASE = "http://127.0.0.1:8000";

export default function LoginDashboard() {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("accessToken");

  useEffect(() => {
    if (token) fetchDocuments();
  }, [token]);

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_BASE}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = Array.isArray(res.data)
        ? res.data
        : res.data.results;

      setDocuments(data);

    } catch (err) {
      alert("Failed to fetch documents.");
    }
  };

  // CREATE
 const handleUpload = async () => {
  if (!file || !title) return alert("Enter title & select file");

  console.log("Uploading:", file, title, token, documents);

  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);

  try {
    setLoading(true);

    const res = await axios.post(`${API_BASE}/api/v1/documents/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Upload response:", res.data);

    // Ensure documents is always an array
    setDocuments([res.data, ...(documents || [])]);
    setTitle("");
    setFile(null);
  } catch (err) {
    console.error("Upload failed:", err.response?.data || err.message);
    alert("Upload failed");
  } finally {
    setLoading(false);
  }
};

  // DELETE
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure?")) return;

    try {
      await axios.delete(`${API_BASE}/api/v1/documents/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setDocuments(documents.filter((doc) => doc.id !== id));
    } catch {
      alert("Delete failed");
    }
  };

  // UPDATE
  const handleUpdate = async (id) => {
    try {
      const res = await axios.patch(
        `${API_BASE}/api/v1/documents/${id}/`,
        { title: editingTitle },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setDocuments(
        documents.map((doc) => (doc.id === id ? res.data|| doc : doc))
      );

      setEditingId(null);
      setEditingTitle("");
    } catch {
      alert("Update failed");
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/";
  };

  if (!token) {
    return <h3 style={{ color: "red" }}>Please login first.</h3>;
  }

  return (
    <div className="dashboard">
      <div className="header">
        <h2>📁 Document Dashboard</h2>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {/* Upload Section */}
      <div className="upload-card">
        <h3>Upload Document</h3>
        <input
          type="text"
          placeholder="Document title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>
      </div>

      <FlaskAPIComponent token={token} />

      {/* Document List */}
      <div className="documents-grid">
        {documents?.length === 0 ? (
          <p>No documents uploaded yet.</p>
        ) : (
          documents?.map((doc) => (
            <div key={doc.id} className="document-card">
              {editingId === doc.id ? (
                <>
                  <input
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                  />
                  <button onClick={() => handleUpdate(doc.id)}>Save</button>
                  <button onClick={() => setEditingId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  <h4>{doc.title}</h4>
                  <p><b>Type:</b> {doc.file_type}</p>
                  <p>
                    <b>Uploaded:</b>{" "}
                    {new Date(doc.uploaded_at).toLocaleString()}
                  </p>

                  <div className="card-buttons">
                    <button
                      className="edit-btn"
                      onClick={() => {
                        setEditingId(doc.id);
                        setEditingTitle(doc.title);
                      }}
                    >
                      Edit
                    </button>

                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(doc.id)}
                    >
                      Delete
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
