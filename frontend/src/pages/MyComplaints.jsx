
import React, { useEffect, useState } from "react";
import ComplaintCard from "../components/ComplaintCard";
import { getTickets } from "../services/api";

export default function MyComplaints() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchComplaints() {
      try {
        const data = await getTickets();
        setComplaints(data);
      } catch (err) {
        console.error("Failed to load complaints:", err);
        setError("Unable to load complaints.");
      } finally {
        setLoading(false);
      }
    }

    fetchComplaints();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Loading complaints...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-6xl mx-auto">

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            My Complaints
          </h1>

          <p className="text-gray-500 mt-2">
            View and track your submitted complaints.
          </p>
        </div>

        {/* Empty State */}
        {complaints.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-200 p-10 text-center">
            <h2 className="text-lg font-semibold text-gray-900">
              No complaints yet
            </h2>

            <p className="text-gray-500 mt-2">
              You haven't submitted any complaints.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {complaints.map((complaint) => (
              <ComplaintCard
                key={complaint.id}
                complaint={complaint}
              />
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
