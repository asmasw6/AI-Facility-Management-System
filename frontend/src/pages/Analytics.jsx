
import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getTickets } from "../services/api";
import { formatValue, getPriorityClass, getStatusClass } from "../utils/helpers";

export default function Analytics() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const data = await getTickets();
        setTickets(data);
      } catch (err) {
        console.error("Failed to load analytics:", err);
        setError("Unable to load analytics.");
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, []);

  /* =========================
     BASIC STATISTICS
  ========================== */

  const statistics = useMemo(() => {
    const total = tickets.length;

    const resolved = tickets.filter(
      (ticket) => ticket.status === "resolved"
    ).length;

    const urgent = tickets.filter(
      (ticket) => ticket.priority === "urgent"
    ).length;

    const high = tickets.filter(
      (ticket) => ticket.priority === "high"
    ).length;

    const negative = tickets.filter(
      (ticket) => ticket.sentiment === "negative"
    ).length;

    const resolutionRate =
      total > 0 ? ((resolved / total) * 100).toFixed(1) : 0;

    const urgentRate =
      total > 0 ? ((urgent / total) * 100).toFixed(1) : 0;

    const negativeRate =
      total > 0 ? ((negative / total) * 100).toFixed(1) : 0;

    return {
      total,
      resolved,
      urgent,
      high,
      negative,
      resolutionRate,
      urgentRate,
      negativeRate,
    };
  }, [tickets]);

  /* =========================
     CATEGORY ANALYTICS
  ========================== */

  const categoryStats = useMemo(() => {
    const categories = {};

    tickets.forEach((ticket) => {
      const category =
        ticket.predicted_category || "Unknown";

      categories[category] =
        (categories[category] || 0) + 1;
    });

    return Object.entries(categories)
      .sort((a, b) => b[1] - a[1]);
  }, [tickets]);

  /* =========================
     STATUS ANALYTICS
  ========================== */

  const statusStats = useMemo(() => {
    const statuses = {
      open: 0,
      in_progress: 0,
      resolved: 0,
      closed: 0,
    };

    tickets.forEach((ticket) => {
      if (statuses[ticket.status] !== undefined) {
        statuses[ticket.status]++;
      }
    });

    return Object.entries(statuses);
  }, [tickets]);

  /* =========================
     PRIORITY ANALYTICS
  ========================== */

  const priorityStats = useMemo(() => {
    const priorities = {
      urgent: 0,
      high: 0,
      medium: 0,
      low: 0,
    };

    tickets.forEach((ticket) => {
      if (priorities[ticket.priority] !== undefined) {
        priorities[ticket.priority]++;
      }
    });

    return Object.entries(priorities);
  }, [tickets]);

  /* =========================
     SENTIMENT ANALYTICS
  ========================== */

  const sentimentStats = useMemo(() => {
    const sentiments = {
      positive: 0,
      neutral: 0,
      negative: 0,
    };

    tickets.forEach((ticket) => {
      if (sentiments[ticket.sentiment] !== undefined) {
        sentiments[ticket.sentiment]++;
      }
    });

    return Object.entries(sentiments);
  }, [tickets]);

  /* =========================
     ROUTING ANALYTICS
  ========================== */

  const routingStats = useMemo(() => {
    const teams = {};

    tickets.forEach((ticket) => {
      const team =
        ticket.routing_team || "Unassigned";

      teams[team] =
        (teams[team] || 0) + 1;
    });

    return Object.entries(teams)
      .sort((a, b) => b[1] - a[1]);
  }, [tickets]);

  /* =========================
     TOP CATEGORY
  ========================== */

  const topCategory =
    categoryStats.length > 0
      ? categoryStats[0][0]
      : "—";

  /* =========================
     LOADING
  ========================== */

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">
          Loading analytics...
        </p>
      </div>
    );
  }

  /* =========================
     ERROR
  ========================== */

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

        {/* =========================
            HEADER
        ========================== */}

        <div className="mb-8 flex items-start justify-between">

          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Analytics
            </h1>

            <p className="mt-2 text-gray-500">
              Analyze complaints, AI predictions, sentiment,
              priorities, and maintenance routing.
            </p>
          </div>

          <Link
            to="/admin/dashboard"
            className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            ← Dashboard
          </Link>

        </div>


        {/* =========================
            KPI CARDS
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


          {/* Resolution Rate */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Resolution Rate
            </p>

            <p className="mt-2 text-3xl font-bold text-green-600">
              {statistics.resolutionRate}%
            </p>
          </div>


          {/* Urgent */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Urgent Complaints
            </p>

            <p className="mt-2 text-3xl font-bold text-red-600">
              {statistics.urgent}
            </p>

            <p className="mt-1 text-xs text-gray-400">
              {statistics.urgentRate}% of total
            </p>
          </div>


          {/* High */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              High Priority
            </p>

            <p className="mt-2 text-3xl font-bold text-orange-600">
              {statistics.high}
            </p>
          </div>


          {/* Negative */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-500">
              Negative Sentiment
            </p>

            <p className="mt-2 text-3xl font-bold text-gray-700">
              {statistics.negative}
            </p>

            <p className="mt-1 text-xs text-gray-400">
              {statistics.negativeRate}% of analyzed tickets
            </p>
          </div>

        </div>


        {/* =========================
            CATEGORY + PRIORITY
        ========================== */}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Category */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Complaints by Category
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Most frequently reported issues.
            </p>

            <div className="mt-6 space-y-5">

              {categoryStats.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No category data available.
                </p>
              ) : (
                categoryStats.map(([category, count]) => {

                  const percentage =
                    statistics.total > 0
                      ? (count / statistics.total) * 100
                      : 0;

                  return (
                    <div key={category}>

                      <div className="flex justify-between">

                        <span className="text-sm font-medium text-gray-700">
                          {formatValue(category)}
                        </span>

                        <span className="text-sm font-semibold text-gray-900">
                          {count}
                        </span>

                      </div>

                      <div className="mt-2 h-2 rounded-full bg-gray-100">

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

            {topCategory !== "—" && (
              <div className="mt-6 rounded-lg bg-blue-50 p-4">

                <p className="text-xs text-blue-600">
                  Most Reported Category
                </p>

                <p className="mt-1 font-semibold text-blue-900">
                  {formatValue(topCategory)}
                </p>

              </div>
            )}

          </div>


          {/* Priority */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Priority Distribution
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              AI-generated complaint priority levels.
            </p>

            <div className="mt-6 space-y-5">

              {priorityStats.map(([priority, count]) => {

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

                    <div className="mt-2 h-2 rounded-full bg-gray-100">

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
            STATUS + SENTIMENT
        ========================== */}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Status */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Complaint Status
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Current lifecycle of submitted complaints.
            </p>

            <div className="mt-6 grid grid-cols-2 gap-4">

              {statusStats.map(([status, count]) => (

                <div
                  key={status}
                  className="rounded-lg bg-gray-50 p-4"
                >

                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-medium ${getStatusClass(
                      status
                    )}`}
                  >
                    {formatValue(status)}
                  </span>

                  <p className="mt-3 text-2xl font-bold text-gray-900">
                    {count}
                  </p>

                  <p className="text-xs text-gray-500">
                    complaints
                  </p>

                </div>

              ))}

            </div>

          </div>


          {/* Sentiment */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-gray-900">
              Customer Sentiment
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Sentiment detected by the AI system.
            </p>

            <div className="mt-6 space-y-5">

              {sentimentStats.map(([sentiment, count]) => {

                const percentage =
                  statistics.total > 0
                    ? (count / statistics.total) * 100
                    : 0;

                return (
                  <div key={sentiment}>

                    <div className="flex justify-between">

                      <span className="text-sm font-medium text-gray-700">
                        {formatValue(sentiment)}
                      </span>

                      <span className="text-sm font-semibold text-gray-900">
                        {count}
                      </span>

                    </div>

                    <div className="mt-2 h-2 rounded-full bg-gray-100">

                      <div
                        className="h-2 rounded-full bg-gray-500"
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
            AI ROUTING
        ========================== */}

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            AI Agent Routing
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            How complaints are distributed across maintenance teams.
          </p>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {routingStats.length === 0 ? (
              <p className="text-sm text-gray-500">
                No routing data available.
              </p>
            ) : (
              routingStats.map(([team, count]) => {

                const percentage =
                  statistics.total > 0
                    ? ((count / statistics.total) * 100).toFixed(1)
                    : 0;

                return (
                  <div
                    key={team}
                    className="rounded-lg border border-gray-100 bg-gray-50 p-5"
                  >

                    <p className="text-sm text-gray-500">
                      Routing Team
                    </p>

                    <p className="mt-2 font-semibold text-gray-900">
                      {team}
                    </p>

                    <p className="mt-4 text-2xl font-bold text-blue-600">
                      {count}
                    </p>

                    <p className="text-xs text-gray-500">
                      {percentage}% of complaints
                    </p>

                  </div>
                );
              })
            )}

          </div>

        </div>


        {/* =========================
            AI INSIGHTS
        ========================== */}

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-gray-900">
            AI System Insights
          </h2>

          <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">

            <div className="rounded-lg bg-gray-50 p-5">

              <p className="text-sm text-gray-500">
                Top Complaint Type
              </p>

              <p className="mt-2 font-semibold text-gray-900">
                {formatValue(topCategory)}
              </p>

            </div>


            <div className="rounded-lg bg-gray-50 p-5">

              <p className="text-sm text-gray-500">
                Urgent Rate
              </p>

              <p className="mt-2 font-semibold text-red-600">
                {statistics.urgentRate}%
              </p>

            </div>


            <div className="rounded-lg bg-gray-50 p-5">

              <p className="text-sm text-gray-500">
                Resolution Rate
              </p>

              <p className="mt-2 font-semibold text-green-600">
                {statistics.resolutionRate}%
              </p>

            </div>

          </div>

        </div>


        {/* =========================
            FOOTER
        ========================== */}

        <div className="mt-6 text-center">

          <p className="text-xs text-gray-400">
            Analytics are calculated from the current complaint data.
          </p>

        </div>

      </div>

    </div>
  );
}
