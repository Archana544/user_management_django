import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from './pages/Login'
import LoginDashboard from "./pages/LoginDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<LoginDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
