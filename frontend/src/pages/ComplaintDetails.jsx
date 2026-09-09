import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTicket } from "../services/api";
import { formatValue, getPriorityClass, getStatusClass } from "../utils/helpers";



export default function ComplaintDetails() {
  const { id } = useParams();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchTicket() {
      try {
        const data = await getTicket(id);
        setTicket(data);
      } catch (err) {
        console.error("Failed to load complaint:", err);
        setError("Unable to load complaint.");
      } finally {
        setLoading(false);
      }
    }

    fetchTicket();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Loading complaint...</p>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-gray-50 px-6 py-10">
        <div className="mx-auto max-w-5xl">
          <Link
            to="/complaints"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← Back to My Complaints
          </Link>

          <div className="mt-6 rounded-xl border border-red-200 bg-white p-8 text-center">
            <p className="text-red-500">
              {error || "Complaint not found."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const ticketId = ticket.id || ticket._id;

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-5xl">

        {/* Back */}
        <Link
          to="/complaints"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          ← Back to My Complaints
        </Link>

        {/* Header */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-4">

            <div>
              <p className="text-sm font-medium text-blue-600">
                Complaint #{ticketId}
              </p>

              <h1 className="mt-2 text-2xl font-bold text-gray-900">
                {formatValue(ticket.predicted_category)}
              </h1>

              <p className="mt-2 text-sm text-gray-500">
                Submitted on{" "}
                {ticket.created_at
                  ? new Date(ticket.created_at).toLocaleString()
                  : "—"}
              </p>
            </div>

            <span
              className={`rounded-full px-4 py-2 text-sm font-medium ${getStatusClass(
                ticket.status
              )}`}
            >
              {formatValue(ticket.status)}
            </span>

          </div>
        </div>

        {/* Issue Description */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            Issue Description
          </h2>

          <p className="mt-4 leading-7 text-gray-600">
            {ticket.issue_description || "No description available."}
          </p>

        </div>

        {/* Complaint Information */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            Complaint Information
          </h2>

          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">

            {/* Category */}
            <div>
              <p className="text-sm text-gray-500">
                Category
              </p>

              <p className="mt-1 font-medium text-gray-900">
                {formatValue(ticket.predicted_category)}
              </p>
            </div>

            {/* Priority */}
            <div>
              <p className="text-sm text-gray-500">
                Priority
              </p>

              <span
                className={`mt-1 inline-block rounded-md px-3 py-1 text-sm font-medium ${getPriorityClass(
                  ticket.priority
                )}`}
              >
                {formatValue(ticket.priority)}
              </span>
            </div>

            {/* Status */}
            <div>
              <p className="text-sm text-gray-500">
                Status
              </p>

              <p className="mt-1 font-medium text-gray-900">
                {formatValue(ticket.status)}
              </p>
            </div>

          </div>

        </div>

        {/* AI Analysis */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex items-center justify-between">

            <h2 className="text-lg font-semibold text-gray-900">
              AI Analysis
            </h2>

            <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
              AI Generated
            </span>

          </div>

          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

            {/* Category */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Predicted Category
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(ticket.predicted_category)}
              </p>
            </div>

            {/* Confidence */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Confidence
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {ticket.confidence != null
                  ? `${(ticket.confidence * 100).toFixed(1)}%`
                  : "—"}
              </p>
            </div>

            {/* Sentiment */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Sentiment
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(ticket.sentiment)}
              </p>
            </div>

            {/* Priority */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Priority
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(ticket.priority)}
              </p>
            </div>

          </div>

          {/* Priority Reason */}
          <div className="mt-5 rounded-lg bg-gray-50 p-4">
            <p className="text-sm text-gray-500">
              Priority Reason
            </p>

            <p className="mt-2 leading-6 text-gray-700">
              {ticket.priority_reason || "—"}
            </p>
          </div>

          {/* Routing */}
          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2">

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Route
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(ticket.route)}
              </p>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Routing Team
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(ticket.routing_team)}
              </p>
            </div>

          </div>

          {/* AI Response */}
          <div className="mt-5 rounded-lg bg-gray-50 p-4">

            <p className="text-sm text-gray-500">
              AI Response
            </p>

            <p className="mt-2 leading-6 text-gray-700">
              {ticket.ai_response || "No AI response available."}
            </p>

          </div>

        </div>

        {/* Status Updates */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            Status Updates
          </h2>

          <div className="mt-6 space-y-6">

            {/* Submitted */}
            <div className="flex gap-4">

              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-600">
                ✓
              </div>

              <div>
                <p className="font-medium text-gray-900">
                  Complaint submitted
                </p>

                <p className="text-sm text-gray-500">
                  {ticket.created_at
                    ? new Date(ticket.created_at).toLocaleString()
                    : "—"}
                </p>
              </div>

            </div>

            {/* Current Status */}
            <div className="flex gap-4">

              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                ●
              </div>

              <div>
                <p className="font-medium text-gray-900">
                  {formatValue(ticket.status)}
                </p>

                <p className="text-sm text-gray-500">
                  Current complaint status
                </p>
              </div>

            </div>

            {/* Resolved */}
            <div className="flex gap-4">

              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  ticket.resolved_at
                    ? "bg-green-100 text-green-600"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {ticket.resolved_at ? "✓" : "○"}
              </div>

              <div>
                <p
                  className={`font-medium ${
                    ticket.resolved_at
                      ? "text-gray-900"
                      : "text-gray-400"
                  }`}
                >
                  Issue resolved
                </p>

                <p
                  className={`text-sm ${
                    ticket.resolved_at
                      ? "text-gray-500"
                      : "text-gray-400"
                  }`}
                >
                  {ticket.resolved_at
                    ? new Date(ticket.resolved_at).toLocaleString()
                    : "Pending"}
                </p>
              </div>

            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
