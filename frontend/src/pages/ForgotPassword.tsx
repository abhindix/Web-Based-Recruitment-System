import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const nav = useNavigate();

  return (
    <div className="card" style={{ maxWidth: 420 }}>
      <h2>Forgot Password</h2>
      <input className="input" placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)} />
      <button className="btn" onClick={() => { setMsg("If this email exists, a reset link will be sent."); }}>
        Send reset link
      </button>
      {msg && <div style={{ color: '#4caf50', marginTop: 10 }}>{msg}</div>}
      <button className="btn" style={{ marginTop: 16 }} onClick={() => nav(-1)}>Back</button>
    </div>
  );
}
