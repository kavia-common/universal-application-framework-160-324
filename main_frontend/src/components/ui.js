import React from "react";

// PUBLIC_INTERFACE
export function Button({ children, className = "", ...rest }) {
  return (
    <button
      className={
        "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 " +
        className
      }
      {...rest}
    >
      {children}
    </button>
  );
}

// PUBLIC_INTERFACE
export function Badge({ children, intent = "default", className = "" }) {
  const intentCls = {
    default: "bg-gray-100 text-gray-800 border-gray-200",
    success: "bg-green-50 text-green-700 border-green-200",
    danger: "bg-red-50 text-red-700 border-red-200",
    info: "bg-blue-50 text-blue-700 border-blue-200",
    warning: "bg-yellow-50 text-yellow-700 border-yellow-200",
  }[intent] || "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs border ${intentCls} ${className}`}>
      {children}
    </span>
  );
}
```

Explanation: Replace the starter App with Router and new pages wrapped in Layout.
````edit file="universal-application-framework-160-324/main_frontend/src/App.js"
<<<<<<< SEARCH
import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

// PUBLIC_INTERFACE
function App() {
  const [theme, setTheme] = useState('light');

  // Effect to apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // PUBLIC_INTERFACE
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="App">
      <header className="App-header">
        <button 
          className="theme-toggle" 
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>
          Current theme: <strong>{theme}</strong>
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
=======
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Scheduler from "./pages/Scheduler";
import Reports from "./pages/Reports";

// PUBLIC_INTERFACE
function App() {
  /** Root app component with routing and layout */
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scheduler" element={<Scheduler />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
>>>>>>> REPLACE
