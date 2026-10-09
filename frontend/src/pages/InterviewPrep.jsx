import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const PRESET_DURATIONS = [
  { label: "⚡ 3-Day Sprint", days: 3 },
  { label: "📅 7-Day Fast-Track", days: 7 },
  { label: "🚀 14-Day Booster", days: 14 },
  { label: "🎯 30-Day Comprehensive", days: 30 },
  { label: "🏆 60-Day Mastery", days: 60 }
];

export default function InterviewPrep({ user }) {
  const role = String(user?.role || "").toLowerCase();
  const isStudent = role === "student";

  // Admin Candidate Selector State
  const [studentList, setStudentList] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [selectedStudentProfile, setSelectedStudentProfile] = useState(null);
  const [studentSearch, setStudentSearch] = useState("");

  // Plan Duration & Drive Date State
  const [targetDays, setTargetDays] = useState(30);
  const [driveDate, setDriveDate] = useState("");
  const [activePhaseFilter, setActivePhaseFilter] = useState("all");

  const [matches, setMatches] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loadingMatches, setLoadingMatches] = useState(true);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [activeJobId, setActiveJobId] = useState(null);
  const [error, setError] = useState("");
  const [checkedTasks, setCheckedTasks] = useState({});

  // Resume Modal State
  const [resumeModalOpen, setResumeModalOpen] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [resumeViewTab, setResumeViewTab] = useState("code"); // "code" | "preview"
  const [copySuccess, setCopySuccess] = useState(false);

  // Copilot Chat State
  const [chatMessages, setChatMessages] = useState([
    { sender: "agent", text: "Hello! I am your AI Placement Agent. Select a target job above, configure your drive date or preparation duration (e.g. 30 days), and ask me for custom mock questions or technical guidance." }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  // Multi-Agent Ecosystem State
  const [evaluatingEcosystem, setEvaluatingEcosystem] = useState(false);
  const [ecosystemResult, setEcosystemResult] = useState(null);

  async function handleEvaluateEcosystem(customQuery = "comprehensive review") {
    if (!activeJobId) return;
    setEvaluatingEcosystem(true);
    setError("");

    try {
      const payload = {
        job_id: activeJobId,
        query: customQuery
      };
      if (!isStudent && selectedStudentId) {
        payload.student_id = selectedStudentId;
      }

      const res = await api("/api/agent/prep-ecosystem", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      setEcosystemResult(res);
      // Also inject report into copilot chat log
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: res.summary_markdown || res.reply,
          data: res.report,
          type: "consensus"
        }
      ]);
    } catch (err) {
      setError(err.message || "Failed to execute multi-agent panel evaluation.");
    } finally {
      setEvaluatingEcosystem(false);
    }
  }

  // Handle Drive Date change to calculate days
  function handleDriveDateChange(e) {
    const val = e.target.value;
    setDriveDate(val);
    if (val) {
      const target = new Date(val);
      const today = new Date();
      const diffTime = target.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays > 0) {
        setTargetDays(diffDays);
      }
    }
  }

  // If Admin/Faculty, load student list first
  useEffect(() => {
    if (!isStudent) {
      async function loadStudents() {
        try {
          const res = await api("/api/students/");
          const list = Array.isArray(res) ? res : res.items || [];
          setStudentList(list);
          if (list.length > 0 && !selectedStudentId) {
            setSelectedStudentId(list[0].id);
            setSelectedStudentProfile(list[0]);
          }
        } catch (err) {
          setError(err.message || "Failed to load students for admin prep planner.");
        }
      }
      loadStudents();
    }
  }, [isStudent, selectedStudentId]);

  const loadMatches = useCallback(async () => {
    setLoadingMatches(true);
    setError("");

    try {
      if (isStudent) {
        const result = await api("/api/students/me/matched-jobs");
        setMatches(Array.isArray(result) ? result : []);
        if (result.length > 0 && !activeJobId) {
          setActiveJobId(result[0].job_id);
        }
      } else if (selectedStudentId) {
        const result = await api(`/api/students/${selectedStudentId}/matched-jobs`);
        const rankedMatches = result?.matches || [];
        setMatches(rankedMatches);
        if (result?.student) {
          setSelectedStudentProfile(result.student);
        }
        if (rankedMatches.length > 0 && !activeJobId) {
          setActiveJobId(rankedMatches[0].job_id);
        }
      }
    } catch (err) {
      setError(err.message || "Failed to load job matches.");
    } finally {
      setLoadingMatches(false);
    }
  }, [isStudent, selectedStudentId, activeJobId]);

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  async function handleGeneratePlan(jobId) {
    setGeneratingPlan(true);
    setActiveJobId(jobId);
    setError("");

    try {
      const params = new URLSearchParams();
      if (targetDays) params.append("days", targetDays);
      if (driveDate) params.append("drive_date", driveDate);

      const qs = params.toString() ? `?${params.toString()}` : "";
      const endpoint = isStudent
        ? `/api/students/me/prep-plan/${jobId}${qs}`
        : `/api/students/${selectedStudentId}/prep-plan/${jobId}${qs}`;

      const plan = await api(endpoint, {
        method: "POST"
      });
      setSelectedPlan(plan);
      setCheckedTasks({});
      setTimeout(() => {
        document.getElementById("plan-viewer")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err.message || "Failed to generate interview preparation plan.");
    } finally {
      setGeneratingPlan(false);
    }
  }

  async function handleGenerateResume(job) {
    setResumeModalOpen(true);
    setResumeLoading(true);
    setResumeData(null);
    setCopySuccess(false);

    try {
      const res = await api("/api/resume/generate-latex", {
        method: "POST",
        body: JSON.stringify({
          job_id: String(job.job_id || job.id),
          job_title: job.title || job.job_title,
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

  async function handleSendChat(queryText = null) {
    const q = (queryText || chatInput).trim();
    if (!q || !activeJobId) return;

    setChatMessages((prev) => [...prev, { sender: "user", text: q }]);
    if (!queryText) setChatInput("");
    setChatLoading(true);

    try {
      const payload = {
        job_id: activeJobId,
        query: q
      };
      if (!isStudent && selectedStudentId) {
        payload.student_id = selectedStudentId;
      }

      const res = await api("/api/agent/chat", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      const responseText = res.reply || res.message || res.text || "Plan updated by AI Copilot.";

      if (res.type === "plan" && res.data) {
        setSelectedPlan({
          ...res.data,
          job_title: matches.find((m) => m.job_id === activeJobId)?.title || res.data.job_title,
          company_name: matches.find((m) => m.job_id === activeJobId)?.company_name || res.data.company_name
        });
      }

      setChatMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: responseText,
          data: res.data,
          type: res.type
        }
      ]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        { sender: "agent", text: `Error: ${err.message}` }
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  function toggleTask(dayIdx, taskIdx) {
    const key = `${dayIdx}-${taskIdx}`;
    setCheckedTasks((prev) => ({
      ...prev,
      [key]: !prev[key]
    }));
  }

  function getTierBadgeClass(tier) {
    if (tier === "Strong Match") return "status-badge approved";
    if (tier === "Good Match") return "status-badge pending";
    return "status-badge";
  }

  const filteredStudentOptions = studentList.filter((s) => {
    if (!studentSearch.trim()) return true;
    const t = studentSearch.toLowerCase();
    return s.name.toLowerCase().includes(t) || s.roll_number.toLowerCase().includes(t) || s.branch.toLowerCase().includes(t);
  });

  const dailySchedule = selectedPlan?.daily_schedule || selectedPlan?.daily_roadmap || [];
  
  // Calculate completed task percentage
  let totalTasks = 0;
  let completedTasks = 0;
  dailySchedule.forEach((d, dIdx) => {
    (d.tasks || []).forEach((_, tIdx) => {
      totalTasks++;
      if (checkedTasks[`${dIdx}-${tIdx}`]) completedTasks++;
    });
  });
  const progressPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Filter daily schedule by phase
  const displayedSchedule = dailySchedule.filter((d) => {
    if (activePhaseFilter === "all") return true;
    return d.phase?.toLowerCase().includes(activePhaseFilter.toLowerCase());
  });

  return (
    <div className="page-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">ADAPTIVE PLACEMENT AGENT</span>
          <h2>Dynamic Placement Preparation Plan & Drive Roadmaps</h2>
          <p className="muted">
            {isStudent
              ? "The engine calculates the exact days remaining until your company placement drive (e.g. 30 days) and constructs a day-by-day roadmap targeting your missing skill gaps."
              : "Admin & Placement Cell Mode: Inspect candidate skill matches and generate dynamic multi-day roadmaps adapted to drive dates."}
          </p>
        </div>
        <button className="secondary-button" onClick={loadMatches}>
          ↻ Refresh Matches
        </button>
      </div>

      {error && <div className="notice error">{error}</div>}

      {/* DYNAMIC DURATION & DRIVE DATE CONTROLS */}
      <div className="panel" style={{ borderTop: "4px solid #10b981" }}>
        <div className="section-heading compact-heading">
          <div>
            <span className="eyebrow" style={{ color: "#059669" }}>DRIVE TIMELINE CONFIGURATION</span>
            <h3 style={{ margin: "4px 0" }}>Configure Placement Drive Date & Preparation Days</h3>
            <p className="muted" style={{ fontSize: "13px" }}>
              Set your target drive date or select preparation duration to generate a customized day-by-day roadmap.
            </p>
          </div>
          <span className="pill approved" style={{ fontWeight: "bold", fontSize: "13px" }}>
            🎯 Target: {targetDays} Days Preparation
          </span>
        </div>

        {/* Duration Presets */}
        <div style={{ marginTop: "12px" }}>
          <label style={{ display: "block", fontSize: "12px", fontWeight: "bold", color: "var(--color-text-muted)", marginBottom: "6px" }}>
            Duration Presets:
          </label>
          <div className="tag-list" style={{ gap: "8px", flexWrap: "wrap" }}>
            {PRESET_DURATIONS.map((preset) => {
              const isSelected = targetDays === preset.days && !driveDate;
              return (
                <button
                  key={preset.days}
                  type="button"
                  onClick={() => {
                    setTargetDays(preset.days);
                    setDriveDate("");
                  }}
                  className={isSelected ? "primary-button compact" : "secondary-button compact"}
                  style={{ fontSize: "12px", fontWeight: isSelected ? "bold" : "normal" }}
                >
                  {preset.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Drive Date & Day Slider */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px", marginTop: "16px", paddingTop: "14px", borderTop: "1px solid var(--color-border, #eee)" }}>
          <div>
            <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "4px" }}>
              📅 Specify Upcoming Drive Date:
            </label>
            <input
              type="date"
              value={driveDate}
              onChange={handleDriveDateChange}
              style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
            />
            {driveDate && (
              <span className="small-text" style={{ color: "#15803d", fontWeight: "600", marginTop: "4px", display: "block" }}>
                ✓ {targetDays} days calculated until drive date ({driveDate})
              </span>
            )}
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
              <label style={{ fontSize: "13px", fontWeight: "bold" }}>
                ⏳ Custom Days Slider:
              </label>
              <strong style={{ color: "#1a73e8", fontSize: "14px" }}>{targetDays} Days</strong>
            </div>
            <input
              type="range"
              min="1"
              max="60"
              value={targetDays}
              onChange={(e) => {
                setTargetDays(Number(e.target.value));
                setDriveDate("");
              }}
              style={{ width: "100%", cursor: "pointer", accentColor: "#10b981" }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--color-text-muted)" }}>
              <span>1 Day (Sprint)</span>
              <span>15 Days</span>
              <span>30 Days (Standard)</span>
              <span>60 Days (Mastery)</span>
            </div>
          </div>
        </div>
      </div>

      {/* ADMIN CANDIDATE SELECTOR */}
      {!isStudent && (
        <div className="panel" style={{ borderTop: "4px solid #7c3aed", background: "#faf5ff" }}>
          <div className="section-heading compact-heading">
            <div>
              <span className="eyebrow" style={{ color: "#7c3aed" }}>ADMIN CANDIDATE SELECTOR</span>
              <h3 style={{ margin: "4px 0" }}>Inspect Candidate Roadmap & Skill Gaps</h3>
            </div>
            {selectedStudentProfile && (
              <span className="pill" style={{ background: "#ede9fe", color: "#6b21a8", fontWeight: "bold" }}>
                CGPA: {selectedStudentProfile.cgpa ? selectedStudentProfile.cgpa.toFixed(2) : "N/A"} • {selectedStudentProfile.branch}
              </span>
            )}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "12px", marginTop: "12px" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "bold", marginBottom: "4px" }}>
                Select Student from Directory:
              </label>
              <select
                value={selectedStudentId || ""}
                onChange={(e) => {
                  const id = Number(e.target.value);
                  setSelectedStudentId(id);
                  const found = studentList.find((s) => s.id === id);
                  if (found) setSelectedStudentProfile(found);
                  setSelectedPlan(null);
                  setActiveJobId(null);
                }}
                style={{ width: "100%", padding: "8px 10px", borderRadius: "6px", border: "1px solid #ccc" }}
              >
                {filteredStudentOptions.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.roll_number}) — {s.branch} [CGPA: {s.cgpa?.toFixed(2) || "N/A"}]
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: "bold", marginBottom: "4px" }}>
                Filter Candidate List:
              </label>
              <input
                type="text"
                placeholder="Search by student name or roll..."
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
                style={{ width: "100%", padding: "8px 10px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
            </div>
          </div>
        </div>
      )}

      {/* 1. Job Matches List */}
      <section className="panel">
        <div className="section-heading compact-heading">
          <div>
            <span className="eyebrow">OPPORTUNITY RANKINGS</span>
            <h3>
              {isStudent
                ? "Ranked Opportunities for Your Profile"
                : `Ranked Opportunities for ${selectedStudentProfile?.name || "Candidate"}`}
            </h3>
          </div>
          <span className="role-chip">{matches.length} Jobs Evaluated</span>
        </div>

        {loadingMatches ? (
          <p className="muted">Analyzing profile against active placement opportunities...</p>
        ) : matches.length === 0 ? (
          <div className="empty-state compact-empty">
            <div className="empty-icon">✦</div>
            <h3>No approved jobs available</h3>
            <p>New job opportunities will be evaluated as soon as they are approved.</p>
          </div>
        ) : (
          <div className="job-grid">
            {matches.map((match) => (
              <article
                className="job-card"
                key={match.job_id}
                style={{
                  border: activeJobId === match.job_id ? "2px solid var(--color-primary, #1a73e8)" : undefined
                }}
              >
                <div className="job-card-top">
                  <div className="company-avatar">
                    {match.company_name.charAt(0).toUpperCase()}
                  </div>
                  <span className={getTierBadgeClass(match.tier)}>
                    {match.tier} • {match.fit_score}% Fit
                  </span>
                </div>

                <h3>{match.title}</h3>
                <p className="company-name">{match.company_name}</p>

                <div className="job-details">
                  <span>CGPA Cutoff: {match.minimum_cgpa}+</span>
                  <span>Match: {match.skill_match_percentage}% Skills</span>
                </div>

                {/* Skill Match Breakdown */}
                <div style={{ marginTop: "12px" }}>
                  <div className="small-text" style={{ marginBottom: "4px", color: "var(--color-text-muted)" }}>
                    <strong>Acquired Skills ({match.matched_skills.length}):</strong>
                  </div>
                  <div className="tag-list compact">
                    {match.matched_skills.length > 0 ? (
                      match.matched_skills.map((s) => (
                        <span className="skill-tag" style={{ background: "#e6f4ea", color: "#137333" }} key={s}>
                          ✓ {s}
                        </span>
                      ))
                    ) : (
                      <span className="muted small-text">None matched yet</span>
                    )}
                  </div>

                  {match.missing_skills.length > 0 && (
                    <div style={{ marginTop: "8px" }}>
                      <div className="small-text" style={{ marginBottom: "4px", color: "var(--color-text-muted)" }}>
                        <strong>Missing Skill Gaps ({match.missing_skills.length}):</strong>
                      </div>
                      <div className="tag-list compact">
                        {match.missing_skills.map((s) => (
                          <span className="skill-tag" style={{ background: "#fce8e6", color: "#c5221f" }} key={s}>
                            ✕ {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions Row */}
                <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <button
                    type="button"
                    className="primary-button full-button"
                    style={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)", fontWeight: "bold" }}
                    disabled={generatingPlan && activeJobId === match.job_id}
                    onClick={() => handleGeneratePlan(match.job_id)}
                  >
                    {generatingPlan && activeJobId === match.job_id
                      ? `Generating ${targetDays}-Day Adaptive Plan...`
                      : `⚡ Generate ${targetDays}-Day Prep Roadmap`}
                  </button>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <button
                      type="button"
                      className="secondary-button compact"
                      style={{ background: "#eff6ff", borderColor: "#bfdbfe", color: "#1d4ed8", fontWeight: "bold" }}
                      disabled={evaluatingEcosystem && activeJobId === match.job_id}
                      onClick={() => {
                        setActiveJobId(match.job_id);
                        handleEvaluateEcosystem();
                      }}
                    >
                      {evaluatingEcosystem && activeJobId === match.job_id ? "🤖 Running Panel..." : "🤖 Multi-Agent Consensus"}
                    </button>

                    <button
                      type="button"
                      className="secondary-button compact"
                      onClick={() => handleGenerateResume(match)}
                    >
                      📄 LaTeX Resume
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Multi-Agent Ecosystem Consensus Result Widget */}
      {ecosystemResult && (
        <section className="panel" style={{ borderTop: "4px solid #6366f1", background: "linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)" }}>
          <div className="section-heading">
            <div>
              <span className="eyebrow" style={{ color: "#4f46e5" }}>LANGGRAPH AGENT ECOSYSTEM</span>
              <h2>Multi-Agent Placement Readiness Consensus</h2>
              <p className="muted">
                Consensus verdict aggregated across <strong>Technical & Code Examiner</strong>, <strong>STAR Behavioral Bar-Raiser</strong>, and <strong>Adaptive Plan Rebalancer</strong>.
              </p>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "28px", fontWeight: "bold", color: ecosystemResult.readiness_score >= 75 ? "#10b981" : "#f59e0b" }}>
                {ecosystemResult.readiness_score}/100
              </div>
              <span className="pill approved">{ecosystemResult.report?.readiness_tier || "Evaluated"}</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px", marginTop: "16px" }}>
            {/* Technical Examiner Pillar */}
            <div style={{ padding: "14px", background: "#fff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <strong style={{ color: "#1e293b", fontSize: "14px" }}>💻 Technical & Code Examiner</strong>
                <span className="pill" style={{ background: "#e0f2fe", color: "#0369a1", fontWeight: "bold" }}>
                  {ecosystemResult.report?.technical_summary?.technical_score || 85}%
                </span>
              </div>
              <p className="small-text" style={{ margin: "4px 0", color: "#475569" }}>
                <strong>Verdict:</strong> {ecosystemResult.report?.technical_summary?.verdict || "Evaluated"}
              </p>
              <div style={{ marginTop: "6px" }}>
                <span className="small-text muted">Critical Remediation:</span>
                <div className="tag-list compact" style={{ marginTop: "4px" }}>
                  {(ecosystemResult.report?.technical_summary?.critical_gaps || []).length > 0 ? (
                    ecosystemResult.report.technical_summary.critical_gaps.map((g) => (
                      <span key={g} className="skill-tag" style={{ background: "#fee2e2", color: "#991b1b" }}>✕ {g}</span>
                    ))
                  ) : (
                    <span className="small-text" style={{ color: "#16a34a" }}>✓ No critical gaps detected</span>
                  )}
                </div>
              </div>
            </div>

            {/* Behavioral Bar-Raiser Pillar */}
            <div style={{ padding: "14px", background: "#fff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <strong style={{ color: "#1e293b", fontSize: "14px" }}>🤝 STAR Behavioral Bar-Raiser</strong>
                <span className="pill" style={{ background: "#fef3c7", color: "#b45309", fontWeight: "bold" }}>
                  {ecosystemResult.report?.behavioral_summary?.culture_fit_score || 88}%
                </span>
              </div>
              <p className="small-text" style={{ margin: "4px 0", color: "#475569" }}>
                <strong>Trap Question:</strong> {ecosystemResult.report?.behavioral_summary?.trap_question || "Discuss project tradeoffs."}
              </p>
              <p className="small-text muted" style={{ marginTop: "6px" }}>
                💡 {ecosystemResult.report?.behavioral_summary?.feedback || "Emphasize quantitative metrics."}
              </p>
            </div>

            {/* Adaptive Plan Rebalancer Pillar */}
            <div style={{ padding: "14px", background: "#fff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <strong style={{ color: "#1e293b", fontSize: "14px" }}>🔄 Plan Rebalancer Agent</strong>
                <span className="pill" style={{ background: "#dcfce7", color: "#15803d", fontWeight: "bold" }}>
                  {ecosystemResult.report?.rebalanced_timeline?.total_days || 30} Days
                </span>
              </div>
              <p className="small-text" style={{ margin: "4px 0", color: "#475569" }}>
                Structured into <strong>4 Adaptive Phases</strong> across algorithmic mastery, system design, and mock rounds.
              </p>
              <button
                type="button"
                className="primary-button compact"
                style={{ marginTop: "8px", width: "100%", fontSize: "12px" }}
                onClick={() => handleGeneratePlan(activeJobId)}
              >
                Apply Rebalanced Roadmap ↓
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 2. Dynamic Plan Viewer Section */}
      {selectedPlan && (
        <section id="plan-viewer" className="panel" style={{ borderLeft: "5px solid #10b981" }}>
          <div className="section-heading">
            <div>
              <span className="eyebrow" style={{ color: "#059669" }}>
                {selectedPlan.job_archetype ? `ARCHETYPE: ${selectedPlan.job_archetype}` : "DYNAMIC ROADMAP"}
              </span>
              <h2>
                {selectedPlan.total_days || targetDays}-Day Actionable Prep Plan for {selectedPlan.job_title} at {selectedPlan.company_name}
              </h2>
              <p className="muted">
                Personalized study schedule targeting missing skill gaps:{" "}
                <strong>{(selectedPlan.missing_skills || []).join(", ") || "Core Technical Competencies"}</strong>
              </p>
            </div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
              <span className="pill" style={{ background: "#dcfce7", color: "#166534", fontWeight: "bold" }}>
                🎯 {selectedPlan.total_days || targetDays} Days Plan
              </span>
              <span className="pill approved">
                {selectedPlan.skill_match_percentage}% Alignment
              </span>
            </div>
          </div>

          {/* Progress Tracker Bar */}
          <div style={{ margin: "16px 0", padding: "14px 18px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "6px" }}>
              <strong>Preparation Checklist Progress ({completedTasks} / {totalTasks} Tasks Completed)</strong>
              <strong style={{ color: "#10b981" }}>{progressPct}%</strong>
            </div>
            <div style={{ width: "100%", height: "10px", background: "#e2e8f0", borderRadius: "5px", overflow: "hidden" }}>
              <div
                style={{
                  width: `${progressPct}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, #10b981 0%, #2563eb 100%)",
                  transition: "width 0.3s ease"
                }}
              />
            </div>
          </div>

          {/* Phase Filter Tabs */}
          <div style={{ display: "flex", gap: "8px", margin: "16px 0", flexWrap: "wrap" }}>
            <button
              type="button"
              className={activePhaseFilter === "all" ? "primary-button compact" : "secondary-button compact"}
              onClick={() => setActivePhaseFilter("all")}
            >
              All {dailySchedule.length} Days
            </button>
            <button
              type="button"
              className={activePhaseFilter === "phase 1" ? "primary-button compact" : "secondary-button compact"}
              onClick={() => setActivePhaseFilter("phase 1")}
            >
              Phase 1: Skill Gap Remediation
            </button>
            <button
              type="button"
              className={activePhaseFilter === "phase 2" ? "primary-button compact" : "secondary-button compact"}
              onClick={() => setActivePhaseFilter("phase 2")}
            >
              Phase 2: Algorithmic Mastery
            </button>
            <button
              type="button"
              className={activePhaseFilter === "phase 3" ? "primary-button compact" : "secondary-button compact"}
              onClick={() => setActivePhaseFilter("phase 3")}
            >
              Phase 3: System Design
            </button>
            <button
              type="button"
              className={activePhaseFilter === "phase 4" ? "primary-button compact" : "secondary-button compact"}
              onClick={() => setActivePhaseFilter("phase 4")}
            >
              Phase 4: Mock Rounds & Finals
            </button>
          </div>

          {/* Daily Schedule List */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
            {displayedSchedule.map((day, dayIdx) => (
              <div
                key={day.day_number || day.day || dayIdx}
                style={{
                  background: "var(--color-bg-subtle, #f8fafc)",
                  padding: "16px",
                  borderRadius: "8px",
                  border: "1px solid var(--color-border, #e2e8f0)",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "6px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span
                      style={{
                        background: "#10b981",
                        color: "#fff",
                        padding: "2px 8px",
                        borderRadius: "12px",
                        fontWeight: "bold",
                        fontSize: "12px"
                      }}
                    >
                      {day.day}
                    </span>
                    <h4 style={{ margin: 0, color: "#111827", fontSize: "15px" }}>
                      {day.theme}
                    </h4>
                  </div>
                  <span className="small-text muted">Estimated: {day.estimated_hours} hrs</span>
                </div>

                {day.phase && (
                  <div style={{ fontSize: "11px", fontWeight: "bold", color: "#6b7280", textTransform: "uppercase", marginBottom: "6px" }}>
                    {day.phase}
                  </div>
                )}

                <p style={{ margin: "4px 0 8px 0", fontSize: "13px", color: "#374151" }}>
                  <strong>Goal:</strong> {day.goal}
                </p>

                <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "8px" }}>
                  {(day.tasks || []).map((task, taskIdx) => {
                    const isChecked = !!checkedTasks[`${dayIdx}-${taskIdx}`];
                    return (
                      <label
                        key={taskIdx}
                        style={{
                          display: "flex",
                          alignItems: "flex-start",
                          gap: "8px",
                          fontSize: "13px",
                          cursor: "pointer",
                          textDecoration: isChecked ? "line-through" : "none",
                          color: isChecked ? "var(--color-text-muted)" : "inherit"
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleTask(dayIdx, taskIdx)}
                          style={{ marginTop: "3px" }}
                        />
                        <span>{task}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* High Priority Mock Questions */}
          {selectedPlan.mock_questions && Object.keys(selectedPlan.mock_questions).length > 0 && (
            <div style={{ marginTop: "24px" }}>
              <h3>High-Yield Technical Mock Questions</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
                {Array.isArray(selectedPlan.mock_questions) ? (
                  selectedPlan.mock_questions.map((q, qIdx) => (
                    <div
                      key={qIdx}
                      style={{
                        padding: "10px 14px",
                        background: "#fff",
                        border: "1px solid #e0e0e0",
                        borderRadius: "6px",
                        fontSize: "13px"
                      }}
                    >
                      <strong>Q{qIdx + 1}:</strong> {q}
                    </div>
                  ))
                ) : (
                  Object.entries(selectedPlan.mock_questions).map(([cat, qList]) => (
                    <div key={cat} style={{ background: "#fff", padding: "12px", border: "1px solid #e2e8f0", borderRadius: "8px" }}>
                      <strong style={{ fontSize: "13px", textTransform: "capitalize", color: "#1a73e8" }}>
                        {cat.replace("_", " ")} Questions:
                      </strong>
                      <ul style={{ margin: "6px 0 0 16px", padding: 0, fontSize: "13px" }}>
                        {qList.map((q, qi) => (
                          <li key={qi} style={{ margin: "4px 0" }}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </section>
      )}

      {/* 3. Placement Copilot Chat Agent */}
      <section className="panel">
        <div className="section-heading compact-heading">
          <div>
            <span className="eyebrow">CONVERSATIONAL PLACEMENT MENTOR</span>
            <h3>Interactive Copilot Chat Agent</h3>
            <p className="muted">
              Ask questions about your {targetDays}-day preparation roadmap, technical concepts, mock interview questions, or role tips.
            </p>
          </div>
        </div>

        <div
          style={{
            maxHeight: "340px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            padding: "12px",
            background: "var(--color-bg-subtle, #f8fafc)",
            borderRadius: "8px",
            marginTop: "12px"
          }}
        >
          {chatMessages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                background: msg.sender === "user" ? "#1a73e8" : "#fff",
                color: msg.sender === "user" ? "#fff" : "#1e293b",
                padding: "10px 14px",
                borderRadius: "8px",
                maxWidth: "80%",
                fontSize: "13px",
                lineHeight: "1.4",
                boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
              }}
            >
              {msg.text}
            </div>
          ))}
          {chatLoading && (
            <div style={{ alignSelf: "flex-start", fontSize: "12px", color: "var(--color-text-muted)" }}>
              ⚡ Copilot is formulating advice...
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendChat();
          }}
          style={{ display: "flex", gap: "8px", marginTop: "12px" }}
        >
          <input
            type="text"
            placeholder={activeJobId ? "Ask a question about this role, concepts, or interview advice..." : "Select a job above to ask targeted questions..."}
            value={chatInput}
            disabled={!activeJobId || chatLoading}
            onChange={(e) => setChatInput(e.target.value)}
            style={{ flex: 1, padding: "10px 12px", borderRadius: "6px", border: "1px solid #ccc" }}
          />
          <button
            type="submit"
            className="primary-button"
            disabled={!activeJobId || chatLoading || !chatInput.trim()}
          >
            Ask Copilot →
          </button>
        </form>
      </section>

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
