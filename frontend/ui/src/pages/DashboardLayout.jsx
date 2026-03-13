import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import UploadModal from "../components/UploadModal";
import { useDocument } from "../context/DocumentContext";
import DocumentList from "../components/DashboardList";
import "../styles/dashboard.css"

export default function DashboardLayout() {

  const [showModal, setShowModal] = useState(false);
  const { uploadedFileName, setUploadedFileName, fetchDocuments } = useDocument();
  const token = localStorage.getItem("accessToken");

  return (
    <div className="layout">

      <Sidebar />

      <div className="main">

        <Navbar />

        <div className="content">
           
          <button
            className="upload-open-btn"
            onClick={() => setShowModal(true)}
          >
            📎 Upload Document
          </button>

          <Outlet />

          {showModal && (
            <UploadModal
              token={token}
              onClose={() => setShowModal(false)}
              onUploadSuccess={(fileName) => {
                setUploadedFileName(fileName);
                fetchDocuments() 
                setShowModal(false);
                
              }}
            />
          )}

        </div>
      </div>
    </div>
  );
}