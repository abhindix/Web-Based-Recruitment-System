import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import CreateJob from "./pages/CreateJob";
import Chat from "./pages/Chat";
import Jobs from "./pages/Jobs";
import Apply from "./pages/Apply";
import { getToken, clearToken } from "./auth";

function Nav() {
  const role = localStorage.getItem("role") || "";
  return (
    <div className="header">
      <div className="brand">RecruitFlow</div>
      <div className="nav">
        <Link className="btn secondary" to="/jobs">Jobs</Link>
        {role === "manager" && (
          <>
            <Link className="btn secondary" to="/create-job">Create Job</Link>
            <Link className="btn secondary" to="/chat">Manager Chat</Link>
          </>
        )}
      </div>
    </div>
  )
}

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = getToken();
  const loc = useLocation();
  if (!token) return <Navigate to="/login" replace state={{ from: loc }} />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="container">
        {getToken() && (
          <>
            <Nav />
            <button
              className="btn secondary"
              onClick={() => {
                clearToken();
                window.location.href = "/login";
              }}
            >
              Sign out
            </button>
          </>
        )}

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          <Route
            path="/jobs"
            element={
              <RequireAuth>
                <Jobs />
              </RequireAuth>
            }
          />
          <Route
            path="/apply/:jobId"
            element={
              <RequireAuth>
                <Apply />
              </RequireAuth>
            }
          />
          <Route
            path="/create-job"
            element={
              <RequireAuth>
                <CreateJob />
              </RequireAuth>
            }
          />
          <Route
            path="/chat"
            element={
              <RequireAuth>
                <Chat />
              </RequireAuth>
            }
          />

          <Route path="/" element={<Navigate to={getToken() ? "/jobs" : "/login"} replace />} />
          <Route path="*" element={<Navigate to={getToken() ? "/jobs" : "/login"} replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
