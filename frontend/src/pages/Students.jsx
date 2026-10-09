import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const POPULAR_SKILL_CATEGORIES = [
  {
    category: "Software & Web",
    skills: ["Python", "Java", "C++", "SQL", "Data Structures", "React", "Node.js", "FastAPI", "TypeScript", "Docker", "AWS", "Git"]
  },
  {
    category: "Electronics & Embedded",
    skills: ["Embedded C", "VLSI", "Verilog", "PCB Design", "RTOS", "Microcontrollers", "MATLAB", "IoT"]
  },
  {
    category: "Mechanical & Civil",
    skills: ["AutoCAD", "SolidWorks", "Finite Element Analysis", "Structural Analysis", "Revit", "CATIA", "ANSYS"]
  }
];

const ALL_POPULAR_SKILLS = POPULAR_SKILL_CATEGORIES.flatMap((c) => c.skills);

const BRANCH_OPTIONS = ["All Branches", "CSE", "CSE-AIML", "IT", "ECE", "EEE", "MECH", "CIVIL"];

const CGPA_CUTOFFS = [
  { label: "All CGPA", value: 0 },
  { label: "6.0+ CGPA", value: 6.0 },
  { label: "7.0+ CGPA", value: 7.0 },
  { label: "7.5+ CGPA", value: 7.5 },
  { label: "8.0+ CGPA", value: 8.0 },
  { label: "8.5+ CGPA", value: 8.5 }
];

export default function Students({ user = {} }) {
  const [students, setStudents] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedSkills, setSelectedSkills] = useState([]); // Support single or multi-skill selection
  const [skillMatchMode, setSkillMatchMode] = useState("all"); // "all" (AND) | "any" (OR)
  const [selectedBranch, setSelectedBranch] = useState("All Branches");
  const [selectedMinCgpa, setSelectedMinCgpa] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const role = String(user?.role || "").toLowerCase();
  const canManage = role === "admin" || role === "operator";

  // Student Add / Edit Modal State
  const [studentModalOpen, setStudentModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    roll_number: "",
    name: "",
    email: "",
    phone: "",
    branch: "CSE",
    graduation_year: 2026,
    cgpa: 8.0,
    skills: "",
    linkedin_url: "",
    github_url: "",
    hackerrank_url: "",
    leetcode_url: "",
    portfolio_url: "",
    bio: ""
  });

  // Override Drive Enrollment Modal State
  const [enrollModalOpen, setEnrollModalOpen] = useState(false);
  const [selectedStudentForEnroll, setSelectedStudentForEnroll] = useState(null);
  const [targetJobId, setTargetJobId] = useState("");
  const [targetStatus, setTargetStatus] = useState("applied");
  const [actionLoading, setActionLoading] = useState(false);

  const loadStudents = useCallback(async (searchTerm = "", skillsArray = [], mode = "all", branchTag = "", minCgpa = 0) => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.append("search", searchTerm.trim());
      if (skillsArray.length > 0) {
        params.append("skill", skillsArray.join(","));
        params.append("skill_mode", mode);
      }
      if (branchTag && branchTag !== "All Branches") params.append("branch", branchTag);
      if (minCgpa > 0) params.append("min_cgpa", minCgpa);

      const qs = params.toString();
      const url = qs ? `/api/students/?${qs}` : "/api/students/";
      const result = await api(url);
      setStudents(Array.isArray(result) ? result : result.items || []);
    } catch (err) {
      setError(err.message || "Failed to load students.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadJobs = useCallback(async () => {
    try {
      const jobList = await api("/api/jobs/");
      setJobs(Array.isArray(jobList) ? jobList : []);
      if (Array.isArray(jobList) && jobList.length > 0) {
        setTargetJobId(String(jobList[0].id));
      }
    } catch {
      setJobs([]);
    }
  }, []);

  useEffect(() => {
    loadStudents(search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa);
  }, [loadStudents, search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa]);

  useEffect(() => {
    if (canManage) {
      loadJobs();
    }
  }, [canManage, loadJobs]);

  function handleSearchSubmit(event) {
    event.preventDefault();
    loadStudents(search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa);
  }

  // Toggle single or multiple skills
  function handleSkillToggle(skill) {
    setSelectedSkills((prev) => {
      const exists = prev.some((s) => s.toLowerCase() === skill.toLowerCase());
      if (exists) {
        return prev.filter((s) => s.toLowerCase() !== skill.toLowerCase());
      } else {
        return [...prev, skill];
      }
    });
  }

  function removeSkill(skillToRemove) {
    setSelectedSkills((prev) => prev.filter((s) => s.toLowerCase() !== skillToRemove.toLowerCase()));
  }

  function clearAllSkills() {
    setSelectedSkills([]);
  }

  function clearAllFilters() {
    setSearch("");
    setSelectedSkills([]);
    setSelectedBranch("All Branches");
    setSelectedMinCgpa(0);
  }

  function openAddModal() {
    setIsEditing(false);
    setFormData({
      id: null,
      roll_number: "",
      name: "",
      email: "",
      phone: "",
      branch: "CSE",
      graduation_year: 2026,
      cgpa: 7.5,
      skills: "Python, SQL, Data Structures",
      linkedin_url: "",
      github_url: "",
      hackerrank_url: "",
      leetcode_url: "",
      portfolio_url: "",
      bio: ""
    });
    setStudentModalOpen(true);
  }

  function openEditModal(student) {
    setIsEditing(true);
    setFormData({
      id: student.id,
      roll_number: student.roll_number || "",
      name: student.name || "",
      email: student.email || "",
      phone: student.phone || "",
      branch: student.branch || "CSE",
      graduation_year: student.graduation_year || 2026,
      cgpa: student.cgpa != null ? student.cgpa : 7.5,
      skills: student.skills || "",
      linkedin_url: student.linkedin_url || "",
      github_url: student.github_url || "",
      hackerrank_url: student.hackerrank_url || "",
      leetcode_url: student.leetcode_url || "",
      portfolio_url: student.portfolio_url || "",
      bio: student.bio || ""
    });
    setStudentModalOpen(true);
  }

  async function handleSaveStudent(e) {
    e.preventDefault();
    setActionLoading(true);
    setError("");
    setSuccessMsg("");

    try {
      if (isEditing && formData.id) {
        await api(`/api/students/${formData.id}`, {
          method: "PUT",
          body: {
            roll_number: formData.roll_number,
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            branch: formData.branch,
            graduation_year: Number(formData.graduation_year),
            cgpa: Number(formData.cgpa),
            skills: formData.skills,
            linkedin_url: formData.linkedin_url,
            github_url: formData.github_url,
            hackerrank_url: formData.hackerrank_url,
            leetcode_url: formData.leetcode_url,
            portfolio_url: formData.portfolio_url,
            bio: formData.bio
          }
        });
        setSuccessMsg(`Student '${formData.name}' (${formData.roll_number}) updated successfully.`);
      } else {
        await api("/api/students/", {
          method: "POST",
          body: {
            roll_number: formData.roll_number,
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            branch: formData.branch,
            graduation_year: Number(formData.graduation_year),
            cgpa: Number(formData.cgpa),
            skills: formData.skills,
            linkedin_url: formData.linkedin_url,
            github_url: formData.github_url,
            hackerrank_url: formData.hackerrank_url,
            leetcode_url: formData.leetcode_url,
            portfolio_url: formData.portfolio_url,
            bio: formData.bio
          }
        });
        setSuccessMsg(`New student '${formData.name}' (${formData.roll_number}) added successfully.`);
      }
      setStudentModalOpen(false);
      loadStudents(search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa);
    } catch (err) {
      setError(err.message || "Failed to save student details.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteStudent(student) {
    if (!window.confirm(`Are you sure you want to delete student '${student.name}' (${student.roll_number})?`)) {
      return;
    }

    try {
      await api(`/api/students/${student.id}`, { method: "DELETE" });
      setSuccessMsg(`Student '${student.name}' deleted successfully.`);
      loadStudents(search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa);
    } catch (err) {
      setError(err.message || "Failed to delete student.");
    }
  }

  function openEnrollModal(student) {
    setSelectedStudentForEnroll(student);
    if (jobs.length > 0 && !targetJobId) {
      setTargetJobId(String(jobs[0].id));
    }
    setEnrollModalOpen(true);
  }

  async function handleForceEnroll(e) {
    e.preventDefault();
    if (!selectedStudentForEnroll || !targetJobId) return;

    setActionLoading(true);
    setError("");
    setSuccessMsg("");

    try {
      const res = await api("/api/applications/override-apply", {
        method: "POST",
        body: {
          student_id: selectedStudentForEnroll.id,
          job_id: Number(targetJobId),
          status: targetStatus
        }
      });
      setSuccessMsg(res.message || `Student '${selectedStudentForEnroll.name}' successfully enrolled in drive (Eligibility Override Active)!`);
      setEnrollModalOpen(false);
    } catch (err) {
      setError(err.message || "Failed to enroll student in drive.");
    } finally {
      setActionLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">TALENT DIRECTORY & RECRUITMENT OPERATIONS</span>
          <h2>Student Talent Directory</h2>
          <p className="muted">
            Search and manage student profiles by single or multiple skill combinations (AND/OR), edit academic details, or directly enroll students into placement drives.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {canManage && (
            <button
              className="primary-button"
              onClick={openAddModal}
              style={{
                background: "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)",
                padding: "10px 18px",
                borderRadius: "8px",
                fontWeight: "700",
                fontSize: "13px"
              }}
            >
              + Add New Student
            </button>
          )}
          <button className="secondary-button" onClick={() => loadStudents(search, selectedSkills, skillMatchMode, selectedBranch, selectedMinCgpa)}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {successMsg && <div className="notice success">{successMsg}</div>}
      {error && <div className="notice error">{error}</div>}

      {/* FILTER CONTROLS PANEL */}
      <div className="panel" style={{ borderTop: "4px solid #4f46e5" }}>
        {/* Search Bar Row */}
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "18px", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 360px" }}>
            <input
              type="text"
              placeholder="Search by student name, roll number, department, or keyword..."
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
            🔍 Search Talent
          </button>
          {(search || selectedSkills.length > 0 || selectedBranch !== "All Branches" || selectedMinCgpa > 0) && (
            <button
              type="button"
              className="secondary-button"
              onClick={clearAllFilters}
              style={{ padding: "10px 16px", borderRadius: "8px", fontSize: "13px", whiteSpace: "nowrap" }}
            >
              ✕ Reset All Filters
            </button>
          )}
        </form>

        {/* Multi-Skill Filter Controls */}
        <div style={{ marginBottom: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px", flexWrap: "wrap", gap: "8px" }}>
            <label style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--color-text-muted, #64748b)" }}>
              Filter by Skill Tags (Select One or Multiple Skills):
            </label>

            {/* Match Mode Selector (AND / OR) */}
            {selectedSkills.length > 1 && (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "#f1f5f9", padding: "4px 10px", borderRadius: "20px", fontSize: "12px" }}>
                <span style={{ fontWeight: "600", color: "#475569" }}>Logic:</span>
                <button
                  type="button"
                  onClick={() => setSkillMatchMode("all")}
                  style={{
                    border: "none",
                    background: skillMatchMode === "all" ? "#4f46e5" : "transparent",
                    color: skillMatchMode === "all" ? "#ffffff" : "#475569",
                    padding: "3px 10px",
                    borderRadius: "14px",
                    fontSize: "11.5px",
                    fontWeight: "700",
                    cursor: "pointer"
                  }}
                >
                  Match ALL (AND)
                </button>
                <button
                  type="button"
                  onClick={() => setSkillMatchMode("any")}
                  style={{
                    border: "none",
                    background: skillMatchMode === "any" ? "#4f46e5" : "transparent",
                    color: skillMatchMode === "any" ? "#ffffff" : "#475569",
                    padding: "3px 10px",
                    borderRadius: "14px",
                    fontSize: "11.5px",
                    fontWeight: "700",
                    cursor: "pointer"
                  }}
                >
                  Match ANY (OR)
                </button>
              </div>
            )}
          </div>

          {/* Active Skills Bar */}
          {selectedSkills.length > 0 && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                flexWrap: "wrap",
                background: "#eef2ff",
                border: "1px solid #c7d2fe",
                borderRadius: "8px",
                padding: "8px 12px",
                marginBottom: "12px"
              }}
            >
              <span style={{ fontSize: "12px", fontWeight: "700", color: "#4338ca" }}>
                Active ({selectedSkills.length} {selectedSkills.length === 1 ? "Skill" : "Skills"}):
              </span>
              {selectedSkills.map((s) => (
                <span
                  key={s}
                  style={{
                    background: "#4f46e5",
                    color: "#ffffff",
                    fontSize: "12px",
                    fontWeight: "600",
                    padding: "3px 10px",
                    borderRadius: "16px",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px"
                  }}
                >
                  {s}
                  <span
                    onClick={() => removeSkill(s)}
                    style={{ cursor: "pointer", fontWeight: "800", fontSize: "12px" }}
                    title="Remove skill"
                  >
                    ✕
                  </span>
                </span>
              ))}
              <button
                type="button"
                onClick={clearAllSkills}
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#6366f1",
                  fontSize: "11.5px",
                  fontWeight: "700",
                  cursor: "pointer",
                  marginLeft: "auto",
                  textDecoration: "underline"
                }}
              >
                Clear Skills
              </button>
            </div>
          )}

          {/* Categorized Popular Skills */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {POPULAR_SKILL_CATEGORIES.map((cat) => (
              <div key={cat.category} style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                <span style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", minWidth: "120px" }}>
                  {cat.category}:
                </span>
                <div className="tag-list" style={{ gap: "6px", flexWrap: "wrap" }}>
                  {cat.skills.map((skill) => {
                    const isSelected = selectedSkills.some((s) => s.toLowerCase() === skill.toLowerCase());
                    return (
                      <button
                        key={skill}
                        type="button"
                        onClick={() => handleSkillToggle(skill)}
                        className="skill-tag"
                        style={{
                          cursor: "pointer",
                          padding: "5px 12px",
                          borderRadius: "16px",
                          border: isSelected ? "1.5px solid #4f46e5" : "1px solid #cbd5e1",
                          background: isSelected ? "#4f46e5" : "#ffffff",
                          color: isSelected ? "#ffffff" : "#334155",
                          fontWeight: isSelected ? "700" : "500",
                          fontSize: "11.5px",
                          transition: "all 0.15s ease",
                          boxShadow: isSelected ? "0 2px 6px rgba(79,70,229,0.25)" : "none"
                        }}
                      >
                        {isSelected ? `✓ ${skill}` : `+ ${skill}`}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Branch & CGPA Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px", paddingTop: "14px", borderTop: "1px solid #f1f5f9" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>
              Department / Branch:
            </label>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              style={{ width: "100%", padding: "9px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "13px" }}
            >
              {BRANCH_OPTIONS.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>
              Minimum CGPA Cutoff:
            </label>
            <select
              value={selectedMinCgpa}
              onChange={(e) => setSelectedMinCgpa(Number(e.target.value))}
              style={{ width: "100%", padding: "9px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "13px" }}
            >
              {CGPA_CUTOFFS.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* RESULTS LISTING */}
      <div className="panel">
        <div className="section-heading compact-heading" style={{ marginBottom: "12px" }}>
          <div>
            <span className="eyebrow">TALENT MATCHES</span>
            <h3>
              {students.length} Student Candidate{students.length === 1 ? "" : "s"} Found
            </h3>
          </div>
          {selectedSkills.length > 0 && (
            <span className="pill approved" style={{ fontWeight: "bold", fontSize: "12px" }}>
              Filtered by: {selectedSkills.join(", ")} {selectedSkills.length > 1 ? `(${skillMatchMode.toUpperCase()})` : ""}
            </span>
          )}
        </div>

        {loading ? (
          <p className="muted">Filtering student talent pool...</p>
        ) : students.length === 0 ? (
          <div className="empty-state compact-empty">
            <div className="empty-icon">◎</div>
            <h3>No matching students found</h3>
            <p>Try refining or selecting fewer skills, switching match logic to ANY (OR), or clearing branch/CGPA filters.</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Roll No</th>
                  <th>Candidate Name</th>
                  <th>Branch</th>
                  <th>CGPA</th>
                  <th>Batch</th>
                  <th>Email</th>
                  <th>Technical Skills</th>
                  {canManage && <th style={{ textAlign: "right" }}>Actions (Admin/Operator)</th>}
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id || student.roll_number}>
                    <td><strong style={{ fontFamily: "monospace", color: "#4f46e5" }}>{student.roll_number}</strong></td>
                    <td><strong>{student.name}</strong></td>
                    <td><span className="role-chip">{student.branch || "—"}</span></td>
                    <td>
                      <strong style={{ color: (student.cgpa || 0) >= 8.0 ? "#15803d" : (student.cgpa || 0) >= 7.0 ? "#1d4ed8" : "#b91c1c" }}>
                        {student.cgpa != null ? Number(student.cgpa).toFixed(2) : "—"}
                      </strong>
                    </td>
                    <td>{student.graduation_year || "—"}</td>
                    <td style={{ fontSize: "12px" }}>{student.email}</td>
                    <td>
                      {student.skills ? (
                        <div className="tag-list compact" style={{ gap: "4px" }}>
                          {student.skills
                            .split(/[|,]/)
                            .map((s) => s.split(":")[0].trim())
                            .filter(Boolean)
                            .map((skill) => {
                              const isMatch = selectedSkills.some(
                                (sel) => sel.toLowerCase() === skill.toLowerCase()
                              );
                              return (
                                <span
                                  className="skill-tag"
                                  key={skill}
                                  style={{
                                    background: isMatch ? "#dcfce7" : undefined,
                                    color: isMatch ? "#15803d" : undefined,
                                    fontWeight: isMatch ? "700" : "normal",
                                    border: isMatch ? "1.5px solid #86efac" : undefined
                                  }}
                                >
                                  {skill}
                                </span>
                              );
                            })}
                        </div>
                      ) : (
                        "—"
                      )}
                    </td>
                    {canManage && (
                      <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                        <div style={{ display: "inline-flex", gap: "6px" }}>
                          <button
                            type="button"
                            className="secondary-button"
                            title="Enroll directly into a campus drive bypassing eligibility"
                            onClick={() => openEnrollModal(student)}
                            style={{
                              padding: "6px 10px",
                              fontSize: "12px",
                              fontWeight: "700",
                              color: "#4338ca",
                              borderColor: "#c7d2fe",
                              background: "#eef2ff"
                            }}
                          >
                            ⚡ Add to Drive
                          </button>
                          <button
                            type="button"
                            className="secondary-button"
                            title="Edit student academic details"
                            onClick={() => openEditModal(student)}
                            style={{ padding: "6px 10px", fontSize: "12px" }}
                          >
                            ✏️ Edit
                          </button>
                          <button
                            type="button"
                            className="secondary-button"
                            title="Delete student"
                            onClick={() => handleDeleteStudent(student)}
                            style={{ padding: "6px 10px", fontSize: "12px", color: "#b91c1c" }}
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ADD / EDIT STUDENT MODAL */}
      {studentModalOpen && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(15, 23, 42, 0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px" }}>
          <div className="modal-card" style={{ background: "#ffffff", borderRadius: "12px", maxWidth: "600px", width: "100%", maxHeight: "90vh", overflowY: "auto", padding: "24px", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#4f46e5" }}>STUDENT RECORD MANAGEMENT</span>
                <h3 style={{ margin: "4px 0 0 0" }}>{isEditing ? `✏️ Edit Details: ${formData.name}` : "➕ Add New Student"}</h3>
              </div>
              <button className="secondary-button" onClick={() => setStudentModalOpen(false)} style={{ padding: "4px 10px" }}>✕</button>
            </div>

            <form onSubmit={handleSaveStudent} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Roll Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 21CS001"
                  value={formData.roll_number}
                  onChange={(e) => setFormData({ ...formData, roll_number: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Email Address *</label>
                <input
                  type="email"
                  required
                  placeholder="e.g. john@college.edu"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Department / Branch</label>
                <select
                  value={formData.branch}
                  onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                >
                  {BRANCH_OPTIONS.filter((b) => b !== "All Branches").map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>CGPA (0 - 10.0)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  required
                  value={formData.cgpa}
                  onChange={(e) => setFormData({ ...formData, cgpa: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Graduation Batch Year</label>
                <input
                  type="number"
                  required
                  value={formData.graduation_year}
                  onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>📞 Phone Number</label>
                <input
                  type="text"
                  placeholder="+91 98765 43210"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>💼 LinkedIn Profile URL</label>
                <input
                  type="text"
                  placeholder="https://linkedin.com/in/username"
                  value={formData.linkedin_url}
                  onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🐙 GitHub Profile URL</label>
                <input
                  type="text"
                  placeholder="https://github.com/username"
                  value={formData.github_url}
                  onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🟢 HackerRank Profile URL</label>
                <input
                  type="text"
                  placeholder="https://hackerrank.com/username"
                  value={formData.hackerrank_url}
                  onChange={(e) => setFormData({ ...formData, hackerrank_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🟠 LeetCode Profile URL</label>
                <input
                  type="text"
                  placeholder="https://leetcode.com/username"
                  value={formData.leetcode_url}
                  onChange={(e) => setFormData({ ...formData, leetcode_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>🌐 Personal Portfolio URL</label>
                <input
                  type="text"
                  placeholder="https://yourportfolio.dev"
                  value={formData.portfolio_url}
                  onChange={(e) => setFormData({ ...formData, portfolio_url: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Technical Skills (comma or pipe separated)</label>
                <input
                  type="text"
                  placeholder="e.g. Python, SQL, React, Docker, Embedded C, VLSI"
                  value={formData.skills}
                  onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>Professional Bio / Career Summary</label>
                <textarea
                  rows="2"
                  placeholder="Summary of student career interests and specialization..."
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", resize: "vertical" }}
                />
              </div>

              <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "12px", borderTop: "1px solid #e2e8f0", paddingTop: "14px" }}>
                <button type="button" className="secondary-button" onClick={() => setStudentModalOpen(false)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={actionLoading}
                  style={{ background: "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)", padding: "10px 22px" }}
                >
                  {actionLoading ? "Saving..." : isEditing ? "💾 Save Changes" : "➕ Create Student"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* FORCE ENROLL IN DRIVE MODAL (OVERRIDE ELIGIBILITY) */}
      {enrollModalOpen && selectedStudentForEnroll && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(15, 23, 42, 0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px" }}>
          <div className="modal-card" style={{ background: "#ffffff", borderRadius: "12px", maxWidth: "540px", width: "100%", padding: "24px", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px" }}>
              <div>
                <span className="eyebrow" style={{ color: "#d97706", fontWeight: "700" }}>ADMIN / OPERATOR OVERRIDE ENROLLMENT</span>
                <h3 style={{ margin: "4px 0 0 0" }}>⚡ Enroll in Drive (Irrespective of Eligibility)</h3>
              </div>
              <button className="secondary-button" onClick={() => setEnrollModalOpen(false)} style={{ padding: "4px 10px" }}>✕</button>
            </div>

            <div style={{ background: "#fef3c7", border: "1px solid #fde68a", borderRadius: "8px", padding: "12px 14px", marginBottom: "16px", fontSize: "13px", color: "#92400e" }}>
              <strong>⚠️ Eligibility Override Active:</strong> This allows Admin & Operator to manually register <strong>{selectedStudentForEnroll.name}</strong> ({selectedStudentForEnroll.roll_number}, CGPA: {selectedStudentForEnroll.cgpa}) directly into the recruitment drive, bypassing CGPA, branch, or skill criteria cutoffs.
            </div>

            <form onSubmit={handleForceEnroll} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Select Placement Drive:</label>
                <select
                  value={targetJobId}
                  onChange={(e) => setTargetJobId(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1.5px solid #cbd5e1", fontSize: "14px", fontWeight: "600" }}
                >
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      🏢 {j.company_name} — {j.title} (Cutoff: {j.minimum_cgpa}+ CGPA)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "6px" }}>Initial Candidate Status:</label>
                <select
                  value={targetStatus}
                  onChange={(e) => setTargetStatus(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "8px", border: "1.5px solid #cbd5e1", fontSize: "13px" }}
                >
                  <option value="applied">Applied (Standard Registration)</option>
                  <option value="shortlisted">Directly Shortlisted (Interview Ready)</option>
                  <option value="interview">Scheduled for Interview</option>
                </select>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "12px", borderTop: "1px solid #e2e8f0", paddingTop: "14px" }}>
                <button type="button" className="secondary-button" onClick={() => setEnrollModalOpen(false)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={actionLoading}
                  style={{ background: "linear-gradient(135deg, #d97706 0%, #b45309 100%)", color: "#ffffff", padding: "10px 22px", fontWeight: "700" }}
                >
                  {actionLoading ? "Enrolling..." : "⚡ Force Enroll Candidate"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}