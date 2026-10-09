import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

export default function FacultyAgent({ user }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [customForm, setCustomForm] = useState({
    company_name: "Google",
    job_title: "Software Development Engineer",
    minimum_cgpa: 7.0,
    eligible_branches: "CSE, CSE-AIML, IT, ECE",
    required_skills: "Python, Java, SQL, Data Structures",
    graduation_year: 2027,
    min_skill_match_pct: 40
  });

  const [loading, setLoading] = useState(false);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [activeListTab, setActiveListTab] = useState("eligible"); // "eligible" | "ineligible"
  const [searchFilter, setSearchFilter] = useState("");
  const [remediationMsg, setRemediationMsg] = useState("");
  const [remediating, setRemediating] = useState(false);

  // Load active jobs for easy selection
  useEffect(() => {
    async function loadJobs() {
      try {
        const res = await api("/api/jobs/");
        const jobList = Array.isArray(res) ? res : res.items || [];
        setJobs(jobList);
        if (jobList.length > 0) {
          setSelectedJobId(String(jobList[0].id));
        }
      } catch {
        setJobs([]);
      } finally {
        setJobsLoading(false);
      }
    }
    loadJobs();
  }, []);

  // Run the Faculty Agent Analysis
  const runAnalysis = useCallback(async (useCustom = false) => {
    setLoading(true);
    setRemediationMsg("");

    try {
      let payload = {};
      if (useCustom || selectedJobId === "custom") {
        payload = {
          company_name: customForm.company_name,
          job_title: customForm.job_title,
          minimum_cgpa: Number(customForm.minimum_cgpa) || 0.0,
          eligible_branches: customForm.eligible_branches.split(",").map((b) => b.trim()),
          required_skills: customForm.required_skills.split(",").map((s) => s.trim()),
          graduation_year: customForm.graduation_year ? Number(customForm.graduation_year) : null,
          min_skill_match_pct: Number(customForm.min_skill_match_pct) || 0
        };
      } else {
        payload = {
          job_id: Number(selectedJobId)
        };
      }

      const res = await api("/api/faculty/filter-eligibility", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setAnalysisResult(res);
    } catch (err) {
      alert(`Agent Analysis Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedJobId, customForm]);

  // Trigger initial run when job list loads
  useEffect(() => {
    if (selectedJobId && selectedJobId !== "custom") {
      runAnalysis(false);
    }
  }, [selectedJobId, runAnalysis]);

  // 1-Click Export CSV
  async function handleExportCSV() {
    if (!analysisResult) return;
    try {
      const payload = selectedJobId === "custom"
        ? {
            company_name: customForm.company_name,
            job_title: customForm.job_title,
            minimum_cgpa: Number(customForm.minimum_cgpa),
            eligible_branches: customForm.eligible_branches.split(",").map((b) => b.trim()),
            required_skills: customForm.required_skills.split(",").map((s) => s.trim())
          }
        : { job_id: Number(selectedJobId) };

      const token = localStorage.getItem("placement_token") || "";
      const apiUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
      const res = await fetch(`${apiUrl}/api/faculty/export-shortlist-csv`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Export failed with status ${res.status}`);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Shortlist_${analysisResult.company_name}_${analysisResult.job_title}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  }

  // Auto-Enroll Students in Remediation Training
  async function handleAutoEnrollRemediation(skill, affectedStudents) {
    setRemediating(true);
    setRemediationMsg("");
    try {
      const studentIds = affectedStudents.map((s) => s.student_id);
      const res = await api("/api/faculty/auto-enroll-remediation", {
        method: "POST",
        body: JSON.stringify({
          skill: skill,
          target_job_title: analysisResult?.job_title || "Placement Drive",
          company_name: analysisResult?.company_name || "Hiring Company",
          student_ids: studentIds
        })
      });
      setRemediationMsg(res.message);
    } catch (err) {
      setRemediationMsg(`Failed: ${err.message}`);
    } finally {
      setRemediating(false);
    }
  }

  // Filter students by search term
  const filteredEligible = (analysisResult?.eligible_students || []).filter((s) => {
    const term = searchFilter.toLowerCase();
    return s.name.toLowerCase().includes(term) || s.roll_number.toLowerCase().includes(term) || s.branch.toLowerCase().includes(term);
  });

  const filteredIneligible = (analysisResult?.ineligible_students || []).filter((s) => {
    const term = searchFilter.toLowerCase();
    return s.name.toLowerCase().includes(term) || s.roll_number.toLowerCase().includes(term) || s.branch.toLowerCase().includes(term);
  });

  return (
    <div className="page-stack">
      {/* Header Banner */}
      <div className="section-heading">
        <div>
          <span className="pill light-pill">FACULTY & PLACEMENT CELL AGENT</span>
          <h2>Autonomous Candidate Eligibility & Shortlisting Agent</h2>
          <p className="muted">
            The faculty agent filters the entire student database against target company requirements, detects skill gaps across the cohort, and exports recruiter shortlists.
          </p>
        </div>
      </div>

      {/* Selector & Criteria Panel */}
      <div className="panel" style={{ borderTop: "4px solid #4f46e5", background: "#ffffff", borderRadius: "12px", boxShadow: "0 4px 20px rgba(0,0,0,0.04)", padding: "24px" }}>
        <div className="section-heading compact-heading" style={{ marginBottom: "18px" }}>
          <div>
            <span className="eyebrow" style={{ color: "#6366f1", fontWeight: "700", letterSpacing: "0.8px" }}>RECRUITMENT DRIVE TARGETING & CRITERIA</span>
            <h3 style={{ margin: "4px 0 0 0", fontSize: "1.25rem", color: "#0f172a" }}>Select Target Drive / Company</h3>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Main Dropdown Bar */}
          <div style={{ display: "flex", gap: "14px", alignItems: "stretch", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 340px", position: "relative" }}>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "#64748b", marginBottom: "6px" }}>
                Target Placement Drive:
              </label>
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  borderRadius: "10px",
                  border: "1.5px solid #cbd5e1",
                  background: "#f8fafc",
                  fontSize: "14px",
                  fontWeight: "600",
                  color: "#1e293b",
                  outline: "none",
                  cursor: "pointer",
                  transition: "all 0.2s ease"
                }}
              >
                <optgroup label="Active Placement Drives">
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      🏢 {j.company_name} — {j.title} (Min CGPA: {j.minimum_cgpa}+)
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Custom Evaluation">
                  <option value="custom">⚡ Enter Custom Drive Criteria...</option>
                </optgroup>
              </select>
            </div>

            <div style={{ display: "flex", alignItems: "flex-end", flex: "0 0 auto" }}>
              <button
                type="button"
                className="primary-button"
                disabled={loading}
                onClick={() => runAnalysis(selectedJobId === "custom")}
                style={{
                  padding: "12px 24px",
                  borderRadius: "10px",
                  fontWeight: "700",
                  fontSize: "13.5px",
                  whiteSpace: "nowrap",
                  background: "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)",
                  boxShadow: "0 4px 12px rgba(79, 70, 229, 0.25)",
                  color: "#ffffff",
                  border: "none",
                  cursor: loading ? "not-allowed" : "pointer",
                  transition: "transform 0.15s ease, box-shadow 0.15s ease"
                }}
              >
                {loading ? "⏳ Evaluating 600+ Students..." : "⚡ Run Eligibility Filter Agent"}
              </button>
            </div>
          </div>

          {/* Active Job Meta Snapshot Card */}
          {selectedJobId !== "custom" && (
            (() => {
              const activeJob = jobs.find((j) => String(j.id) === String(selectedJobId));
              if (!activeJob) return null;
              return (
                <div
                  style={{
                    background: "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
                    border: "1px solid #e2e8f0",
                    borderRadius: "10px",
                    padding: "16px 20px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <div
                        style={{
                          width: "36px",
                          height: "36px",
                          borderRadius: "8px",
                          background: "#e0e7ff",
                          color: "#4338ca",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontWeight: "800",
                          fontSize: "16px"
                        }}
                      >
                        {activeJob.company_name ? activeJob.company_name.charAt(0).toUpperCase() : "🏢"}
                      </div>
                      <div>
                        <div style={{ fontWeight: "700", fontSize: "15px", color: "#0f172a" }}>
                          {activeJob.title}
                        </div>
                        <div style={{ fontSize: "13px", color: "#64748b", fontWeight: "500" }}>
                          {activeJob.company_name} {activeJob.location ? `• ${activeJob.location}` : ""} {activeJob.salary_range ? `• 💰 ${activeJob.salary_range}` : ""}
                        </div>
                      </div>
                    </div>

                    <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "600", background: "#ffffff", padding: "4px 10px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                      Drive ID: #{activeJob.id}
                    </span>
                  </div>

                  <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center", paddingTop: "6px", borderTop: "1px dashed #cbd5e1" }}>
                    <span className="pill" style={{ background: "#e0f2fe", color: "#0369a1", fontWeight: "700", fontSize: "12px", padding: "5px 12px", borderRadius: "20px" }}>
                      🎓 Min CGPA: {activeJob.minimum_cgpa}+
                    </span>
                    <span className="pill" style={{ background: "#fef3c7", color: "#92400e", fontWeight: "700", fontSize: "12px", padding: "5px 12px", borderRadius: "20px" }}>
                      🏛️ Branches: {activeJob.eligible_branches || "All Branches"}
                    </span>
                    <span className="pill" style={{ background: "#dcfce7", color: "#166534", fontWeight: "700", fontSize: "12px", padding: "5px 12px", borderRadius: "20px" }}>
                      🛠️ Required: {activeJob.required_skills || "Standard Core Competencies"}
                    </span>
                  </div>
                </div>
              );
            })()
          )}

          {/* Custom Criteria Form Grid */}
          {selectedJobId === "custom" && (
            <div
              style={{
                background: "#f8fafc",
                border: "1.5px dashed #cbd5e1",
                borderRadius: "10px",
                padding: "18px 20px",
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "14px"
              }}
            >
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Company Name</label>
                <input
                  type="text"
                  placeholder="e.g. Google, Tesla, L&T"
                  value={customForm.company_name}
                  onChange={(e) => setCustomForm({ ...customForm, company_name: e.target.value })}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Job Role Title</label>
                <input
                  type="text"
                  placeholder="e.g. Embedded Firmware Engineer"
                  value={customForm.job_title}
                  onChange={(e) => setCustomForm({ ...customForm, job_title: e.target.value })}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Minimum CGPA</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="7.5"
                  value={customForm.minimum_cgpa}
                  onChange={(e) => setCustomForm({ ...customForm, minimum_cgpa: e.target.value })}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Eligible Branches</label>
                <input
                  type="text"
                  placeholder="e.g. CSE, ECE, EEE"
                  value={customForm.eligible_branches}
                  onChange={(e) => setCustomForm({ ...customForm, eligible_branches: e.target.value })}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Required Skills (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. C++, Embedded C, RTOS, Microcontrollers, SPI/I2C"
                  value={customForm.required_skills}
                  onChange={(e) => setCustomForm({ ...customForm, required_skills: e.target.value })}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {remediationMsg && <div className="notice success">{remediationMsg}</div>}

      {/* Analysis Results */}
      {analysisResult && (
        <>
          {/* Metrics Summary Grid */}
          <div className="metric-grid" style={{ margin: "20px 0" }}>
            <article className="metric-card" style={{ borderLeft: "4px solid #6366f1" }}>
              <div className="metric-icon purple">👥</div>
              <p>Total Evaluated</p>
              <h3>{analysisResult.summary.total_evaluated}</h3>
              <span>All Database Students</span>
            </article>

            <article className="metric-card" style={{ borderLeft: "4px solid #10b981" }}>
              <div className="metric-icon green">✓</div>
              <p>Eligible Shortlist</p>
              <h3 style={{ color: "#10b981" }}>{analysisResult.summary.eligible_count}</h3>
              <span style={{ color: "#059669", fontWeight: "600" }}>{analysisResult.summary.eligibility_rate_pct}% Pass Rate</span>
            </article>

            <article className="metric-card" style={{ borderLeft: "4px solid #ef4444" }}>
              <div className="metric-icon orange" style={{ background: "#fef2f2", color: "#ef4444" }}>✕</div>
              <p>Filtered Ineligible</p>
              <h3 style={{ color: "#ef4444" }}>{analysisResult.summary.ineligible_count}</h3>
              <span>Criteria Not Met</span>
            </article>

            <article className="metric-card" style={{ borderLeft: "4px solid #3b82f6" }}>
              <div className="metric-icon blue">🎓</div>
              <p>Shortlist Avg CGPA</p>
              <h3 style={{ color: "#2563eb" }}>{analysisResult.summary.average_eligible_cgpa}</h3>
              <span>Academic Benchmark</span>
            </article>
          </div>

          {/* Department Breakdown & Top Skill Gaps Remediation Box */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px" }}>
            {/* Branch Distribution */}
            <div className="panel">
              <span className="eyebrow" style={{ color: "#1a73e8" }}>DEPARTMENT DISTRIBUTION</span>
              <h3 style={{ margin: "4px 0 12px 0" }}>Eligible Candidates by Branch</h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {Object.entries(analysisResult.summary.branch_distribution || {}).map(([branch, count]) => (
                  <span key={branch} className="pill" style={{ background: "#eff6ff", color: "#1e40af", fontWeight: "bold" }}>
                    {branch}: {count} Students
                  </span>
                ))}
              </div>
            </div>

            {/* Skill Gap Remediation */}
            <div className="panel">
              <span className="eyebrow" style={{ color: "#f59e0b" }}>TRAINING CELL ACTION</span>
              <h3 style={{ margin: "4px 0 12px 0" }}>Top Cohort Skill Gaps</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {(analysisResult.summary.top_skill_gaps || []).map((gap) => (
                  <div key={gap.skill} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 10px", background: "#fffbeb", borderRadius: "6px" }}>
                    <div>
                      <strong>{gap.skill}</strong> — <span className="muted" style={{ fontSize: "12px" }}>{gap.affected_students} candidates missing</span>
                    </div>
                    <button
                      type="button"
                      className="secondary-button compact"
                      style={{ fontSize: "11px" }}
                      disabled={remediating}
                      onClick={() => {
                        const affected = analysisResult.eligible_students.filter((s) =>
                          (s.missing_skills || []).some((m) => m.toLowerCase().includes(gap.skill.toLowerCase()))
                        );
                        handleAutoEnrollRemediation(gap.skill, affected);
                      }}
                    >
                      🎓 Auto-Enroll Training
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Candidate Table Section */}
          <div className="panel">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", borderBottom: "1px solid var(--color-border, #eee)", paddingBottom: "12px" }}>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  className={activeListTab === "eligible" ? "primary-button" : "secondary-button"}
                  onClick={() => setActiveListTab("eligible")}
                >
                  ✓ Eligible Shortlist ({analysisResult.summary.eligible_count})
                </button>
                <button
                  type="button"
                  className={activeListTab === "ineligible" ? "primary-button" : "secondary-button"}
                  onClick={() => setActiveListTab("ineligible")}
                >
                  ✕ Ineligible Candidates ({analysisResult.summary.ineligible_count})
                </button>
              </div>

              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  placeholder="Search name, roll, or branch..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  style={{ width: "220px", padding: "6px 10px", fontSize: "13px" }}
                />
                <button
                  type="button"
                  className="primary-button"
                  style={{ background: "#15803d" }}
                  onClick={handleExportCSV}
                >
                  ⬇ Export Recruiter CSV
                </button>
              </div>
            </div>

            {/* TAB 1: Eligible Table */}
            {activeListTab === "eligible" && (
              <div className="table-scroll" style={{ marginTop: "12px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Roll Number</th>
                      <th>Candidate Name</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Skill Match</th>
                      <th>Matched Skills</th>
                      <th>Identified Gaps</th>
                      <th>Tier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEligible.map((s) => (
                      <tr key={s.student_id}>
                        <td><strong>{s.roll_number}</strong></td>
                        <td>
                          <strong>{s.name}</strong>
                          <div className="muted" style={{ fontSize: "11px" }}>{s.email}</div>
                        </td>
                        <td><span className="role-chip">{s.branch}</span></td>
                        <td><strong>{s.cgpa.toFixed(2)}</strong></td>
                        <td>
                          <span className="score-badge" style={{ fontWeight: "bold" }}>
                            {Math.round(s.skill_match_percentage)}%
                          </span>
                        </td>
                        <td>
                          <div className="tag-list compact">
                            {s.matched_skills.map((m) => (
                              <span key={m} className="skill-tag" style={{ background: "#e6f4ea", color: "#137333", fontSize: "11px" }}>
                                {m}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td>
                          <div className="tag-list compact">
                            {s.missing_skills.length > 0 ? (
                              s.missing_skills.map((m) => (
                                <span key={m} className="skill-tag" style={{ background: "#fce8e6", color: "#c5221f", fontSize: "11px" }}>
                                  ! {m}
                                </span>
                              ))
                            ) : (
                              <span className="muted" style={{ fontSize: "12px" }}>None</span>
                            )}
                          </div>
                        </td>
                        <td>
                          <span className={`status-badge ${s.readiness_tier.includes("Tier 1") ? "approved" : "pending"}`} style={{ fontSize: "11px" }}>
                            {s.readiness_tier}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* TAB 2: Ineligible Table */}
            {activeListTab === "ineligible" && (
              <div className="table-scroll" style={{ marginTop: "12px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Roll Number</th>
                      <th>Candidate Name</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Skill Match</th>
                      <th>Reason(s) for Ineligibility</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredIneligible.map((s) => (
                      <tr key={s.student_id}>
                        <td><strong>{s.roll_number}</strong></td>
                        <td>
                          <strong>{s.name}</strong>
                          <div className="muted" style={{ fontSize: "11px" }}>{s.email}</div>
                        </td>
                        <td><span className="role-chip">{s.branch}</span></td>
                        <td>{s.cgpa.toFixed(2)}</td>
                        <td>{Math.round(s.skill_match_percentage)}%</td>
                        <td>
                          <ul style={{ margin: 0, paddingLeft: "16px", color: "#dc2626", fontSize: "12px" }}>
                            {s.reasons.map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
