import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import DashboardLayout from "./pages/DashboardLayout";
import DocumentsPage from "./pages/DocumentsPage";
import ChatPage from "./pages/Chatpage";
import ProtectedRoute from "./routes/ProtectedRoute";
import { DocumentProvider } from "./context/DocumentContext";

function App() {
  return (
    <BrowserRouter>
    <DocumentProvider>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="chat" element={<ChatPage />} />
          </Route>
        </Route>

      </Routes>
      </DocumentProvider>
    </BrowserRouter>
  );
}

export default App;