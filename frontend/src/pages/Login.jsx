import { useState } from "react";

const DEMO_ACCOUNTS = [
  { label: "Admin", email: "admin@college.edu", password: "Admin@123", desc: "Manage jobs, import students, system summary" },
  { label: "Student", email: "student@college.edu", password: "Student@123", desc: "View jobs, check eligibility, apply, enroll in training" },
  { label: "Recruiter", email: "recruiter@google.com", password: "Company@123", desc: "Post new placement job opportunities" },
  { label: "Operator", email: "operator@college.edu", password: "Operator@123", desc: "View stats, manage student status" },
  { label: "Trainer", email: "trainer@college.edu", password: "Trainer@123", desc: "Create training sessions and bootcamps" }
];

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("admin@college.edu");
  const [password, setPassword] = useState("Admin@123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await onLogin(email.trim(), password);
    } catch (err) {
      setError(err.message || "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  function selectDemoAccount(acc) {
    setEmail(acc.email);
    setPassword(acc.password);
    setError("");
  }

  return (
    <main className="login-screen">
      <div className="login-decoration decoration-one" />
      <div className="login-decoration decoration-two" />

      <section className="login-brand-panel">
        <div className="login-brand">
          <div className="brand-mark large">P</div>
          <span>PlaceMate</span>
        </div>

        <div className="login-intro">
          <span className="pill light-pill">YOUR CAREER STARTS HERE</span>
          <h1>Turn your potential into your next opportunity.</h1>
          <p>
            A unified workspace for campus recruitment, student eligibility,
            applications, and career training.
          </p>

          <div className="login-feature-list">
            <div><span>✓</span> Discover placement opportunities</div>
            <div><span>✓</span> Track applications in one place</div>
            <div><span>✓</span> Build skills for career readiness</div>
          </div>
        </div>

        <p className="login-panel-footer">AI College Placement Assistant · Phase 1</p>
      </section>

      <section className="login-form-panel">
        <form className="login-card" onSubmit={handleSubmit}>
          <div className="mobile-brand">
            <div className="brand-mark">P</div>
            <strong>PlaceMate</strong>
          </div>

          <span className="eyebrow">WELCOME BACK</span>
          <h2>Sign in to your workspace</h2>
          <p className="muted">
            Enter your college portal credentials to continue.
          </p>

          {error && <div className="notice error">{error}</div>}

          <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@college.edu"
            autoComplete="username"
            required
          />

          <div className="label-row">
            <label htmlFor="password">Password</label>
          </div>

          <div className="password-field">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword((value) => !value)}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          <button className="primary-button login-submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
            {!loading && <span>→</span>}
          </button>

          <div className="demo-box">
            <strong>Quick Demo Logins</strong>
            <p className="muted small-text">Click any role to fill credentials:</p>
            <div className="tag-list" style={{ marginTop: "8px", gap: "6px" }}>
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  type="button"
                  key={acc.label}
                  className="secondary-button compact"
                  style={{ fontSize: "12px", padding: "4px 8px" }}
                  onClick={() => selectDemoAccount(acc)}
                >
                  {acc.label}
                </button>
              ))}
            </div>
          </div>
        </form>
      </section>
    </main>
  );
}