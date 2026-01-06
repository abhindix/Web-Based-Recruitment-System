import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api/auth";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 460, margin: "80px auto" }}>
        <h2>Sign in</h2>
        <p style={{ opacity: 0.85 }}>
          Hiring managers get a chatbot dashboard. Applicants can browse jobs and apply with a CV upload.
        </p>

        <div className="grid">
          <input
            className="input"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className="input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div style={{ color: "#ffb4b4" }}>{error}</div>}

          <button
            className="btn"
            onClick={async () => {
              try {
                setError("");
                await login(email, password);
                window.location.reload();
              } catch (e: any) {
                setError(e.message || "Invalid email or password");
              }
            }}
          >
            Login
          </button>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, opacity: 0.85 }}>
            <span>Don’t have an account? <Link to="/register">Register</Link></span>
            <span><Link to="/">Back</Link></span>
            <span><a href="#" onClick={() => nav('/forgot-password')}>Forgot password?</a></span>
          </div>
        </div>

        <div style={{ marginTop: 18, opacity: 0.8, fontSize: 13 }}>
          Demo manager: <b>admin@test.com</b> / <b>admin123</b>
        </div>
      </div>
    </div>
  );
}
