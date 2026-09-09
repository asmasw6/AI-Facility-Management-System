
import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getTickets } from "../services/api";
import { formatValue, getPriorityClass, getStatusClass } from "../utils/helpers";



export default function Dashboard() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchTickets() {
      try {
        const data = await getTickets();
        setTickets(data);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError("Unable to load dashboard data.");
      } finally {
        setLoading(false);
      }
    }

    fetchTickets();
  }, []);

  const statistics = useMemo(() => {
    return {
      total: tickets.length,

      open: tickets.filter(
        (ticket) => ticket.status === "open"
      ).length,

      inProgress: tickets.filter(
        (ticket) => ticket.status === "in_progress"
      ).length,

      resolved: tickets.filter(
        (ticket) => ticket.status === "resolved"
      ).length,

      urgent: tickets.filter(
        (ticket) => ticket.priority === "urgent"
      ).length,

      high: tickets.filter(
        (ticket) => ticket.priority === "high"
      ).length,

      medium: tickets.filter(
        (ticket) => ticket.priority === "medium"
      ).length,

      low: tickets.filter(
        (ticket) => ticket.priority === "low"
      ).length,
    };
  }, [tickets]);

  const categoryStats = useMemo(() => {
    const categories = {};

    tickets.forEach((ticket) => {
      const category = ticket.predicted_category || "Unknown";

      categories[category] = (categories[category] || 0) + 1;
    });

    return Object.entries(categories).sort((a, b) => b[1] - a[1]);
  }, [tickets]);

  const teamStats = useMemo(() => {
    const teams = {};

    tickets.forEach((ticket) => {
      const team = ticket.routing_team || "Unassigned";

      teams[team] = (teams[team] || 0) + 1;
    });

    return Object.entries(teams).sort((a, b) => b[1] - a[1]);
  }, [tickets]);

  const recentTickets = useMemo(() => {
    return [...tickets]
      .sort(
        (a, b) =>
          new Date(b.created_at) - new Date(a.created_at)
      )
      .slice(0, 5);
  }, [tickets]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">
          Loading dashboard...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-xl border border-red-200 bg-white p-8 text-center">
            <p className="text-red-500">
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-10">

      <div className="mx-auto max-w-7xl">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Admin Dashboard
          </h1>

          <p className="mt-2 text-gray-500">
            Monitor complaints, AI analysis, priorities, and maintenance routing.
          </p>
        </div>


        {/* =========================
            STATISTICS
        ========================== */}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">

          {/* Total */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Total Complaints
            </p>

            <p className="mt-2 text-3xl font-bold text-gray-900">
              {statistics.total}
            </p>
          </div>


          {/* Open */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Open
            </p>

            <p className="mt-2 text-3xl font-bold text-blue-600">
              {statistics.open}
            </p>
          </div>


          {/* In Progress */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              In Progress
            </p>

            <p className="mt-2 text-3xl font-bold text-purple-600">
              {statistics.inProgress}
            </p>
          </div>


          {/* Resolved */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Resolved
            </p>

            <p className="mt-2 text-3xl font-bold text-green-600">
              {statistics.resolved}
            </p>
          </div>


          {/* Urgent */}
          <div className="rounded-xl border border-red-100 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Urgent
            </p>

            <p className="mt-2 text-3xl font-bold text-red-600">
              {statistics.urgent}
            </p>
          </div>

        </div>


        {/* =========================
            ANALYTICS
        ========================== */}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">


          {/* Categories */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Complaints by Category
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Distribution of reported issues.
            </p>

            <div className="mt-6 space-y-5">

              {categoryStats.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No data available.
                </p>
              ) : (
                categoryStats.map(([category, count]) => {

                  const percentage =
                    statistics.total > 0
                      ? (count / statistics.total) * 100
                      : 0;

                  return (
                    <div key={category}>

                      <div className="flex items-center justify-between">

                        <p className="text-sm font-medium text-gray-700">
                          {formatValue(category)}
                        </p>

                        <p className="text-sm font-semibold text-gray-900">
                          {count}
                        </p>

                      </div>

                      <div className="mt-2 h-2 w-full rounded-full bg-gray-100">

                        <div
                          className="h-2 rounded-full bg-blue-500"
                          style={{
                            width: `${percentage}%`,
                          }}
                        />

                      </div>

                    </div>
                  );
                })
              )}

            </div>

          </div>


          {/* Priority */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Complaints by Priority
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Priority distribution generated by the AI system.
            </p>

            <div className="mt-6 space-y-5">

              {[
                ["urgent", statistics.urgent],
                ["high", statistics.high],
                ["medium", statistics.medium],
                ["low", statistics.low],
              ].map(([priority, count]) => {

                const percentage =
                  statistics.total > 0
                    ? (count / statistics.total) * 100
                    : 0;

                return (
                  <div key={priority}>

                    <div className="flex items-center justify-between">

                      <span
                        className={`rounded-md px-2.5 py-1 text-xs font-medium ${getPriorityClass(
                          priority
                        )}`}
                      >
                        {formatValue(priority)}
                      </span>

                      <span className="text-sm font-semibold text-gray-900">
                        {count}
                      </span>

                    </div>

                    <div className="mt-2 h-2 w-full rounded-full bg-gray-100">

                      <div
                        className="h-2 rounded-full bg-gray-700"
                        style={{
                          width: `${percentage}%`,
                        }}
                      />

                    </div>

                  </div>
                );
              })}

            </div>

          </div>

        </div>


        {/* =========================
            ROUTING TEAMS
        ========================== */}

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            Maintenance Teams
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Complaints routed by the AI agent.
          </p>

          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {teamStats.length === 0 ? (
              <p className="text-sm text-gray-500">
                No routing data available.
              </p>
            ) : (
              teamStats.map(([team, count]) => (

                <div
                  key={team}
                  className="rounded-lg border border-gray-100 bg-gray-50 p-4"
                >

                  <p className="text-sm text-gray-500">
                    Team
                  </p>

                  <p className="mt-1 font-semibold text-gray-900">
                    {team}
                  </p>

                  <p className="mt-3 text-2xl font-bold text-blue-600">
                    {count}
                  </p>

                  <p className="text-xs text-gray-500">
                    complaints
                  </p>

                </div>

              ))
            )}

          </div>

        </div>


        {/* =========================
            RECENT COMPLAINTS
        ========================== */}

        <div className="mt-6 rounded-xl border border-gray-200 bg-white shadow-sm">

          <div className="flex items-center justify-between border-b border-gray-100 p-6">

            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Recent Complaints
              </h2>

              <p className="mt-1 text-sm text-gray-500">
                Latest complaints submitted to the system.
              </p>
            </div>

            <Link
              to="/complaints"
              className="text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              View All
            </Link>

          </div>


          {recentTickets.length === 0 ? (

            <div className="p-8 text-center">
              <p className="text-sm text-gray-500">
                No complaints available.
              </p>
            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead className="bg-gray-50">

                  <tr>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Complaint
                    </th>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Category
                    </th>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Priority
                    </th>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Status
                    </th>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Team
                    </th>

                    <th className="px-6 py-3 text-xs font-semibold uppercase text-gray-500">
                      Action
                    </th>

                  </tr>

                </thead>


                <tbody className="divide-y divide-gray-100">

                  {recentTickets.map((ticket) => {

                    const ticketId =
                      ticket.id || ticket._id;

                    return (
                      <tr
                        key={ticketId}
                        className="hover:bg-gray-50"
                      >

                        {/* Complaint */}
                        <td className="px-6 py-4">

                          <p className="max-w-xs truncate text-sm font-medium text-gray-900">
                            {ticket.issue_description || "—"}
                          </p>

                          <p className="mt-1 text-xs text-gray-400">
                            #{ticketId}
                          </p>

                        </td>


                        {/* Category */}
                        <td className="px-6 py-4 text-sm text-gray-700">
                          {formatValue(
                            ticket.predicted_category
                          )}
                        </td>


                        {/* Priority */}
                        <td className="px-6 py-4">

                          <span
                            className={`rounded-md px-2.5 py-1 text-xs font-medium ${getPriorityClass(
                              ticket.priority
                            )}`}
                          >
                            {formatValue(ticket.priority)}
                          </span>

                        </td>


                        {/* Status */}
                        <td className="px-6 py-4">

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-medium ${getStatusClass(
                              ticket.status
                            )}`}
                          >
                            {formatValue(ticket.status)}
                          </span>

                        </td>


                        {/* Team */}
                        <td className="px-6 py-4 text-sm text-gray-700">
                          {ticket.routing_team || "—"}
                        </td>


                        {/* Action */}
                        <td className="px-6 py-4">

                          <Link
                            to={`/complaints/${ticketId}`}
                            className="text-sm font-medium text-blue-600 hover:text-blue-700"
                          >
                            View
                          </Link>

                        </td>

                      </tr>
                    );
                  })}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>
    </div>
  );
}
