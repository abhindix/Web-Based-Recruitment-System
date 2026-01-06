import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Jobs from "./pages/Jobs";
import Apply from "./pages/Apply";
import ManagerChat from "./pages/ManagerChat";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Jobs />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/apply/:jobId" element={<Apply />} />
          <Route path="/manager" element={<ManagerChat />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
