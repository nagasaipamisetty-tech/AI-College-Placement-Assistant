import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const emptyJob = {
  title: "",
  company_name: "",
  description: "",
  required_skills: "",
  minimum_cgpa: "0",
  eligible_branches: "",
  graduation_year: ""
};

export default function Jobs({ user }) {
  const role = String(user.role || "").toLowerCase();
  const isStudent = role === "student";

  const [jobs, setJobs] = useState([]);
  const [studentProfile, setStudentProfile] = useState(null);
  const [matchedJobData, setMatchedJobData] = useState({});
  const [myApplications, setMyApplications] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [form, setForm] = useState(emptyJob);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [activeFilter, setActiveFilter] = useState("all"); // "all" | "eligible" | "applied"

  // Auto-Apply Agent Modal State (Single)
  const [agentModalOpen, setAgentModalOpen] = useState(false);
  const [currentJobApplying, setCurrentJobApplying] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [agentExecuting, setAgentExecuting] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState(null);

  // Bulk Auto-Apply Modal State (All Eligible)
  const [bulkModalOpen, setBulkModalOpen] = useState(false);
  const [bulkExecuting, setBulkExecuting] = useState(false);
  const [bulkQueue, setBulkQueue] = useState([]);
  const [bulkResults, setBulkResults] = useState([]);
  const [bulkCurrentIndex, setBulkCurrentIndex] = useState(0);

  // Resume Generator Modal State
  const [resumeModalOpen, setResumeModalOpen] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [resumeViewTab, setResumeViewTab] = useState("code");
  const [copySuccess, setCopySuccess] = useState(false);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      if (isStudent) {
        const [profileRes, matchRes, appsRes, receiptsRes] = await Promise.all([
          api("/api/students/me").catch(() => null),
          api("/api/students/me/matched-jobs").catch(() => []),
          api("/api/applications/mine").catch(() => []),
          api("/api/auto-apply/receipts").catch(() => [])
        ]);

        setStudentProfile(profileRes);

        const matches = Array.isArray(matchRes) ? matchRes : [];
        const matchMap = {};
        for (const m of matches) {
          matchMap[m.job_id] = m;
        }
        setMatchedJobData(matchMap);
        setMyApplications(Array.isArray(appsRes) ? appsRes : []);
        setReceipts(Array.isArray(receiptsRes) ? receiptsRes : []);

        const jobsRes = await api("/api/jobs/");
        setJobs(Array.isArray(jobsRes) ? jobsRes : jobsRes.items || []);
      } else {
        const endpoint = role === "admin" ? "/api/admin/jobs/pending" : "/api/jobs/";
        const result = await api(endpoint);
        setJobs(Array.isArray(result) ? result : result.items || []);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [role, isStudent]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  function updateField(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value
    }));
  }

  async function submitJob(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      await api("/api/jobs/", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          minimum_cgpa: Number(form.minimum_cgpa || 0),
          graduation_year: form.graduation_year ? Number(form.graduation_year) : null
        })
      });

      setMessage("Job opportunity submitted successfully.");
      setForm(emptyJob);
      await loadJobs();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function reviewJob(id, decision) {
    setError("");
    setMessage("");

    try {
      await api(`/api/admin/jobs/${id}/${decision}`, {
        method: "POST"
      });

      setMessage(`Job ${decision}ed successfully.`);
      await loadJobs();
    } catch (err) {
      setError(err.message);
    }
  }

  // Maps to check application status
  const appliedJobIds = new Set(myApplications.map((a) => a.job_id));
  const receiptsMap = {};
  for (const r of receipts) {
    receiptsMap[String(r.job_id)] = r;
  }

  // Single Auto-Apply Trigger (LangGraph)
  async function triggerAutoApply(job) {
    setCurrentJobApplying(job);
    setAgentModalOpen(true);
    setAgentExecuting(true);
    setAgentState({
      step: 1,
      statusText: "LangGraph StateGraph: Evaluating profile eligibility and CGPA cutoff match...",
      data: null
    });
    setError("");
    setMessage("");

    try {
      const response = await api("/api/auto-apply/job", {
        method: "POST",
        body: JSON.stringify({
          job_id: String(job.id),
          job_title: job.title,
          company_name: job.company_name,
          job_url: "",
          required_skills: job.required_skills ? job.required_skills.split(",").map((s) => s.trim()) : []
        })
      });

      setAgentState({
        step: 3,
        statusText: response.success
          ? "Autonomous Submission Complete! Official Receipt Generated."
          : "Skill Match below threshold. Skipped submission.",
        data: response
      });

      await loadJobs();
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

  // Auto-Apply to ALL Eligible Jobs (LangGraph Batch Orchestration)
  async function handleAutoApplyAllEligible() {
    const eligibleUnapplied = jobs.filter((job) => {
      const match = matchedJobData[job.id];
      const isEligible = match?.eligible ?? (studentProfile?.cgpa >= (job.minimum_cgpa || 0));
      const hasApplied = appliedJobIds.has(job.id) || receiptsMap[String(job.id)]?.status === "SUBMITTED";
      return isEligible && !hasApplied;
    });

    if (eligibleUnapplied.length === 0) {
      setMessage("You have already auto-applied to all eligible campus opportunities!");
      return;
    }

    setBulkQueue(eligibleUnapplied);
    setBulkResults([]);
    setBulkCurrentIndex(0);
    setBulkModalOpen(true);
    setBulkExecuting(true);
    setError("");

    const results = [];
    for (let i = 0; i < eligibleUnapplied.length; i++) {
      const job = eligibleUnapplied[i];
      setBulkCurrentIndex(i);

      try {
        const res = await api("/api/auto-apply/job", {
          method: "POST",
          body: JSON.stringify({
            job_id: String(job.id),
            job_title: job.title,
            company_name: job.company_name,
            job_url: "",
            required_skills: job.required_skills ? job.required_skills.split(",").map((s) => s.trim()) : []
          })
        });

        results.push({
          job,
          success: res.success,
          confirmation_id: res.confirmation_id,
          match_score: res.match_score,
          cover_letter: res.tailored_cover_letter
        });
      } catch (err) {
        results.push({
          job,
          success: false,
          error: err.message
        });
      }
      setBulkResults([...results]);
    }

    setBulkExecuting(false);
    setMessage(`⚡ Successfully auto-applied to ${results.filter(r => r.success).length} eligible campus drives! All official confirmation receipts recorded.`);
    await loadJobs();
  }

  // Generate Tailored LaTeX Resume for Campus Job
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
          required_skills: job.required_skills ? job.required_skills.split(",").map((s) => s.trim()) : []
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
    a.download = resumeData.filename || "Tailored_Campus_Resume.tex";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Eligible & unapplied calculation
  const eligibleUnappliedCount = isStudent
    ? jobs.filter((j) => {
        const match = matchedJobData[j.id];
        const isEligible = match?.eligible ?? (studentProfile?.cgpa >= (j.minimum_cgpa || 0));
        const hasApplied = appliedJobIds.has(j.id) || receiptsMap[String(j.id)]?.status === "SUBMITTED";
        return isEligible && !hasApplied;
      }).length
    : 0;

  const filteredJobs = jobs.filter((job) => {
    if (!isStudent) return true;
    const match = matchedJobData[job.id];
    const isEligible = match?.eligible ?? (studentProfile?.cgpa >= (job.minimum_cgpa || 0));
    const hasApplied = appliedJobIds.has(job.id) || receiptsMap[String(job.id)]?.status === "SUBMITTED";

    if (activeFilter === "eligible") return isEligible && !hasApplied;
    if (activeFilter === "applied") return hasApplied;
    return true;
  });

  return (
    <div className="page-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">CAMPUS PLACEMENT DRIVES</span>
          <h2>{role === "admin" ? "Placement Opportunities Management" : "Campus Job Opportunities"}</h2>
          <p className="muted">
            {isStudent
              ? `Your Profile: ${studentProfile?.branch || "Engineering"} • CGPA: ${studentProfile?.cgpa ? studentProfile.cgpa.toFixed(2) : "N/A"}. Opportunities are filtered against your criteria.`
              : "Explore available campus drives and their eligibility cutoffs."}
          </p>
        </div>

        {/* TOP ACTION BAR: AUTO-APPLY ALL ELIGIBLE BUTTON & REFRESH */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          {isStudent && (
            <button
              type="button"
              className="primary-button"
              style={{
                background: eligibleUnappliedCount > 0 ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)",
                fontWeight: "bold",
                boxShadow: "0 2px 8px rgba(0,0,0,0.12)"
              }}
              onClick={handleAutoApplyAllEligible}
              disabled={loading || eligibleUnappliedCount === 0}
            >
              {eligibleUnappliedCount > 0
                ? `⚡ Auto-Apply to All Eligible (${eligibleUnappliedCount})`
                : "✓ All Eligible Jobs Applied"}
            </button>
          )}

          <button className="secondary-button" onClick={loadJobs}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {/* STUDENT 1-CLICK PROMINENT HERO AUTO-APPLY BANNER */}
      {isStudent && eligibleUnappliedCount > 0 && (
        <div
          style={{
            padding: "18px 24px",
            background: "linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%)",
            color: "white",
            borderRadius: "12px",
            boxShadow: "0 6px 18px rgba(37, 99, 235, 0.3)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "16px"
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ fontSize: "22px" }}>⚡</span>
              <strong style={{ fontSize: "17px", letterSpacing: "0.2px" }}>
                Auto-Apply Option: {eligibleUnappliedCount} Eligible Campus Opportunity{eligibleUnappliedCount > 1 ? "ies" : ""} Ready
              </strong>
              <span
                style={{
                  background: "#10b981",
                  color: "#ffffff",
                  padding: "3px 10px",
                  borderRadius: "14px",
                  fontSize: "12px",
                  fontWeight: "bold"
                }}
              >
                100% Eligible
              </span>
            </div>
            <p style={{ margin: "6px 0 0 0", fontSize: "13px", opacity: 0.92, lineHeight: "1.5" }}>
              You meet all CGPA cutoffs, eligible branches, and required technical skills. Click below to let the LangGraph agent autonomously synthesize tailored statements, submit applications, and generate official verification receipts.
            </p>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={handleAutoApplyAllEligible}
            style={{
              background: "#ffffff",
              color: "#1e40af",
              fontWeight: "bold",
              fontSize: "14px",
              padding: "10px 20px",
              boxShadow: "0 3px 10px rgba(0,0,0,0.2)",
              whiteSpace: "nowrap"
            }}
          >
            ⚡ Auto-Apply to All Eligible Jobs ({eligibleUnappliedCount}) →
          </button>
        </div>
      )}

      {/* Student Filter Tabs */}
      {isStudent && (
        <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--color-border, #e0e0e0)", paddingBottom: "10px" }}>
          <button
            type="button"
            className={activeFilter === "all" ? "primary-button" : "secondary-button"}
            onClick={() => setActiveFilter("all")}
          >
            All Drives ({jobs.length})
          </button>
          <button
            type="button"
            className={activeFilter === "eligible" ? "primary-button" : "secondary-button"}
            onClick={() => setActiveFilter("eligible")}
          >
            ⚡ Eligible to Auto-Apply ({eligibleUnappliedCount})
          </button>
          <button
            type="button"
            className={activeFilter === "applied" ? "primary-button" : "secondary-button"}
            onClick={() => setActiveFilter("applied")}
          >
            ✓ My Applications ({myApplications.length})
          </button>
        </div>
      )}

      {/* Recruiter / Admin Post Form */}
      {["company", "admin", "operator"].includes(role) && (
        <form className="panel form-panel" onSubmit={submitJob} style={{ borderTop: "4px solid #1a73e8" }}>
          <h3>Post a New Campus Placement Opportunity</h3>
          <p className="muted">Define company cutoffs, eligible branches, and required technical skills.</p>

          <div className="form-grid">
            <div className="field">
              <label>Job Title *</label>
              <input name="title" value={form.title} onChange={updateField} placeholder="e.g. Software Development Engineer" required />
            </div>
            <div className="field">
              <label>Company Name *</label>
              <input name="company_name" value={form.company_name} onChange={updateField} placeholder="e.g. Google" required />
            </div>
            <div className="field">
              <label>Minimum CGPA Cutoff *</label>
              <input name="minimum_cgpa" type="number" min="0" max="10" step="0.1" value={form.minimum_cgpa} onChange={updateField} placeholder="e.g. 7.5" required />
            </div>
            <div className="field">
              <label>Target Graduation Batch</label>
              <input name="graduation_year" type="number" value={form.graduation_year} onChange={updateField} placeholder="2027" />
            </div>
            <div className="field full-width">
              <label>Required Technical Skills (comma-separated)</label>
              <input name="required_skills" value={form.required_skills} onChange={updateField} placeholder="Python, Java, SQL, Data Structures" />
            </div>
            <div className="field full-width">
              <label>Eligible Departments / Branches (comma-separated)</label>
              <input name="eligible_branches" value={form.eligible_branches} onChange={updateField} placeholder="CSE, CSE-AIML, IT, ECE" />
            </div>
            <div className="field full-width">
              <label>Job Description</label>
              <textarea name="description" rows="3" value={form.description} onChange={updateField} placeholder="Describe the role responsibilities and qualifications..." />
            </div>
          </div>

          <button className="primary-button" disabled={saving}>
            {saving ? "Posting..." : "Post Placement Opportunity →"}
          </button>
        </form>
      )}

      {loading ? (
        <div className="panel">Evaluating opportunities and eligibility criteria...</div>
      ) : filteredJobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">▤</div>
          <h3>No jobs found</h3>
          <p>
            {activeFilter === "eligible"
              ? "You have already applied to all eligible opportunities or no new matching drives are open."
              : activeFilter === "applied"
              ? "You haven't applied to any campus jobs yet. Click 'Auto-Apply' on any eligible drive!"
              : "There are no opportunities to display at the moment."}
          </p>
        </div>
      ) : (
        <div className="job-grid">
          {filteredJobs.map((job) => {
            const company = job.company_name || job.company || "Company";
            const minCgpa = job.minimum_cgpa ?? job.min_cgpa ?? 0;
            const match = matchedJobData[job.id];
            const isEligible = isStudent ? match?.eligible ?? (studentProfile?.cgpa >= minCgpa) : true;
            const reasons = isStudent ? match?.eligibility_reasons || [] : [];
            const hasApplied = isStudent && (appliedJobIds.has(job.id) || receiptsMap[String(job.id)]?.status === "SUBMITTED");
            const existingReceipt = receiptsMap[String(job.id)];

            return (
              <article
                className="job-card"
                key={job.id}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  border: isStudent && !isEligible ? "1.5px solid #fca5a5" : hasApplied ? "1.5px solid #86efac" : isEligible ? "1.5px solid #93c5fd" : undefined,
                  background: isStudent && !isEligible ? "#fffbfb" : hasApplied ? "#f8fdf9" : undefined
                }}
              >
                <div>
                  <div className="job-card-top">
                    <div
                      className="company-avatar"
                      style={{
                        background: isStudent && !isEligible ? "#991b1b" : hasApplied ? "#15803d" : "#1a73e8",
                        color: "#fff"
                      }}
                    >
                      {company.charAt(0).toUpperCase()}
                    </div>

                    {/* Student Specific Personalized Status Badge */}
                    {isStudent ? (
                      <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                        {hasApplied ? (
                          <span className="status-badge approved" style={{ fontWeight: "bold", background: "#dcfce7", color: "#15803d" }}>
                            ✓ Applied
                          </span>
                        ) : isEligible ? (
                          <span className="status-badge approved" style={{ fontWeight: "bold", background: "#eff6ff", color: "#1d4ed8", borderColor: "#bfdbfe" }}>
                            ⚡ 1-Click Auto-Apply
                          </span>
                        ) : (
                          <span className="status-badge rejected" style={{ fontWeight: "bold" }}>
                            ✕ Not Eligible
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className={`status-badge ${job.status === "approved" ? "approved" : "pending"}`}>
                        Posting: {job.status || "Open"}
                      </span>
                    )}
                  </div>

                  <h3 style={{ fontSize: "16px", marginTop: "8px" }}>{job.title}</h3>
                  <p className="company-name" style={{ fontWeight: 600, color: "#1a73e8" }}>{company}</p>
                  <p className="job-description" style={{ fontSize: "13px" }}>
                    {job.description || "Explore this opportunity for your next career step."}
                  </p>

                  <div className="job-details" style={{ margin: "8px 0" }}>
                    <span style={{ fontWeight: isStudent && (studentProfile?.cgpa < minCgpa) ? "bold" : "normal", color: isStudent && (studentProfile?.cgpa < minCgpa) ? "#dc2626" : "inherit" }}>
                      CGPA Cutoff: {minCgpa}+ {isStudent && studentProfile?.cgpa && `(Yours: ${studentProfile.cgpa.toFixed(2)})`}
                    </span>
                    {job.graduation_year && <span>Batch: {job.graduation_year}</span>}
                  </div>

                  {job.eligible_branches && (
                    <div className="small-text" style={{ margin: "6px 0", color: "var(--color-text-muted)" }}>
                      <strong>Allowed Branches:</strong> {job.eligible_branches}
                    </div>
                  )}

                  {job.required_skills && (
                    <div className="tag-list compact" style={{ marginTop: "8px" }}>
                      {job.required_skills.split(",").map((s) => s.trim()).filter(Boolean).map((skill) => (
                        <span className="skill-tag" key={skill}>{skill}</span>
                      ))}
                    </div>
                  )}

                  {/* INELIGIBILITY REASONS ALERT FOR STUDENTS */}
                  {isStudent && !isEligible && (
                    <div style={{ marginTop: "12px", padding: "10px 12px", background: "#fef2f2", borderLeft: "3px solid #ef4444", borderRadius: "4px" }}>
                      <strong style={{ fontSize: "12px", color: "#991b1b" }}>✕ Ineligible Criteria:</strong>
                      <ul style={{ margin: "4px 0 0 14px", padding: 0, fontSize: "11px", color: "#b91c1c" }}>
                        {studentProfile?.cgpa < minCgpa && (
                          <li>
                            <strong>CGPA Deficiency: Your CGPA ({studentProfile.cgpa.toFixed(2)}) is below the required {minCgpa.toFixed(2)} cutoff.</strong>
                          </li>
                        )}
                        {reasons.filter((r) => !r.includes("CGPA Deficiency")).map((r, ri) => (
                          <li key={ri}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* STUDENT ACTION ROW: AUTONOMOUS AUTO-APPLY & RESUME GENERATION */}
                {isStudent && (
                  <div style={{ marginTop: "16px", paddingTop: "12px", borderTop: "1px solid var(--color-border, #eee)", display: "flex", flexDirection: "column", gap: "8px" }}>
                    {hasApplied ? (
                      <button
                        type="button"
                        className="secondary-button full-button"
                        style={{ background: "#dcfce7", color: "#166534", borderColor: "#86efac", fontWeight: "bold" }}
                        onClick={() => {
                          if (existingReceipt) {
                            setSelectedReceipt(existingReceipt);
                          } else {
                            setMessage(`Application record exists for ${job.title} at ${company}.`);
                          }
                        }}
                      >
                        ✓ Applied {existingReceipt ? `(Receipt: ${existingReceipt.confirmation_id})` : "(View Status)"} 🔍
                      </button>
                    ) : isEligible ? (
                      <button
                        type="button"
                        className="primary-button full-button"
                        style={{ background: "linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)", color: "white", fontWeight: "bold" }}
                        onClick={() => triggerAutoApply(job)}
                      >
                        ⚡ Auto-Apply (LangGraph Agent)
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="secondary-button full-button"
                        disabled
                        style={{ opacity: 0.6, cursor: "not-allowed", background: "#f3f4f6", color: "#6b7280" }}
                      >
                        ✕ Ineligible (Cannot Apply)
                      </button>
                    )}

                    <button
                      type="button"
                      className="secondary-button full-button"
                      style={{ background: "#f0fdf4", color: "#166534", borderColor: "#bbf7d0", fontSize: "12px", fontWeight: "600" }}
                      onClick={() => handleGenerateResume(job)}
                    >
                      📄 Tailor .tex Resume for this Drive
                    </button>
                  </div>
                )}

                {/* Admin Actions */}
                {role === "admin" && job.status === "pending" && (
                  <div className="button-row" style={{ marginTop: "16px" }}>
                    <button className="primary-button" onClick={() => reviewJob(job.id, "approve")}>
                      Approve Job
                    </button>
                    <button className="danger-button" onClick={() => reviewJob(job.id, "reject")}>
                      Reject
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}

      {/* BATCH / ALL ELIGIBLE AUTO-APPLY MODAL */}
      {bulkModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="panel" style={{ width: "90%", maxWidth: "680px", maxHeight: "90vh", overflowY: "auto", background: "var(--color-bg-card, #fff)", borderRadius: "12px", boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border, #eee)", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#10b981" }}>LANGGRAPH AGENT ORCHESTRATION</span>
                <h3 style={{ margin: "4px 0" }}>Auto-Applying to All Eligible Campus Drives</h3>
                <p className="muted" style={{ fontSize: "13px" }}>
                  Autonomous state machine executing for {bulkQueue.length} eligible drive{bulkQueue.length > 1 ? "s" : ""}
                </p>
              </div>
              {!bulkExecuting && (
                <button className="secondary-button compact" onClick={() => setBulkModalOpen(false)}>✕ Close</button>
              )}
            </div>

            {/* Progress Bar */}
            <div style={{ margin: "16px 0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "6px" }}>
                <span>
                  {bulkExecuting
                    ? `Processing ${bulkCurrentIndex + 1} of ${bulkQueue.length}...`
                    : `Completed: ${bulkResults.filter(r => r.success).length} applied successfully`}
                </span>
                <strong style={{ color: "#1a73e8" }}>
                  {Math.round((bulkResults.length / (bulkQueue.length || 1)) * 100)}%
                </strong>
              </div>
              <div style={{ width: "100%", height: "8px", background: "#e5e7eb", borderRadius: "4px", overflow: "hidden" }}>
                <div
                  style={{
                    width: `${(bulkResults.length / (bulkQueue.length || 1)) * 100}%`,
                    height: "100%",
                    background: "linear-gradient(90deg, #10b981 0%, #2563eb 100%)",
                    transition: "width 0.3s ease"
                  }}
                />
              </div>
            </div>

            {/* Queue Itemized List */}
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "14px" }}>
              {bulkQueue.map((job, idx) => {
                const res = bulkResults[idx];
                const isCurrent = bulkExecuting && bulkCurrentIndex === idx;
                const isDone = Boolean(res);

                return (
                  <div
                    key={job.id}
                    style={{
                      padding: "10px 14px",
                      borderRadius: "8px",
                      background: isCurrent ? "#eff6ff" : isDone ? "#f8fafc" : "#f9fafb",
                      border: isCurrent ? "1.5px solid #3b82f6" : isDone ? "1px solid #e2e8f0" : "1px solid #eee",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: "14px", color: "#111827" }}>{job.title}</strong>
                      <div className="muted" style={{ fontSize: "12px" }}>{job.company_name}</div>
                      {res?.confirmation_id && (
                        <div style={{ fontSize: "11px", color: "#166534", marginTop: "2px" }}>
                          Receipt: <strong>{res.confirmation_id}</strong> • Fit: {Math.round(res.match_score)}%
                        </div>
                      )}
                    </div>

                    <div>
                      {isCurrent ? (
                        <span className="status-badge pending" style={{ animation: "pulse 1.5s infinite" }}>
                          ⚡ Applying...
                        </span>
                      ) : isDone && res.success ? (
                        <span className="status-badge approved" style={{ fontWeight: "bold" }}>
                          ✓ Applied
                        </span>
                      ) : isDone && !res.success ? (
                        <span className="status-badge rejected">
                          ✕ Skipped
                        </span>
                      ) : (
                        <span className="status-badge" style={{ background: "#e5e7eb", color: "#6b7280" }}>
                          Queued
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Completion Footer */}
            {!bulkExecuting && (
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px", marginTop: "20px", borderTop: "1px solid var(--color-border, #eee)", paddingTop: "14px" }}>
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => setBulkModalOpen(false)}
                >
                  Done
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Single Auto-Apply LangGraph Execution Modal */}
      {agentModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="panel" style={{ width: "90%", maxWidth: "600px", maxHeight: "90vh", overflowY: "auto", background: "var(--color-bg-card, #fff)", borderRadius: "12px", boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border, #eee)", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#1a73e8" }}>LANGGRAPH CAMPUS AUTO-APPLY AGENT</span>
                <h3 style={{ margin: "4px 0" }}>Auto-Applying for {currentJobApplying?.title}</h3>
                <p className="muted" style={{ fontSize: "13px" }}>{currentJobApplying?.company_name}</p>
              </div>
              {!agentExecuting && (
                <button className="secondary-button compact" onClick={() => setAgentModalOpen(false)}>✕ Close</button>
              )}
            </div>

            {/* Workflow Step Indicator */}
            <div style={{ margin: "20px 0", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px", opacity: agentState?.step >= 1 ? 1 : 0.4 }}>
                <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: agentState?.step > 1 ? "#10b981" : "#1a73e8", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", fontSize: "13px" }}>
                  {agentState?.step > 1 ? "✓" : "1"}
                </div>
                <div>
                  <strong>Evaluate Campus Eligibility & Cutoffs</strong>
                  <div className="muted" style={{ fontSize: "12px" }}>Validates CGPA cutoff, eligible branch, and skill taxonomy match</div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "12px", opacity: agentState?.step >= 2 ? 1 : 0.4 }}>
                <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: agentState?.step > 2 ? "#10b981" : agentState?.step === 2 ? "#1a73e8" : "#9ca3af", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", fontSize: "13px" }}>
                  {agentState?.step > 2 ? "✓" : "2"}
                </div>
                <div>
                  <strong>Hugging Face / Open-Source NLP Statement Synthesis</strong>
                  <div className="muted" style={{ fontSize: "12px" }}>Synthesizes customized statement of interest & company screening answers</div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "12px", opacity: agentState?.step >= 3 ? 1 : 0.4 }}>
                <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: agentState?.step === 3 ? (agentState.data?.success ? "#10b981" : "#f59e0b") : "#9ca3af", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", fontSize: "13px" }}>
                  {agentState?.step === 3 ? "✓" : "3"}
                </div>
                <div>
                  <strong>Autonomous Placement Submission & Receipt</strong>
                  <div className="muted" style={{ fontSize: "12px" }}>Logs official application record and generates confirmation receipt ID</div>
                </div>
              </div>
            </div>

            {agentExecuting ? (
              <div style={{ padding: "16px", background: "var(--color-bg-subtle, #f3f4f6)", borderRadius: "8px", textAlign: "center" }}>
                <p style={{ fontWeight: 600, color: "#1a73e8" }}>⚡ {agentState?.statusText}</p>
                <p className="muted" style={{ fontSize: "12px" }}>Executing LangGraph state transition graph...</p>
              </div>
            ) : agentState?.data ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginTop: "12px" }}>
                <div className={`notice ${agentState.data.success ? "success" : "warning"}`}>
                  <strong>{agentState.data.success ? "✓ Application Successfully Submitted to Campus Drive" : "⚠ Application Skipped"}</strong>
                  <p style={{ fontSize: "13px", marginTop: "4px" }}>
                    {agentState.data.success
                      ? `Receipt ID: ${agentState.data.confirmation_id} • Match Score: ${agentState.data.match_score}%`
                      : `Criteria did not meet role requirements.`}
                  </p>
                </div>

                {agentState.data.tailored_cover_letter && (
                  <div>
                    <h4 style={{ fontSize: "14px", marginBottom: "6px" }}>Synthesized Application Statement:</h4>
                    <div style={{ padding: "12px", background: "var(--color-bg-subtle, #f8fafc)", borderLeft: "4px solid #1a73e8", fontSize: "13px", borderRadius: "4px", lineHeight: "1.5" }}>
                      "{agentState.data.tailored_cover_letter}"
                    </div>
                  </div>
                )}

                {agentState.data.custom_qa && Object.keys(agentState.data.custom_qa).length > 0 && (
                  <div>
                    <h4 style={{ fontSize: "14px", marginBottom: "6px" }}>Auto-Generated Screening Q&A:</h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "12px" }}>
                      {Object.entries(agentState.data.custom_qa).map(([q, a]) => (
                        <div key={q} style={{ padding: "8px 12px", background: "var(--color-bg-subtle, #f8fafc)", borderRadius: "6px" }}>
                          <strong>Q: {q}</strong>
                          <div className="muted" style={{ marginTop: "2px" }}>A: {a}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px", marginTop: "12px" }}>
                  <button className="primary-button" onClick={() => setAgentModalOpen(false)}>
                    Done
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* View Individual Receipt Modal */}
      {selectedReceipt && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="panel" style={{ width: "90%", maxWidth: "650px", maxHeight: "90vh", overflowY: "auto", background: "var(--color-bg-card, #fff)", borderRadius: "12px", boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border, #eee)", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#10b981" }}>CAMPUS DRIVE CONFIRMATION RECEIPT</span>
                <h3 style={{ margin: "4px 0" }}>{selectedReceipt.job_title}</h3>
                <p className="muted" style={{ fontSize: "13px" }}>{selectedReceipt.company_name} • Confirmation: <strong style={{ color: "#1a73e8" }}>{selectedReceipt.confirmation_id}</strong></p>
              </div>
              <button className="secondary-button compact" onClick={() => setSelectedReceipt(null)}>✕ Close</button>
            </div>

            <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                <span className="pill">Fit Score: {Math.round(selectedReceipt.match_score)}%</span>
                <span className="pill approved">Status: {selectedReceipt.status}</span>
                <span className="pill">Applied: {new Date(selectedReceipt.applied_at).toLocaleString()}</span>
              </div>

              {selectedReceipt.tailored_cover_letter && (
                <div>
                  <h4 style={{ fontSize: "14px", marginTop: "10px", marginBottom: "6px" }}>Synthesized Application Statement:</h4>
                  <div style={{ padding: "12px", background: "var(--color-bg-subtle, #f8fafc)", borderLeft: "4px solid #10b981", fontSize: "13px", borderRadius: "4px", lineHeight: "1.5" }}>
                    "{selectedReceipt.tailored_cover_letter}"
                  </div>
                </div>
              )}

              {selectedReceipt.custom_qa && Object.keys(selectedReceipt.custom_qa).length > 0 && (
                <div>
                  <h4 style={{ fontSize: "14px", marginTop: "10px", marginBottom: "6px" }}>Screening Answers:</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "12px" }}>
                    {Object.entries(selectedReceipt.custom_qa).map(([q, a]) => (
                      <div key={q} style={{ padding: "8px 12px", background: "var(--color-bg-subtle, #f8fafc)", borderRadius: "6px" }}>
                        <strong>Q: {q}</strong>
                        <div className="muted" style={{ marginTop: "2px" }}>A: {a}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* LaTeX Resume Generator Modal */}
      {resumeModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div className="panel" style={{ width: "92%", maxWidth: "850px", maxHeight: "90vh", overflowY: "auto", background: "var(--color-bg-card, #fff)", borderRadius: "12px", boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border, #eee)", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#166534" }}>LATEX RESUME TAILORING ENGINE</span>
                <h3 style={{ margin: "4px 0" }}>ATS-Optimized Resume for {resumeData?.job_title || "Target Role"}</h3>
                <p className="muted" style={{ fontSize: "13px" }}>{resumeData?.company_name} • Format: <strong style={{ color: "#1a73e8" }}>data/resume_template.tex</strong></p>
              </div>
              <button className="secondary-button compact" onClick={() => setResumeModalOpen(false)}>✕ Close</button>
            </div>

            {resumeLoading ? (
              <div style={{ padding: "40px 20px", textAlign: "center" }}>
                <p style={{ fontWeight: 600, color: "#1a73e8" }}>⚡ Injecting profile skills, tailored projects, and STAR bullets into LaTeX template...</p>
              </div>
            ) : resumeData ? (
              <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "16px" }}>
                {/* Actions Bar */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ display: "flex", gap: "6px" }}>
                    <button
                      className={resumeViewTab === "code" ? "primary-button compact" : "secondary-button compact"}
                      onClick={() => setResumeViewTab("code")}
                    >
                      LaTeX Source (.tex)
                    </button>
                    <button
                      className={resumeViewTab === "preview" ? "primary-button compact" : "secondary-button compact"}
                      onClick={() => setResumeViewTab("preview")}
                    >
                      Structured Preview
                    </button>
                  </div>

                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      type="button"
                      className="secondary-button compact"
                      onClick={handleCopyLaTeX}
                    >
                      {copySuccess ? "✓ Copied LaTeX!" : "📋 Copy LaTeX Code"}
                    </button>
                    <button
                      type="button"
                      className="primary-button compact"
                      style={{ background: "#166534" }}
                      onClick={handleDownloadTex}
                    >
                      ⬇ Download .tex File
                    </button>
                  </div>
                </div>

                {/* Overleaf Tip */}
                <div style={{ padding: "10px 14px", background: "#f0fdf4", borderLeft: "4px solid #16a34a", borderRadius: "6px", fontSize: "13px", color: "#166534" }}>
                  💡 <strong>How to compile into PDF:</strong> Download this <code>.tex</code> file and compile with <code>pdflatex</code>, or open <a href="https://www.overleaf.com" target="_blank" rel="noopener noreferrer" style={{ textDecoration: "underline", fontWeight: "bold" }}>Overleaf.com</a>, create a "New Project" and paste the code!
                </div>

                {/* TAB 1: Code View */}
                {resumeViewTab === "code" && (
                  <div style={{ position: "relative" }}>
                    <textarea
                      readOnly
                      value={resumeData.tex_content}
                      style={{
                        width: "100%",
                        height: "380px",
                        fontFamily: "monospace",
                        fontSize: "12px",
                        padding: "12px",
                        backgroundColor: "#1e1e1e",
                        color: "#d4d4d4",
                        borderRadius: "8px",
                        border: "1px solid #333",
                        lineHeight: "1.4",
                        resize: "vertical"
                      }}
                    />
                  </div>
                )}

                {/* TAB 2: Structured Visual Preview */}
                {resumeViewTab === "preview" && resumeData.preview && (
                  <div style={{ padding: "16px", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "8px", display: "flex", flexDirection: "column", gap: "12px", fontSize: "13px" }}>
                    <div>
                      <h3 style={{ color: "#1e40af", margin: 0 }}>{resumeData.preview.name}</h3>
                      <p className="muted" style={{ margin: "2px 0" }}>{resumeData.preview.email} • Roll: {resumeData.preview.roll_number} • B.Tech {resumeData.preview.branch} (CGPA: {resumeData.preview.cgpa})</p>
                    </div>

                    <div>
                      <h4 style={{ color: "#6b21a8", borderBottom: "1px solid #e9d5ff", paddingBottom: "2px" }}>Target Role Objective</h4>
                      <p>Tailored for <strong>{resumeData.job_title}</strong> at <strong>{resumeData.company_name}</strong>.</p>
                    </div>

                    <div>
                      <h4 style={{ color: "#6b21a8", borderBottom: "1px solid #e9d5ff", paddingBottom: "2px" }}>Categorized Technical Skills</h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        {Object.entries(resumeData.preview.categorized_skills || {}).map(([cat, skills]) => (
                          <div key={cat}>
                            <strong>{cat}: </strong>
                            <span>{skills.join(", ")}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 style={{ color: "#6b21a8", borderBottom: "1px solid #e9d5ff", paddingBottom: "2px" }}>Tailored STAR Projects</h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                        {(resumeData.preview.projects || []).map((p) => (
                          <div key={p.title} style={{ padding: "8px 12px", background: "#fff", borderRadius: "6px", border: "1px solid #eee" }}>
                            <strong>{p.title}</strong> — <span className="muted">{p.tagline}</span>
                            <p style={{ margin: "4px 0" }}>{p.description}</p>
                            <span className="small-text" style={{ color: "#1e40af" }}><strong>Tech:</strong> {p.tech}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}