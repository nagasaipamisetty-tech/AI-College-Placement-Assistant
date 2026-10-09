import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard({ user, onNavigate }) {
  const role = String(user.role || "").toLowerCase();
  const isStudent = role === "student";

  const [summary, setSummary] = useState(null);
  const [studentProfile, setStudentProfile] = useState(null);
  const [matchedJobs, setMatchedJobs] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Student Profile Edit Modal State
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const [profileFormData, setProfileFormData] = useState({
    phone: "",
    bio: "",
    skills: "",
    linkedin_url: "",
    github_url: "",
    hackerrank_url: "",
    leetcode_url: "",
    portfolio_url: ""
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaveMsg, setProfileSaveMsg] = useState("");

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        if (isStudent) {
          const [profileRes, matchRes] = await Promise.all([
            api("/api/students/me").catch(() => null),
            api("/api/students/me/matched-jobs").catch(() => [])
          ]);
          if (active) {
            setStudentProfile(profileRes);
            if (profileRes) {
              setProfileFormData({
                phone: profileRes.phone || "",
                bio: profileRes.bio || "",
                skills: profileRes.skills || "",
                linkedin_url: profileRes.linkedin_url || "",
                github_url: profileRes.github_url || "",
                hackerrank_url: profileRes.hackerrank_url || "",
                leetcode_url: profileRes.leetcode_url || "",
                portfolio_url: profileRes.portfolio_url || ""
              });
            }
            setMatchedJobs(Array.isArray(matchRes) ? matchRes : []);
          }
        } else if (role === "admin") {
          const res = await api("/api/admin/summary");
          if (active) setSummary(res);
        }
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadData();

    return () => {
      active = false;
    };
  }, [role, isStudent]);

  function openEditProfile() {
    if (studentProfile) {
      setProfileFormData({
        phone: studentProfile.phone || "",
        bio: studentProfile.bio || "",
        skills: studentProfile.skills || "",
        linkedin_url: studentProfile.linkedin_url || "",
        github_url: studentProfile.github_url || "",
        hackerrank_url: studentProfile.hackerrank_url || "",
        leetcode_url: studentProfile.leetcode_url || "",
        portfolio_url: studentProfile.portfolio_url || ""
      });
    }
    setProfileSaveMsg("");
    setProfileModalOpen(true);
  }

  async function handleSaveProfile(e) {
    e.preventDefault();
    setSavingProfile(true);
    setProfileSaveMsg("");
    try {
      const updated = await api("/api/students/me", {
        method: "PUT",
        body: profileFormData
      });
      setStudentProfile(updated);
      setProfileSaveMsg("Profile details and social links updated successfully!");
      setTimeout(() => {
        setProfileModalOpen(false);
        setProfileSaveMsg("");
      }, 1200);
    } catch (err) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setSavingProfile(false);
    }
  }

  const shortcuts = [
    {
      title: "🎯 Faculty Eligibility Agent",
      description: "Batch-filter 600+ students, detect skill gaps, and export recruiter shortlists.",
      action: "faculty-agent",
      roles: ["admin", "training", "operator", "company"],
      icon: "🎯"
    },
    {
      title: "AI Prep Plan",
      description: "Match jobs, resolve skill gaps and get a 30/60/90-day unique daily interview plan.",
      action: "prep",
      roles: ["student", "admin", "operator"],
      icon: "⚡"
    },
    {
      title: "Live Off-Campus Openings",
      description: "Real-time hiring drives from Uber, Google, Stripe & LangGraph auto-apply agent.",
      action: "live-market",
      roles: ["student"],
      icon: "🌐"
    },
    {
      title: "Campus Jobs",
      description: "Explore college placement opportunities and eligibility criteria.",
      action: "jobs",
      roles: ["admin", "student", "company", "operator"],
      icon: "💼"
    },
    {
      title: "Student directory",
      description: "Search student profiles, multi-skill filters and placement details.",
      action: "students",
      roles: ["admin", "training", "operator"],
      icon: "◎"
    },
    {
      title: "Import student data",
      description: "Upload a CSV file to update student records.",
      action: "import",
      roles: ["admin"],
      icon: "⇧"
    },
    {
      title: "Applications",
      description: "Review application progress and status.",
      action: "applications",
      roles: ["admin", "student", "operator"],
      icon: "▤"
    },
    {
      title: "Training programs",
      description: "Explore sessions and manage enrollment.",
      action: "training",
      roles: ["admin", "training", "student"],
      icon: "✦"
    }
  ];

  const displayName = studentProfile?.name || user.name || user.email?.split("@")[0] || "there";
  const ineligibleJobs = matchedJobs.filter((j) => !j.eligible);
  const eligibleJobs = matchedJobs.filter((j) => j.eligible);

  return (
    <div className="dashboard">
      <section className="welcome-banner">
        <div>
          <span className="pill light-pill">YOUR PLACEMENT WORKSPACE</span>
          <h2>Welcome back, {displayName}!</h2>
          <p>
            {isStudent
              ? `Department: ${studentProfile?.branch || "Engineering"} • CGPA: ${studentProfile?.cgpa ? Number(studentProfile.cgpa).toFixed(2) : "N/A"} • Batch: ${studentProfile?.graduation_year || 2026}`
              : role === "company"
                ? "Manage your recruitment opportunities and connect with eligible candidates."
                : role === "training"
                  ? "Support student readiness with relevant training programs."
                  : "Here is your workspace for placement activity and student support."}
          </p>
        </div>
        <div className="welcome-art" aria-hidden="true">
          <div className="art-circle circle-a" />
          <div className="art-circle circle-b" />
          <div className="art-card">
            <span>✦</span>
            <strong>PlaceMate</strong>
            <small>Placement AI</small>
          </div>
        </div>
      </section>

      {/* STUDENT PROFILE & SOCIAL PORTFOLIO CARD */}
      {isStudent && studentProfile && (
        <section
          className="panel"
          style={{
            borderTop: "4px solid #4f46e5",
            background: "#ffffff",
            borderRadius: "12px",
            boxShadow: "0 4px 18px rgba(0,0,0,0.04)",
            padding: "20px 24px",
            marginBottom: "20px"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
            <div style={{ display: "flex", gap: "16px", alignItems: "center", flexWrap: "wrap" }}>
              <div
                style={{
                  width: "56px",
                  height: "56px",
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)",
                  color: "#ffffff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "800",
                  fontSize: "22px",
                  boxShadow: "0 4px 10px rgba(79, 70, 229, 0.3)"
                }}
              >
                {studentProfile.name ? studentProfile.name.charAt(0).toUpperCase() : "S"}
              </div>

              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <h3 style={{ margin: 0, fontSize: "1.2rem", color: "#0f172a" }}>{studentProfile.name}</h3>
                  <span style={{ fontFamily: "monospace", fontWeight: "700", background: "#f1f5f9", padding: "2px 8px", borderRadius: "6px", fontSize: "12px", color: "#475569" }}>
                    {studentProfile.roll_number}
                  </span>
                  <span className="role-chip">{studentProfile.branch}</span>
                </div>

                <div style={{ display: "flex", gap: "14px", marginTop: "6px", flexWrap: "wrap", fontSize: "13px", color: "#64748b" }}>
                  <span>✉️ {studentProfile.email}</span>
                  {studentProfile.phone ? (
                    <span>📞 {studentProfile.phone}</span>
                  ) : (
                    <span style={{ color: "#94a3b8" }}>📞 Phone not added</span>
                  )}
                  <span>🎓 CGPA: <strong style={{ color: "#0f172a" }}>{studentProfile.cgpa != null ? Number(studentProfile.cgpa).toFixed(2) : "—"}</strong></span>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={openEditProfile}
              style={{ padding: "8px 16px", borderRadius: "8px", fontWeight: "700", fontSize: "12.5px", borderColor: "#c7d2fe", color: "#4338ca", background: "#eef2ff" }}
            >
              ✏️ Edit Profile & URLs
            </button>
          </div>

          {studentProfile.bio && (
            <p style={{ marginTop: "14px", fontSize: "13.5px", color: "#334155", lineHeight: "1.5", background: "#f8fafc", padding: "10px 14px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <strong>Bio:</strong> {studentProfile.bio}
            </p>
          )}

          {/* Social & Coding Handles List */}
          <div style={{ display: "flex", gap: "10px", marginTop: "16px", flexWrap: "wrap", alignItems: "center", paddingTop: "14px", borderTop: "1px solid #f1f5f9" }}>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "#475569", textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Coding & Profiles:
            </span>

            {studentProfile.linkedin_url ? (
              <a
                href={studentProfile.linkedin_url.startsWith("http") ? studentProfile.linkedin_url : `https://${studentProfile.linkedin_url}`}
                target="_blank"
                rel="noreferrer"
                className="skill-tag"
                style={{ background: "#0a66c2", color: "#ffffff", border: "none", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
              >
                💼 LinkedIn ↗
              </a>
            ) : (
              <button onClick={openEditProfile} className="skill-tag" style={{ border: "1px dashed #94a3b8", color: "#64748b", background: "#ffffff" }}>
                + Add LinkedIn
              </button>
            )}

            {studentProfile.github_url ? (
              <a
                href={studentProfile.github_url.startsWith("http") ? studentProfile.github_url : `https://${studentProfile.github_url}`}
                target="_blank"
                rel="noreferrer"
                className="skill-tag"
                style={{ background: "#24292f", color: "#ffffff", border: "none", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
              >
                🐙 GitHub ↗
              </a>
            ) : (
              <button onClick={openEditProfile} className="skill-tag" style={{ border: "1px dashed #94a3b8", color: "#64748b", background: "#ffffff" }}>
                + Add GitHub
              </button>
            )}

            {studentProfile.hackerrank_url ? (
              <a
                href={studentProfile.hackerrank_url.startsWith("http") ? studentProfile.hackerrank_url : `https://${studentProfile.hackerrank_url}`}
                target="_blank"
                rel="noreferrer"
                className="skill-tag"
                style={{ background: "#00ea64", color: "#0b3b17", fontWeight: "700", border: "none", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
              >
                🟢 HackerRank ↗
              </a>
            ) : (
              <button onClick={openEditProfile} className="skill-tag" style={{ border: "1px dashed #94a3b8", color: "#64748b", background: "#ffffff" }}>
                + Add HackerRank
              </button>
            )}

            {studentProfile.leetcode_url ? (
              <a
                href={studentProfile.leetcode_url.startsWith("http") ? studentProfile.leetcode_url : `https://${studentProfile.leetcode_url}`}
                target="_blank"
                rel="noreferrer"
                className="skill-tag"
                style={{ background: "#ffa116", color: "#451a03", fontWeight: "700", border: "none", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
              >
                🟠 LeetCode ↗
              </a>
            ) : (
              <button onClick={openEditProfile} className="skill-tag" style={{ border: "1px dashed #94a3b8", color: "#64748b", background: "#ffffff" }}>
                + Add LeetCode
              </button>
            )}

            {studentProfile.portfolio_url && (
              <a
                href={studentProfile.portfolio_url.startsWith("http") ? studentProfile.portfolio_url : `https://${studentProfile.portfolio_url}`}
                target="_blank"
                rel="noreferrer"
                className="skill-tag"
                style={{ background: "#7c3aed", color: "#ffffff", border: "none", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none" }}
              >
                🌐 Portfolio / Website ↗
              </a>
            )}
          </div>
        </section>
      )}

      {/* STUDENT SPECIFIC: Ineligibility Warning & Reason Breakdown */}
      {isStudent && ineligibleJobs.length > 0 && (
        <section className="panel" style={{ borderLeft: "5px solid #ef4444", background: "#fff5f5" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #fee2e2", paddingBottom: "10px" }}>
            <div>
              <span className="pill" style={{ background: "#fee2e2", color: "#b91c1c", fontWeight: "bold" }}>
                ⚠️ PLACEMENT ELIGIBILITY ALERT
              </span>
              <h3 style={{ margin: "6px 0 2px 0", color: "#991b1b" }}>
                You are currently Ineligible for {ineligibleJobs.length} Campus Placement Drive(s)
              </h3>
              <p className="muted" style={{ fontSize: "13px" }}>
                The placement agent identified the exact academic cutoffs or skill gap criteria preventing your application:
              </p>
            </div>
            <button
              className="primary-button compact"
              style={{ background: "#dc2626" }}
              onClick={() => onNavigate("prep")}
            >
              View Full Diagnosis →
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "14px" }}>
            {ineligibleJobs.map((job) => (
              <div
                key={job.job_id}
                style={{
                  padding: "12px 16px",
                  background: "#ffffff",
                  borderRadius: "8px",
                  border: "1px solid #fecaca",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <h4 style={{ margin: 0, fontSize: "15px", color: "#111827" }}>
                      {job.title} — <span style={{ color: "#1a73e8", fontWeight: "bold" }}>{job.company_name}</span>
                    </h4>
                    <span className="small-text muted">
                      Cutoff CGPA: {job.minimum_cgpa}+ • Required Branches: {job.eligible_branches || "All"}
                    </span>
                  </div>
                  <span className="status-badge rejected" style={{ fontWeight: "bold" }}>
                    ✕ INELIGIBLE
                  </span>
                </div>

                <div style={{ marginTop: "8px", padding: "8px 12px", background: "#fef2f2", borderRadius: "6px" }}>
                  <strong style={{ fontSize: "12px", color: "#991b1b" }}>Exact Reason(s) Why You Cannot Apply:</strong>
                  <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: "12px", color: "#b91c1c" }}>
                    {(job.eligibility_reasons || []).map((reason, rIdx) => (
                      <li key={rIdx} style={{ margin: "3px 0" }}>
                        <strong>{reason}</strong>
                      </li>
                    ))}
                  </ul>
                </div>

                <div style={{ marginTop: "8px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="small-text" style={{ color: "#4b5563" }}>
                    <strong>Next Action:</strong> Attend remedial workshops or practice on LeetCode.
                  </span>
                  <button
                    className="secondary-button compact"
                    style={{ fontSize: "11px" }}
                    onClick={() => onNavigate("training")}
                  >
                    🎓 View Remedial Training
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Metric Grid */}
      <div className="section-heading">
        <div>
          <span className="eyebrow">OVERVIEW</span>
          <h2>Your placement metrics</h2>
        </div>
        <span className="role-chip">{role}</span>
      </div>

      {loading && <div className="panel">Loading your overview...</div>}
      {error && <div className="notice error">Overview could not be loaded: {error}</div>}

      {!loading && isStudent && (
        <>
          <div className="metric-grid">
            <article className="metric-card">
              <div className="metric-icon blue">🎓</div>
              <p>Your CGPA</p>
              <h3>{studentProfile?.cgpa ? Number(studentProfile.cgpa).toFixed(2) : "—"}</h3>
              <span>Academic Performance</span>
            </article>
            <article className="metric-card" style={{ borderLeft: "4px solid #10b981" }}>
              <div className="metric-icon green">✓</div>
              <p>Eligible Drives</p>
              <h3 style={{ color: "#10b981" }}>{eligibleJobs.length}</h3>
              <span>Ready to Apply</span>
            </article>
            <article className="metric-card" style={{ borderLeft: "4px solid #ef4444" }}>
              <div className="metric-icon red">✕</div>
              <p>Ineligible Drives</p>
              <h3 style={{ color: "#ef4444" }}>{ineligibleJobs.length}</h3>
              <span>Needs Improvement</span>
            </article>
            <article className="metric-card">
              <div className="metric-icon purple">⚡</div>
              <p>Top Match</p>
              <h3>{matchedJobs[0]?.fit_score || 0}%</h3>
              <span>{matchedJobs[0]?.company_name || "None"}</span>
            </article>
          </div>

          {/* ELIGIBLE DRIVES AUTO-APPLY BANNER */}
          {eligibleJobs.length > 0 && (
            <section
              className="panel"
              style={{
                marginTop: "16px",
                background: "linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%)",
                color: "white",
                borderRadius: "10px",
                boxShadow: "0 4px 14px rgba(37, 99, 235, 0.25)"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "20px" }}>⚡</span>
                    <strong style={{ fontSize: "16px" }}>Auto-Apply Option Active: {eligibleJobs.length} Campus Drive(s) Ready</strong>
                  </div>
                  <p style={{ margin: "4px 0 0 0", fontSize: "13px", opacity: 0.9 }}>
                    Your academic performance and skills match all cutoffs. Auto-apply with the LangGraph state machine agent in 1 click!
                  </p>
                </div>
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => onNavigate("jobs")}
                  style={{
                    background: "#ffffff",
                    color: "#1e40af",
                    fontWeight: "bold",
                    fontSize: "13px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
                  }}
                >
                  ⚡ Auto-Apply to All ({eligibleJobs.length}) on Campus Jobs →
                </button>
              </div>
            </section>
          )}
        </>
      )}

      {!loading && !isStudent && (
        <div className="metric-grid">
          <article className="metric-card">
            <div className="metric-icon purple">▤</div>
            <p>Role</p>
            <h3>{role || "User"}</h3>
            <span>Current access level</span>
          </article>
          <article className="metric-card">
            <div className="metric-icon blue">✉</div>
            <p>Account</p>
            <h3>Active</h3>
            <span>{user.email}</span>
          </article>
          <article className="metric-card">
            <div className="metric-icon green">✓</div>
            <p>Workspace</p>
            <h3>Ready</h3>
            <span>AI Placement Assistant</span>
          </article>
          <article className="metric-card">
            <div className="metric-icon orange">✦</div>
            <p>Quick access</p>
            <h3>{shortcuts.filter((item) => item.roles.includes(role)).length}</h3>
            <span>Available sections</span>
          </article>
        </div>
      )}

      <div className="section-heading">
        <div>
          <span className="eyebrow">GET STARTED</span>
          <h2>Quick actions</h2>
        </div>
      </div>

      <div className="shortcut-grid">
        {shortcuts
          .filter((item) => item.roles.includes(role))
          .map((item) => (
            <button
              className="shortcut-card"
              key={item.action}
              onClick={() => onNavigate(item.action)}
            >
              <span className="shortcut-icon">{item.icon}</span>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
              <span className="shortcut-link">Open section →</span>
            </button>
          ))}
      </div>

      {/* EDIT STUDENT PROFILE MODAL */}
      {profileModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(15, 23, 42, 0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px" }}>
          <div className="modal-card" style={{ background: "#ffffff", borderRadius: "12px", maxWidth: "620px", width: "100%", maxHeight: "90vh", overflowY: "auto", padding: "24px", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#4f46e5" }}>CANDIDATE PLACEMENT PROFILE</span>
                <h3 style={{ margin: "4px 0 0 0" }}>✏️ Edit Profile, Contact & Social Links</h3>
              </div>
              <button className="secondary-button" onClick={() => setProfileModalOpen(false)} style={{ padding: "4px 10px" }}>✕</button>
            </div>

            {profileSaveMsg && <div className="notice success">{profileSaveMsg}</div>}

            <form onSubmit={handleSaveProfile} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>📞 Phone Number</label>
                <input
                  type="text"
                  placeholder="+91 98765 43210"
                  value={profileFormData.phone}
                  onChange={(e) => setProfileFormData({ ...profileFormData, phone: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>💼 LinkedIn Profile URL</label>
                <input
                  type="text"
                  placeholder="https://linkedin.com/in/yourname"
                  value={profileFormData.linkedin_url}
                  onChange={(e) => setProfileFormData({ ...profileFormData, linkedin_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🐙 GitHub Profile URL</label>
                <input
                  type="text"
                  placeholder="https://github.com/yourusername"
                  value={profileFormData.github_url}
                  onChange={(e) => setProfileFormData({ ...profileFormData, github_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🟢 HackerRank Profile URL</label>
                <input
                  type="text"
                  placeholder="https://hackerrank.com/yourhandle"
                  value={profileFormData.hackerrank_url}
                  onChange={(e) => setProfileFormData({ ...profileFormData, hackerrank_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🟠 LeetCode Profile URL</label>
                <input
                  type="text"
                  placeholder="https://leetcode.com/yourhandle"
                  value={profileFormData.leetcode_url}
                  onChange={(e) => setProfileFormData({ ...profileFormData, leetcode_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🌐 Personal Portfolio / Website</label>
                <input
                  type="text"
                  placeholder="https://yourportfolio.dev"
                  value={profileFormData.portfolio_url}
                  onChange={(e) => setProfileFormData({ ...profileFormData, portfolio_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Technical Skills (comma separated)</label>
                <input
                  type="text"
                  placeholder="Python, SQL, React, Docker, Embedded C, VLSI"
                  value={profileFormData.skills}
                  onChange={(e) => setProfileFormData({ ...profileFormData, skills: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Professional Bio / Career Objective</label>
                <textarea
                  rows="3"
                  placeholder="Aspiring Software Engineer passionate about backend distributed systems and AI systems..."
                  value={profileFormData.bio}
                  onChange={(e) => setProfileFormData({ ...profileFormData, bio: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", resize: "vertical" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px", borderTop: "1px solid #e2e8f0", paddingTop: "14px" }}>
                <button type="button" className="secondary-button" onClick={() => setProfileModalOpen(false)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={savingProfile}
                  style={{ background: "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)", padding: "10px 22px" }}
                >
                  {savingProfile ? "Saving..." : "💾 Save Profile Details"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}