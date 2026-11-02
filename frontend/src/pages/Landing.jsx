
import React from "react";
import { Link } from "react-router-dom";

const services = [
  {
    icon: "📝",
    title: "Easy Complaint Submission",
    description:
      "Submit maintenance complaints using text or voice."
  },
  {
    icon: "🤖",
    title: "AI-Powered Classification",
    description:
      "Automatically classify complaints into the appropriate categories."
  },
  {
    icon: "⚡",
    title: "Smart Priority Routing",
    description:
      "Route complaints to the appropriate maintenance team based on priority."
  },
  {
    icon: "📊",
    title: "Complaint Tracking",
    description:
      "View your complaints and follow their status."
  }
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-50">

      <main className="mx-auto max-w-6xl px-6 py-16">
        <section className="text-center">
          <p className="mb-4 font-semibold text-teal-600">
            SMARTER FACILITY MANAGEMENT
          </p>

          <h2 className="text-4xl font-bold leading-tight text-gray-900 md:text-5xl">
            Facility Management,
            <span className="text-blue-700">
              {" "}Made Simple
            </span>
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-gray-600">
            Report maintenance issues, receive AI-powered
            assistance, and track your complaints in one place.
          </p>

          <Link
            to="/register"
            className="mt-8 inline-block rounded-xl bg-blue-700 px-7 py-3 font-semibold text-white shadow-sm hover:bg-blue-800"
          >
            Get Started
          </Link>
        </section>

        <section className="mt-20">
          <h3 className="text-center text-2xl font-bold text-gray-900">
            Our Services
          </h3>

          <p className="mt-3 text-center text-gray-500">
            Everything you need to manage maintenance complaints.
          </p>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {services.map((service) => (
              <div
                key={service.title}
                className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
              >
                
                <div className="text-3xl flex items-center justify-center ">
                  {service.icon}
                </div>

                <h4 className="mt-5 font-bold text-gray-900 flex items-center justify-center">
                  {service.title}
                </h4>

                <p className="mt-3 text-sm leading-6 text-gray-600 flex items-center justify-center text-center">
                  {service.description}
                </p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-200 bg-white px-6 py-5 text-center text-sm text-gray-500">
        Smart Facility Management System
      </footer>
    </div>
  );
}
