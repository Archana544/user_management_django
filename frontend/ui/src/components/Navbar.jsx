
export default function Navbar() {
  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="navbar">
      <span>Welcome Back 👋</span>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}