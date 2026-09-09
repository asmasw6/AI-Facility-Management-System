import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import MyComplaints from "./pages/MyComplaints";
import ComplaintDetails from "./pages/ComplaintDetails";

import Dashboard from "./pages/Dashboard";
import Complaints from "./pages/Complaints";
import Analytics from "./pages/Analytics";



function App() {

  return (
   <BrowserRouter>
      <Navbar />

      <main>
        <Routes>
          {/* User */}
          <Route path="/" element={<Home />} />
          <Route path="/complaints" element={<MyComplaints />} />
          <Route path="/complaints/:id"element={<ComplaintDetails />}/>
          
          
          {/* Admin */}
          <Route path="/admin/dashboard" element={<Dashboard />} />
          <Route path="/admin/complaints" element={<Complaints />} />
          <Route path="/admin/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </BrowserRouter>
  )

  
}

export default App
