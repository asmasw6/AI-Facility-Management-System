import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import MyComplaints from "./pages/MyComplaints";
import ComplaintDetails from "./pages/ComplaintDetails";

import Dashboard from "./pages/Dashboard";
import Complaints from "./pages/Complaints";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Landing from "./pages/Landing";

function App() {
  const [isLoadingIn, setIsLoadingIn] = useState(
    !!localStorage.getItem("access_token"),
  );
  return (
    <BrowserRouter>
      <Navbar />

      <main>
        <Routes>
          {/* User */}
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login onLogin={() => setIsLoadingIn(true)} />} />
          <Route path="/" element={!isLoadingIn ? <Landing /> : <Home />} />
          <Route path="/complaints" element={<MyComplaints />} />
          <Route path="/complaints/:id" element={<ComplaintDetails />} />

          {/* Admin */}
          <Route path="/admin/dashboard" element={<Dashboard />} />
          <Route path="/admin/complaints" element={<Complaints />} />
          <Route path="/admin/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
