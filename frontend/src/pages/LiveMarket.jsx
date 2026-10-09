import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

export default function LiveMarket() {
  const [opportunities, setOpportunities] = useState([]);
  const [codingProblems, setCodingProblems] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState("python");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [receiptsLoading, setReceiptsLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [activeTab, setActiveTab] = useState("jobs"); // "jobs" | "receipts" | "practice"

  // Auto-Apply Agent Modal State
  const [agentModalOpen, setAgentModalOpen] = useState(false);
  const [currentJobApplying, setCurrentJobApplying] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [agentExecuting, setAgentExecuting] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState(null);

  // Resume Modal State
  const [resumeModalOpen, setResumeModalOpen] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const loadOpportunities = useCallback(async (queryText = "") => {
    setLoading(true);
    setError("");

    try {
      const url = queryText.trim()
        ? `/api/live/opportunities?search=${encodeURIComponent(queryText.trim())}`
        : "/api/live/opportunities";
      const result = await api(url);
      setOpportunities(result.items || []);
    } catch (err) {
      setError(err.message || "Failed to load live internet job feed.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPracticeProblems = useCallback(async (skillName) => {
    setPracticeLoading(true);
    try {
      const result = await api(`/api/live/practice?skill=${encodeURIComponent(skillName)}`);
      setCodingProblems(result.problems || []);
    } catch {
      setCodingProblems([]);
    } finally {
      setPracticeLoading(false);
    }
  }, []);

  const loadReceipts = useCallback(async () => {
    setReceiptsLoading(true);
    try {
      const result = await api("/api/auto-apply/receipts");
      setReceipts(Array.isArray(result) ? result : []);
    } catch {
      setReceipts([]);
    } finally {
      setReceiptsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOpportunities(search);
  }, [loadOpportunities, search]);

  useEffect(() => {
    loadPracticeProblems(selectedSkill);
  }, [loadPracticeProblems, selectedSkill]);

  useEffect(() => {
    if (activeTab === "receipts") {
      loadReceipts();
    }
  }, [activeTab, loadReceipts]);

  function handleSearchSubmit(e) {
    e.preventDefault();
    loadOpportunities(search);
  }

  // Trigger LangGraph Autonomous Auto-Apply Agent
  async function triggerAutoApply(job) {
    setCurrentJobApplying(job);
    setAgentModalOpen(true);
    setAgentExecuting(true);
    setAgentState({
      step: 1,
      statusText: "LangGraph StateGraph: Evaluating CGPA eligibility & technical skill taxonomy match...",
      data: null
    });
    setError("");

    try {
      const response = await api("/api/auto-apply/job", {
        method: "POST",
        body: JSON.stringify({
          job_id: String(job.id),
          job_title: job.title,
          company_name: job.company_name,
          job_url: job.apply_url || "",
          required_skills: job.required_skills || []
        })
      });

      setAgentState({
        step: 3,
        statusText: response.success
          ? "Autonomous Submission Complete! Confirmation Receipt Generated."
          : "Skill Match below threshold. Skipped submission.",
        data: response
      });
      loadReceipts();
    } catch (err) {
      setAgentState({
        step: 3,
        statusText: `Execution stopped: ${err.message}`,
        error: err.message
      });
    } finally {
      setAgentExecuting(false);
    }
  }

  // Generate Tailored LaTeX Resume
  async function handleGenerateResume(job) {
    setResumeModalOpen(true);
    setResumeLoading(true);
    setResumeData(null);
    setCopySuccess(false);

    try {
      const res = await api("/api/resume/generate-latex", {
        method: "POST",
        body: JSON.stringify({
          job_id: String(job.id),
          job_title: job.title,
          company_name: job.company_name,
          required_skills: job.required_skills || []
        })
      });
      setResumeData(res);
    } catch (err) {
      setError(err.message || "Failed to generate tailored LaTeX resume.");
    } finally {
      setResumeLoading(false);
    }
  }

  function handleCopyLaTeX() {
    if (!resumeData?.tex_content) return;
    navigator.clipboard.writeText(resumeData.tex_content);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2500);
  }

  function handleDownloadTex() {
    if (!resumeData?.tex_content) return;
    const blob = new Blob([resumeData.tex_content], { type: "text/x-tex" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = resumeData.filename || "Tailored_Resume.tex";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-stack">
      {/* Top Banner */}
      <div className="section-heading">
        <div>
          <span className="pill light-pill">VERIFIED OFF-CAMPUS OPPORTUNITIES</span>
          <h2>Live Off-Campus Opportunities</h2>
          <p className="muted">
            Authentic job openings at top tech companies (Google, Microsoft, NVIDIA, Qualcomm, L&T, Stripe). Use the AI agent to auto-apply or generate a tailored ATS resume.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button className="secondary-button" onClick={() => loadOpportunities(search)}>
            ⚡ Refresh Live Feed
          </button>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}
      {successMsg && <div className="notice success">{successMsg}</div>}

      {/* Tab Switcher */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px" }}>
        <button
          className={activeTab === "jobs" ? "primary-button" : "secondary-button"}
          onClick={() => setActiveTab("jobs")}
        >
          🌐 Live Jobs ({opportunities.length})
        </button>
        <button
          className={activeTab === "receipts" ? "primary-button" : "secondary-button"}
          onClick={() => {
            setActiveTab("receipts");
            loadReceipts();
          }}
        >
          ⚡ Application Receipts ({receipts.length})
        </button>
        <button
          className={activeTab === "practice" ? "primary-button" : "secondary-button"}
          onClick={() => setActiveTab("practice")}
        >
          💻 Live LeetCode Challenges
        </button>
      </div>

      {/* TAB 1: Live Jobs Feed (Compact Cards) */}
      {activeTab === "jobs" && (
        <>
          {/* Search Bar */}
          <div className="panel" style={{ padding: "16px 20px", marginBottom: "16px", borderRadius: "10px" }}>
            <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <div style={{ flex: "1 1 360px" }}>
                <input
                  type="text"
                  placeholder="Search jobs by company (Google, NVIDIA, Qualcomm), skill (Python, VLSI, CAD), or role..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  style={{ width: "100%", padding: "10px 14px", borderRadius: "8px", border: "1px solid #d1d5db", fontSize: "14px", boxSizing: "border-box" }}
                />
              </div>
              <button
                type="submit"
                className="primary-button"
                style={{ padding: "10px 22px", borderRadius: "8px", fontWeight: "600", fontSize: "13px", whiteSpace: "nowrap" }}
              >
                🔍 Search Openings
              </button>
              {search && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setSearch("");
                    loadOpportunities("");
                  }}
                  style={{ padding: "10px 16px", borderRadius: "8px", fontSize: "13px" }}
                >
                  ✕ Clear
                </button>
              )}
            </form>
          </div>

          {loading ? (
            <p className="muted">Fetching verified live off-campus opportunities...</p>
          ) : opportunities.length === 0 ? (
            <div className="empty-state compact-empty">
              <div className="empty-icon">🌐</div>
              <h3>No matching live opportunities found</h3>
              <p>Try refining your search keyword.</p>
            </div>
          ) : (
            /* COMPACT CARD GRID */
            <div className="job-grid">
              {opportunities.map((item) => (
                <article
                  className="job-card"
                  key={item.id}
                  style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", borderRadius: "12px", border: "1px solid #e2e8f0" }}
                >
                  <div>
                    <div className="job-card-top">
                      <div className="company-avatar" style={{ background: "#4f46e5", color: "white", fontWeight: "800" }}>
                        {item.company_name.charAt(0).toUpperCase()}
                      </div>
                      <span className="status-badge approved" style={{ fontWeight: "700" }}>
                        {item.salary_range}
                      </span>
                    </div>

                    <h3 style={{ fontSize: "16px", marginTop: "10px" }}>{item.title}</h3>
                    <p className="company-name" style={{ fontWeight: 700, color: "#4f46e5" }}>
                      {item.company_name} • <span className="muted">{item.location}</span>
                    </p>

                    <div className="job-details" style={{ margin: "8px 0" }}>
                      <span>Mode: {item.work_mode}</span>
                      <span>Batch: {item.hiring_batch || "2026 / 2027"}</span>
                    </div>

                    <p className="job-description" style={{ fontSize: "13px", color: "var(--color-text-muted)" }}>
                      {item.description}
                    </p>

                    {/* Required Skills */}
                    {(item.required_skills || []).length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
                        {item.required_skills.slice(0, 5).map((sk) => (
                          <span key={sk} className="pill" style={{ background: "#e0e7ff", color: "#3730a3", fontWeight: "700", fontSize: "11px" }}>
                            {sk}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div style={{ marginTop: "14px", paddingTop: "12px", borderTop: "1px solid #f1f5f9", display: "flex", flexDirection: "column", gap: "6px" }}>
                    <button
                      type="button"
                      className="primary-button full-button"
                      style={{ background: "#4f46e5", color: "white", fontWeight: "700" }}
                      onClick={() => triggerAutoApply(item)}
                    >
                      ⚡ Auto-Apply Agent
                    </button>
                    <button
                      type="button"
                      className="secondary-button full-button"
                      style={{ fontWeight: "600" }}
                      onClick={() => handleGenerateResume(item)}
                    >
                      📄 Tailor .tex Resume
                    </button>
                    <a
                      href={item.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="secondary-button"
                      style={{ textAlign: "center", textDecoration: "none", fontSize: "12px", color: "#475569" }}
                    >
                      Direct Portal ↗
                    </a>
                  </div>
                </article>
              ))}
            </div>
          )}
        </>
      )}

      {/* TAB 2: Application Receipts */}
      {activeTab === "receipts" && (
        <div className="panel">
          <div className="section-heading compact-heading">
            <div>
              <span className="eyebrow">APPLICATION RECEIPTS & CONFIRMATIONS</span>
              <h3>Off-Campus Applications History</h3>
              <p className="muted">Verified application receipts, synthesized cover letters, and official submission timestamps.</p>
            </div>
          </div>

          {receiptsLoading ? (
            <p className="muted">Loading receipts...</p>
          ) : receipts.length === 0 ? (
            <div className="empty-state compact-empty">
              <div className="empty-icon">⚡</div>
              <h3>No submitted applications yet</h3>
              <p>Use the ⚡ Auto-Apply Agent button on any job card to get started.</p>
            </div>
          ) : (
            <div className="table-scroll" style={{ marginTop: "12px" }}>
              <table>
                <thead>
                  <tr>
                    <th>Confirmation ID</th>
                    <th>Company & Role</th>
                    <th>Fit Score</th>
                    <th>Status</th>
                    <th>Submitted At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {receipts.map((r) => (
                    <tr key={r.id}>
                      <td><code style={{ color: "#4f46e5", fontWeight: "bold" }}>{r.confirmation_id}</code></td>
                      <td><strong>{r.job_title}</strong> — {r.company_name}</td>
                      <td><span className="pill approved" style={{ fontWeight: "bold" }}>{r.match_score}% Fit</span></td>
                      <td>
                        <span className={`status-badge ${r.status === "SUBMITTED" ? "approved" : "rejected"}`}>
                          {r.status}
                        </span>
                      </td>
                      <td className="muted" style={{ fontSize: "12px" }}>{new Date(r.created_at).toLocaleString()}</td>
                      <td>
                        <button
                          className="secondary-button compact"
                          onClick={() => setSelectedReceipt(r)}
                        >
                          View Receipt
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Coding & Practice */}
      {activeTab === "practice" && (
        <div className="panel">
          <div className="section-heading compact-heading">
            <div>
              <span className="eyebrow">TECH INTERVIEW ROUND 1 PREPARATION</span>
              <h3>Live LeetCode & Coding Tracks</h3>
              <p className="muted">Curated algorithmic coding questions frequently asked in technical screening rounds for live jobs.</p>
            </div>
          </div>

          {/* Skill Selector */}
          <div style={{ display: "flex", gap: "8px", margin: "16px 0", flexWrap: "wrap" }}>
            {["python", "java", "sql", "react", "data structures"].map((s) => (
              <button
                key={s}
                className={selectedSkill === s ? "primary-button" : "secondary-button"}
                style={{ textTransform: "capitalize", fontSize: "13px" }}
                onClick={() => setSelectedSkill(s)}
              >
                {s}
              </button>
            ))}
          </div>

          {practiceLoading ? (
            <p className="muted">Loading problems...</p>
          ) : (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Problem Title</th>
                    <th>Topic / Category</th>
                    <th>Difficulty</th>
                    <th>Practice Link</th>
                  </tr>
                </thead>
                <tbody>
                  {codingProblems.map((p, idx) => (
                    <tr key={idx}>
                      <td><strong>{p.title}</strong></td>
                      <td><span className="role-chip">{p.category}</span></td>
                      <td>
                        <span className={`status-badge ${p.difficulty === "Easy" ? "approved" : p.difficulty === "Medium" ? "pending" : "rejected"}`}>
                          {p.difficulty}
                        </span>
                      </td>
                      <td>
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="secondary-button compact"
                          style={{ textDecoration: "none", display: "inline-block" }}
                        >
                          Solve on LeetCode ↗
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* MODAL 1: AUTONOMOUS AGENT EXECUTION MODAL */}
      {agentModalOpen && currentJobApplying && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="modal-card" style={{ background: "white", borderRadius: "12px", maxWidth: "600px", width: "90%", maxHeight: "85vh", overflowY: "auto", padding: "24px", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #eee", paddingBottom: "12px", marginBottom: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "24px" }}>⚡</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: "18px" }}>LangGraph Auto-Apply Agent</h3>
                  <p className="muted" style={{ margin: 0, fontSize: "12px" }}>Autonomous multi-agent execution pipeline</p>
                </div>
              </div>
              {!agentExecuting && (
                <button className="secondary-button compact" onClick={() => setAgentModalOpen(false)}>✕</button>
              )}
            </div>

            <div style={{ margin: "14px 0", padding: "12px 16px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <strong style={{ fontSize: "14px", color: "#1e40af" }}>{currentJobApplying.title}</strong>
              <p className="muted" style={{ margin: "2px 0 0 0", fontSize: "12px" }}>{currentJobApplying.company_name} • {currentJobApplying.location}</p>
            </div>

            {agentExecuting && (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px", margin: "20px 0" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <div className="spinner" style={{ width: "24px", height: "24px", borderWidth: "3px" }} />
                  <span style={{ fontSize: "14px", fontWeight: "600", color: "#4f46e5" }}>
                    {agentState?.statusText}
                  </span>
                </div>
              </div>
            )}

            {!agentExecuting && agentState?.data && (
              <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                <div style={{ padding: "12px", background: agentState.data.success ? "#f0fdf4" : "#fef2f2", borderRadius: "8px", border: `1px solid ${agentState.data.success ? "#bbf7d0" : "#fecaca"}` }}>
                  <strong style={{ color: agentState.data.success ? "#166534" : "#991b1b" }}>
                    {agentState.data.success ? "✓ Auto-Apply Successful" : "✕ Skipped by Agent"}
                  </strong>
                  <p style={{ margin: "4px 0 0 0", fontSize: "13px" }}>{agentState.data.message}</p>
                </div>

                {agentState.data.confirmation_id && (
                  <div style={{ background: "#f1f5f9", padding: "10px", borderRadius: "6px", fontFamily: "monospace", fontSize: "12px" }}>
                    <strong>Confirmation ID: </strong>{agentState.data.confirmation_id}
                  </div>
                )}

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px", marginTop: "12px" }}>
                  <button className="primary-button" onClick={() => setAgentModalOpen(false)}>
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 2: RECEIPT DETAILS MODAL */}
      {selectedReceipt && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="modal-card" style={{ background: "white", borderRadius: "12px", maxWidth: "650px", width: "90%", maxHeight: "85vh", overflowY: "auto", padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #eee", paddingBottom: "12px", marginBottom: "16px" }}>
              <h3>Application Receipt #{selectedReceipt.confirmation_id}</h3>
              <button className="secondary-button compact" onClick={() => setSelectedReceipt(null)}>✕</button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
              <div><strong>Company:</strong> {selectedReceipt.company_name}</div>
              <div><strong>Role:</strong> {selectedReceipt.job_title}</div>
              <div><strong>Match Score:</strong> <span className="pill approved">{selectedReceipt.match_score}% Fit</span></div>
              <div><strong>Status:</strong> {selectedReceipt.status}</div>

              {selectedReceipt.tailored_cover_letter && (
                <div style={{ marginTop: "10px" }}>
                  <strong>Synthesized Cover Letter:</strong>
                  <pre style={{ background: "#f8fafc", padding: "12px", borderRadius: "8px", fontSize: "12px", whiteSpace: "pre-wrap", marginTop: "6px" }}>
                    {selectedReceipt.tailored_cover_letter}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: TAILORED RESUME MODAL */}
      {resumeModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="modal-card" style={{ background: "white", borderRadius: "12px", maxWidth: "750px", width: "92%", maxHeight: "90vh", overflowY: "auto", padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #eee", paddingBottom: "12px", marginBottom: "16px" }}>
              <div>
                <span className="eyebrow">AI RESUME COMPILER</span>
                <h3 style={{ margin: "2px 0 0 0" }}>ATS LaTeX Resume</h3>
              </div>
              <button className="secondary-button compact" onClick={() => setResumeModalOpen(false)}>✕</button>
            </div>

            {resumeLoading ? (
              <p className="muted">Generating tailored LaTeX resume...</p>
            ) : resumeData ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button className="secondary-button compact" onClick={handleCopyLaTeX}>
                    {copySuccess ? "✓ Copied LaTeX!" : "📋 Copy LaTeX"}
                  </button>
                  <button className="primary-button compact" onClick={handleDownloadTex}>
                    ⬇ Download .tex File
                  </button>
                </div>

                <textarea
                  readOnly
                  value={resumeData.tex_content}
                  style={{ width: "100%", height: "340px", fontFamily: "monospace", fontSize: "12px", padding: "12px", backgroundColor: "#1e1e1e", color: "#d4d4d4", borderRadius: "8px" }}
                />
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
