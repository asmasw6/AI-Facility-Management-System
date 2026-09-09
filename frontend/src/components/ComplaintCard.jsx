
import React from "react";
import { Link } from "react-router-dom";
import { formatValue, getPriorityClass, getStatusClass } from "../utils/helpers";


export default function ComplaintCard({ complaint }) {
  const ticketId = complaint.id || complaint._id;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition">

      {/* Top Section */}
      <div className="flex items-start justify-between gap-4">

        <div className="min-w-0">
          <p className="text-sm font-medium text-blue-600">
            Complaint #{ticketId}
          </p>

          <h2 className="mt-1 text-lg font-semibold text-gray-900">
            {formatValue(complaint.predicted_category)}
          </h2>
        </div>

        {/* Status */}
        <span
          className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(
            complaint.status
          )}`}
        >
          {formatValue(complaint.status)}
        </span>

      </div>

      {/* Complaint Description */}
      <div className="mt-4">
        <p className="text-xs text-gray-500">
          Complaint
        </p>

        <p className="mt-1 text-sm text-gray-700 line-clamp-2">
          {complaint.issue_description || "No description available."}
        </p>
      </div>

      {/* Information */}
      <div className="mt-5 grid grid-cols-3 gap-4 border-t border-gray-100 pt-5">

        {/* Category */}
        <div>
          <p className="text-xs text-gray-500">
            Category
          </p>

          <p className="mt-1 text-sm font-medium text-gray-900">
            {formatValue(complaint.predicted_category)}
          </p>
        </div>

        {/* Priority */}
        <div>
          <p className="text-xs text-gray-500">
            Priority
          </p>

          <span
            className={`mt-1 inline-block px-2 py-1 rounded-md text-xs font-medium ${getPriorityClass(
              complaint.priority
            )}`}
          >
            {formatValue(complaint.priority)}
          </span>
        </div>

        {/* Submitted */}
        <div>
          <p className="text-xs text-gray-500">
            Submitted
          </p>

          <p className="mt-1 text-sm font-medium text-gray-900">
            {complaint.created_at
              ? new Date(complaint.created_at).toLocaleDateString()
              : "—"}
          </p>
        </div>

      </div>

      {/* AI Information */}
      <div className="mt-5 flex flex-wrap gap-2">

        {complaint.sentiment && (
          <span className="px-2.5 py-1 rounded-md bg-gray-100 text-gray-600 text-xs">
            Sentiment: {formatValue(complaint.sentiment)}
          </span>
        )}

        {complaint.routing_team && (
          <span className="px-2.5 py-1 rounded-md bg-gray-100 text-gray-600 text-xs">
            Team: {complaint.routing_team}
          </span>
        )}

      </div>

      {/* View Details */}
      <div className="mt-5 border-t border-gray-100 pt-4">

        <Link
          to={`/complaints/${ticketId}`}
          className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          View Details →
        </Link>

      </div>

    </div>
  );
}
