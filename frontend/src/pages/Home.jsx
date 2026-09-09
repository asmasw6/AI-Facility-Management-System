import React from "react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">Report an Issue</h1>

          <p className="mt-2 text-gray-600">
            Submit your complaint and let our AI-powered system handle the rest.
          </p>
        </div>

        {/* Complaint Form */}
        <div className="rounded-2xl bg-white p-8 shadow-sm">
          {/* Category */}
          {/*
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Complaint Category
            </label>

            <select className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500">
              <option value="">Select a category</option>
              <option value="electricity">Electricity Issue</option>
              <option value="security">Security Complaint</option>
              <option value="plumbing">Plumbing Issue</option>
              <option value="water">Water Supply Request</option>
            </select>
          </div>
*/}
          {/* Description */}
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Describe your issue
            </label>

            <textarea
              rows="6"
              placeholder="Tell us what happened..."
              className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-blue-500"
            />
          </div>

          {/* Submit */}
          <button
            type="button"
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700"
          >
            Submit Complaint
          </button>
        </div>
      </div>
    </div>
  );
}
