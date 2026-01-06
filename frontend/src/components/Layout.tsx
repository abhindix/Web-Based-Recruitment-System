import { Link, useNavigate } from "react-router-dom";
import { getToken } from "../api/client";
import { clearToken } from "../auth";

export default function Layout({ children }: { children: React.ReactNode }) {
  const nav = useNavigate();
  const token = getToken();

  return (
    <div className="container">
      <div className="header">
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div style={{ fontWeight: 800, fontSize: 18 }}>RecruitFlow</div>
          <span className="badge">FastAPI • React • OAuth2 • AI Agent</span>
        </div>
        <div className="nav">
          <Link className="btn" to="/jobs">Jobs</Link>
          <Link className="btn" to="/manager">Manager Chat</Link>
          {!token ? (
            <>
              <Link className="btn" to="/login">Login</Link>
              <Link className="btn" to="/register">Register</Link>
            </>
          ) : (
            <button
              className="btn"
              onClick={() => {
                clearToken();
                nav("/login");
              }}
            >
              Logout
            </button>
          )}
        </div>
      </div>

      {children}
    </div>
  );
}
