import { Link, NavLink } from "react-router-dom";

const Navbar = () => {
  // مؤقتًا للتجربة
  // لاحقًا نجيب الـ role من الـ authentication / JWT
  const userRole = "user";

  const userLinks = [
    { name: "Home", path: "/" },
    { name: "My Complaints", path: "/complaints" },
  ];

  const adminLinks = [
    { name: "Dashboard", path: "/admin/dashboard" },
    { name: "Complaints", path: "/admin/complaints" },
    { name: "Analytics", path: "/admin/analytics" },
  ];

  const links = userRole === "admin" ? adminLinks : userLinks;

  return (
    <nav className="w-full border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        {/* Logo / Brand */}
        <Link
          to="/"
          className="text-xl font-bold text-gray-900"
        >
          🤖 AI Facility Management
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-8">
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `text-sm font-medium transition ${
                  isActive
                    ? "text-blue-600"
                    : "text-gray-600 hover:text-blue-600"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </div>

        {/* User */}
        <div className="flex items-center gap-3">
          <button className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200">
            👤
          </button>
        </div>

      </div>
    </nav>
  );
};

export default Navbar;