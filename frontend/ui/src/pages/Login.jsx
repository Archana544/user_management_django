import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate for routing

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate(); // Initialize navigate function

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        throw new Error("Invalid username or password");
      }

      const data = await res.json();

      // Store JWT tokens
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      // Navigate to LoginDashboard after successful login
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <form style={styles.card} onSubmit={handleLogin}>
        <h2 style={styles.title}>Sign In</h2>

        {error && <p style={styles.error}>{error}</p>}

        <input
          style={styles.input}
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          style={styles.input}
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button style={styles.button} disabled={loading}>
          {loading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #0a1f44, #0d47a1)",
    fontFamily: "Arial",
  },
  card: {
    width: "350px",
    padding: "2rem",
    borderRadius: "14px",
    backgroundColor: "#fff",
    boxShadow: "0px 8px 25px rgba(0,0,0,0.2)",
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  title: {
    textAlign: "center",
    marginBottom: "1rem",
    color: "#0d47a1",
  },
  input: {
    padding: "0.75rem",
    borderRadius: "10px",
    border: "1px solid #ccc",
    fontSize: "1rem",
    outline: "none",
  },
  button: {
    padding: "0.75rem",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#0d47a1",
    color: "#fff",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: "bold",
  },
  error: {
    color: "red",
    fontSize: "0.9rem",
    textAlign: "center",
  },
};
