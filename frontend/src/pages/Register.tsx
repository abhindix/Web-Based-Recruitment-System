import { useState } from "react";
import { register } from "../api/auth";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [email, setEmail] = useState("");
  const [fullName, setFull] = useState("");
  const [password, setPass] = useState("");
  const [role, setRole] = useState<"manager" | "applicant">("applicant");
  const [err, setErr] = useState("");
  const nav = useNavigate();

  return (
    <div className="card" style={{ maxWidth: 520 }}>
      <h2>Create account</h2>
      <div className="grid">
        <input className="input" placeholder="Full name" value={fullName} onChange={(e) => setFull(e.target.value)} />
        <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="input" placeholder="Password" type="password" value={password} onChange={(e) => setPass(e.target.value)} />
        <select className="input" value={role} onChange={(e) => setRole(e.target.value as any)}>
          <option value="applicant">Applicant</option>
          <option value="manager">Hiring Manager</option>
        </select>
        {err && <div style={{ color: "#ffb4b4", whiteSpace: "pre-wrap" }}>{err}</div>}
        <button
          className="btn"
          onClick={async () => {
            setErr("");
            try {
              await register({ email, full_name: fullName, password, role });
              nav("/login");
            } catch (e: any) {
              setErr(e.message);
            }
          }}
        >
          Register
        </button>
      </div>
    </div>
  );
}
