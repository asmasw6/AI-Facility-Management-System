
import React, { useState } from "react";

export default function Home() {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!description.trim()) {
      setError("Please describe your issue.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/process-call/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            call_id: "6a9ef4f9c6652a6ae12ec0be", // example call ID
            customer_id: "6a9eda85521ecd1d215366de", // example customer ID
            text: description,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Failed to process call"
        );
      }

      const data = await response.json();

      setResult(data);
      setDescription("");
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl">

        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Report an Issue
          </h1>

          <p className="mt-2 text-gray-600">
            Submit your complaint and let our AI-powered system handle the rest.
          </p>
        </div>

        {/* Complaint Form */}
        <div className="rounded-2xl bg-white p-8 shadow-sm">

          {/* Description */}
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Describe your issue
            </label>

            <textarea
              rows="6"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Tell us what happened..."
              className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="mb-6 rounded-lg bg-green-50 p-4">
              <p className="font-medium text-green-800">
                Complaint processed successfully.
              </p>

              {result.ai_response && (
                <p className="mt-2 text-gray-700">
                  {result.ai_response}
                </p>
              )}

              {result.category && (
                <p className="mt-2 text-sm text-gray-600">
                  Category: {result.category}
                </p>
              )}

              {result.sentiment && (
                <p className="text-sm text-gray-600">
                  Sentiment: {result.sentiment}
                </p>
              )}

              {result.priority && (
                <p className="text-sm text-gray-600">
                  Priority: {result.priority}
                </p>
              )}
            </div>
          )}

          {/* Submit */}
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {loading ? "Processing..." : "Submit Complaint"}
          </button>

        </div>
      </div>
    </div>
  );
}
