import { useState } from "react";
import API from "../api/api";

export default function UploadModal({ token, onClose, onUploadSuccess }) {

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const uploadFile = async () => {

    if (!file) {
      setError("Please select a file.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);

    try {

      await API.post(
        "/api/v1/documents/",
        formData,
      );

      // ✅ Update global context
      onUploadSuccess(file.name);
     window.dispatchEvent(new Event("documentUploaded"));

      // ✅ Reset internal state
      setFile(null);

      // ✅ Force close modal immediately
      onClose();
      console.log("TOKEN:", token);

    } catch (err) {
      console.error(err);
      setError("Upload failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal-box">

        <h3>Upload Document</h3>

        <input
          type="file"
          onChange={(e) => {
            setFile(e.target.files[0]);
            setError("");
          }}
        />

        {error && <p className="modal-error">{error}</p>}

        <div className="modal-actions">

          <button
            onClick={uploadFile}
            disabled={loading}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>

          <button
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>

        </div>

      </div>
    </div>
  );
}