import { useEffect, useState } from "react";
import {
  clearSession,
  getSavedUser,
  getToken,
  api,
  logout
} from "./api";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Students from "./pages/Students";
import ImportCSV from "./pages/ImportCSV";
import Applications from "./pages/Applications";
import Training from "./pages/Training";
import InterviewPrep from "./pages/InterviewPrep";
import LiveMarket from "./pages/LiveMarket";
import FacultyAgent from "./pages/FacultyAgent";

const navigation = [
  { id: "dashboard", label: "Dashboard", roles: ["admin", "student", "company", "training", "operator"] },
  { id: "faculty-agent", label: "Eligibility Agent", roles: ["admin", "training", "operator", "company"] },
  { id: "prep", label: "AI Prep Plan", roles: ["student", "admin", "operator"] },
  { id: "live-market", label: "Live Off-Campus", roles: ["student"] },
  { id: "jobs", label: "Campus Jobs", roles: ["admin", "student", "company", "operator"] },
  { id: "students", label: "Students", roles: ["admin", "training", "operator"] },
  { id: "import", label: "Import CSV", roles: ["admin"] },
  { id: "applications", label: "Applications", roles: ["admin", "student", "operator"] },
  { id: "training", label: "Training", roles: ["admin", "training", "student"] }
];

const getPageFromHash = () => {
  const raw = window.location.hash.replace(/^#\/?/, "").trim();
  return raw || "dashboard";
};

export default function App() {
  const [user, setUser] = useState(getSavedUser());
  const [page, setPage] = useState(getPageFromHash());
  const [checking, setChecking] = useState(Boolean(getToken()));
  const [notice, setNotice] = useState("");

  const navigateTo = (targetPage) => {
    window.location.hash = targetPage;
    setPage(targetPage);
    setNotice("");
  };

  useEffect(() => {
    const handleHashChange = () => {
      setPage(getPageFromHash());
      setNotice("");
    };

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    let active = true;

    async function validateSession() {
      if (!getToken()) {
        setChecking(false);
        return;
      }

      try {
        const currentUser = await api("/api/auth/me");
        if (active) setUser(currentUser);
      } catch {
        clearSession();
        if (active) setUser(null);
      } finally {
        if (active) setChecking(false);
      }
    }

    validateSession();

    return () => {
      active = false;
    };
  }, []);

  async function handleLogin(email, password) {
    const loggedInUser = await import("./api").then((module) =>
      module.login(email, password)
    );
    setUser(loggedInUser);
    navigateTo(getPageFromHash() !== "dashboard" ? getPageFromHash() : "dashboard");
  }

  function handleLogout() {
    logout();
    setUser(null);
    window.location.hash = "";
    setPage("dashboard");
    setNotice("");
  }

  if (checking) {
    return (
      <main className="loading-screen">
        <div className="spinner" />
        <p>Checking your session...</p>
      </main>
    );
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  const role = String(user.role || "").toLowerCase();
  const allowedNavigation = navigation.filter((item) =>
    item.roles.includes(role)
  );

  function renderPage() {
    switch (page) {
      case "faculty-agent":
        return <FacultyAgent user={user} />;
      case "prep":
        return <InterviewPrep user={user} />;
      case "live-market":
        return <LiveMarket />;
      case "jobs":
        return <Jobs user={user} />;
      case "students":
        return <Students user={user} />;
      case "import":
        return <ImportCSV />;
      case "applications":
        return <Applications user={user} />;
      case "training":
        return <Training user={user} />;
      default:
        return <Dashboard user={user} onNavigate={navigateTo} />;
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">P</div>
          <div>
            <h2>PlaceMate</h2>
            <p>Placement Assistant</p>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="nav-list">
          {allowedNavigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? "active" : ""}`}
              onClick={() => navigateTo(item.id)}
            >
              <span className="nav-dot" />
              {item.label}
              {page === item.id && <span className="nav-arrow">›</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="support-card">
            <div className="support-icon">✦</div>
            <strong>AI Placement Agent</strong>
            <p>On-campus drives & real-time global industry opportunities.</p>
          </div>
          <button className="logout-button" onClick={handleLogout}>
            <span>↪</span> Sign out
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">COLLEGE PLACEMENT PORTAL</p>
            <h1>{navigation.find((item) => item.id === page)?.label || "Dashboard"}</h1>
          </div>

          <div className="topbar-user">
            <div className="avatar">
              {(user.name || user.email || "U").charAt(0).toUpperCase()}
            </div>
            <div className="user-meta">
              <strong>{user.name || user.email}</strong>
              <span>{role}</span>
            </div>
          </div>
        </header>

        {notice && <div className="notice success">{notice}</div>}

        <section className="page-content">{renderPage()}</section>

        <footer className="footer">
          AI College Placement Assistant <span>•</span> Phase 1
        </footer>
      </main>
    </div>
  );
}