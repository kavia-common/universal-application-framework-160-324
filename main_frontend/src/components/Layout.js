import React from "react";
import { NavLink } from "react-router-dom";

// PUBLIC_INTERFACE
export default function Layout({ children }) {
  /** Main app shell with sidebar and header */
  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex md:flex-col">
        <div className="h-16 flex items-center px-6 border-b">
          <span className="text-lg font-semibold text-primary">AI Cost Optimizer</span>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          <NavItem to="/" label="Dashboard" icon="📊" end />
          <NavItem to="/scheduler" label="Scheduler" icon="⏰" />
          <NavItem to="/reports" label="Reports" icon="📑" />
        </nav>
        <div className="p-4 border-t text-xs text-gray-500">
          © {new Date().getFullYear()} Kavia Labs
        </div>
      </aside>

      {/* Mobile top nav */}
      <div className="md:hidden fixed top-0 inset-x-0 z-40 bg-white border-b border-gray-200">
        <div className="flex items-center justify-between h-14 px-4">
          <span className="font-semibold text-primary">AI Cost Optimizer</span>
          <div className="flex items-center gap-3 text-sm">
            <NavLink className={mobileLinkClasses} to="/" end>Dashboard</NavLink>
            <NavLink className={mobileLinkClasses} to="/scheduler">Scheduler</NavLink>
            <NavLink className={mobileLinkClasses} to="/reports">Reports</NavLink>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="flex-1">
        <div className="md:hidden h-14" />
        <header className="bg-white border-b border-gray-200">
          <div className="container-responsive py-4 flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-800">AI Cloud Cost Optimizer</h1>
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline text-sm text-gray-600">Environment</span>
              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-50 text-green-700 border border-green-200">Demo</span>
            </div>
          </div>
        </header>
        <div className="container-responsive py-6">{children}</div>
      </main>
    </div>
  );
}

function NavItem({ to, label, icon, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium " +
        (isActive
          ? "bg-blue-50 text-blue-700 border border-blue-200"
          : "text-gray-700 hover:bg-gray-100 hover:text-gray-900")
      }
    >
      <span className="text-base">{icon}</span>
      <span>{label}</span>
    </NavLink>
  );
}

function mobileLinkClasses({ isActive }) {
  return (
    "px-2 py-1 rounded text-sm " +
    (isActive ? "bg-blue-50 text-blue-700" : "text-gray-700")
  );
}
