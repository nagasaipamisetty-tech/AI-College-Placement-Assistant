
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";

const initialForm = {
  title: "",
  description: "",
  trainer: "",
  scheduled_at: ""
};

const FILE_ICONS = {
  pdf: "📄",
  image: "🖼️",
  note: "📝",
  document: "📎"
};

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Training({ user }) {
  const role = String(user.role || "").toLowerCase();
  const canCreate = ["admin", "training", "trainer"].includes(role);
  const canUpload = ["admin", "training", "trainer"].includes(role);

  // Sessions
  const [sessions, setSessions] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Materials
  const [materials, setMaterials] = useState([]);
  const [materialsLoading, setMaterialsLoading] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({ title: "", description: "", session_id: "" });
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Shared
  const [activeTab, setActiveTab] = useState("sessions"); // "sessions" | "materials"
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await api("/api/training/");
      setSessions(Array.isArray(result) ? result : result.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadMaterials = useCallback(async () => {
    setMaterialsLoading(true);
    try {
      const result = await api("/api/training/materials");
      setMaterials(Array.isArray(result) ? result : []);
    } catch {
      setMaterials([]);
    } finally {
      setMaterialsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();
    loadMaterials();
  }, [loadSessions, loadMaterials]);

  function updateField(e) {
    setForm((cur) => ({ ...cur, [e.target.name]: e.target.value }));
  }

  async function createSession(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await api("/api/training/", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null
        })
      });
      setMessage("Training session created successfully.");
      setForm(initialForm);
      await loadSessions();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function enroll(sessionId) {
    setError("");
    setMessage("");
    try {
      await api(`/api/training/${sessionId}/enroll`, { method: "POST" });
      setMessage("You have enrolled in the training session.");
      await loadSessions();
    } catch (err) {
      setError(err.message);
    }
  }

  // ── Upload Material ──────────────────────────────────────────────

  function handleFileDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) setUploadFile(file);
  }

  function handleFileInput(e) {
    const file = e.target.files[0];
    if (file) setUploadFile(file);
  }

  function resetUploadModal() {
    setUploadFile(null);
    setUploadForm({ title: "", description: "", session_id: "" });
    setUploadModalOpen(false);
  }

  async function handleUploadSubmit(e) {
    e.preventDefault();
    if (!uploadFile) {
      setError("Please select a file to upload.");
      return;
    }
    setUploading(true);
    setError("");
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("title", uploadForm.title || uploadFile.name);
      formData.append("description", uploadForm.description || "");
      if (uploadForm.session_id) {
        formData.append("session_id", uploadForm.session_id);
      }
      formData.append("file", uploadFile);

      const token = localStorage.getItem("placement_token");
      const res = await fetch("/api/training/materials/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      setMessage("Material uploaded successfully! Students can now access it.");
      resetUploadModal();
      await loadMaterials();
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function deleteMaterial(materialId) {
    if (!window.confirm("Delete this material? This cannot be undone.")) return;
    setError("");
    try {
      await api(`/api/training/materials/${materialId}`, { method: "DELETE" });
      setMessage("Material deleted.");
      await loadMaterials();
    } catch (err) {
      setError(err.message);
    }
  }

  function openDownload(material) {
    const token = localStorage.getItem("placement_token");
    const url = `${material.download_url}?token=${token}`;
    window.open(material.download_url, "_blank");
  }

  // ── Render ────────────────────────────────────────────────────────

  return (
    <div className="page-stack">
      {/* Header */}
      <div className="section-heading">
        <div>
          <span className="eyebrow">CAREER DEVELOPMENT</span>
          <h2>Training Programs</h2>
          <p className="muted">
            Build job-ready skills through training sessions and study materials.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          {canUpload && activeTab === "materials" && (
            <button className="primary-button" onClick={() => setUploadModalOpen(true)}>
              ⬆ Upload Material
            </button>
          )}
          <button className="secondary-button" onClick={() => { loadSessions(); loadMaterials(); }}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {/* Tab Switcher */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px", flexWrap: "wrap" }}>
        <button
          className={activeTab === "sessions" ? "primary-button" : "secondary-button"}
          onClick={() => setActiveTab("sessions")}
        >
          📅 Training Sessions ({sessions.length})
        </button>
        <button
          className={activeTab === "materials" ? "primary-button" : "secondary-button"}
          onClick={() => setActiveTab("materials")}
        >
          📁 Study Materials ({materials.length})
        </button>
      </div>

      {/* ── TAB 1: Sessions ── */}
      {activeTab === "sessions" && (
        <>
          {canCreate && (
            <form className="panel form-panel" onSubmit={createSession}>
              <h3>Create a training session</h3>
              <div className="form-grid">
                <div className="field">
                  <label>Session title *</label>
                  <input name="title" value={form.title} onChange={updateField} required />
                </div>
                <div className="field">
                  <label>Trainer</label>
                  <input name="trainer" value={form.trainer} onChange={updateField} />
                </div>
                <div className="field full-width">
                  <label>Scheduled date and time</label>
                  <input
                    name="scheduled_at"
                    type="datetime-local"
                    value={form.scheduled_at}
                    onChange={updateField}
                  />
                </div>
                <div className="field full-width">
                  <label>Description</label>
                  <textarea name="description" rows="3" value={form.description} onChange={updateField} />
                </div>
              </div>
              <button className="primary-button" disabled={saving}>
                {saving ? "Creating..." : "Create session →"}
              </button>
            </form>
          )}

          {loading ? (
            <div className="panel">Loading training sessions...</div>
          ) : sessions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✦</div>
              <h3>No training sessions available</h3>
              <p>Training sessions will appear here when they are created.</p>
            </div>
          ) : (
            <div className="training-grid">
              {sessions.map((session) => (
                <article className="training-card" key={session.id}>
                  <div className="training-card-icon">✦</div>
                  <span className="eyebrow">TRAINING SESSION</span>
                  <h3>{session.title}</h3>
                  <p>{session.description || "A learning opportunity to support your career development."}</p>

                  <div className="training-meta">
                    <span>◉ {session.trainer || "Trainer to be announced"}</span>
                    <span>
                      ◷{" "}
                      {session.scheduled_at
                        ? new Date(session.scheduled_at).toLocaleString()
                        : "Schedule to be announced"}
                    </span>
                  </div>

                  {/* Materials for this session */}
                  {materials.filter((m) => m.session_id === session.id).length > 0 && (
                    <div style={{ marginTop: "10px", padding: "8px 10px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", marginBottom: "6px", textTransform: "uppercase" }}>
                        📁 Study Materials ({materials.filter((m) => m.session_id === session.id).length})
                      </div>
                      {materials.filter((m) => m.session_id === session.id).map((m) => (
                        <div key={m.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "4px 0", borderTop: "1px solid #f1f5f9" }}>
                          <span style={{ fontSize: "12px" }}>
                            {FILE_ICONS[m.file_type] || "📎"} {m.title}
                            <span style={{ color: "#94a3b8", marginLeft: "6px" }}>({formatBytes(m.file_size)})</span>
                          </span>
                          <a
                            href={m.download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="secondary-button compact"
                            style={{ textDecoration: "none", fontSize: "11px" }}
                          >
                            ⬇ Open
                          </a>
                        </div>
                      ))}
                    </div>
                  )}

                  {role === "student" && (
                    <button
                      className="primary-button full-button"
                      style={{ marginTop: "12px" }}
                      onClick={() => enroll(session.id)}
                    >
                      Enroll now →
                    </button>
                  )}
                </article>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── TAB 2: Study Materials ── */}
      {activeTab === "materials" && (
        <div>
          {/* Upload CTA for trainers */}
          {canUpload && (
            <div
              style={{
                border: "2px dashed #c7d2fe",
                borderRadius: "12px",
                padding: "24px",
                textAlign: "center",
                background: "#f5f3ff",
                marginBottom: "20px",
                cursor: "pointer"
              }}
              onClick={() => setUploadModalOpen(true)}
            >
              <div style={{ fontSize: "36px", marginBottom: "8px" }}>⬆</div>
              <h3 style={{ margin: "0 0 6px 0", color: "#4338ca" }}>Upload Study Material</h3>
              <p className="muted" style={{ margin: 0 }}>
                Click to upload PDFs, images, notes, presentations, or documents for students to access.
              </p>
              <div style={{ display: "flex", gap: "8px", justifyContent: "center", marginTop: "12px", flexWrap: "wrap" }}>
                {["📄 PDF", "🖼️ Images", "📝 Notes (.txt/.md)", "📎 Word / PowerPoint"].map((t) => (
                  <span key={t} className="pill" style={{ background: "#e0e7ff", color: "#3730a3", fontWeight: "600" }}>{t}</span>
                ))}
              </div>
            </div>
          )}

          {materialsLoading ? (
            <p className="muted">Loading study materials...</p>
          ) : materials.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📁</div>
              <h3>No study materials uploaded yet</h3>
              <p>
                {canUpload
                  ? "Click \"Upload Material\" above to share resources with students."
                  : "Your trainer will upload study materials here for you to access."}
              </p>
            </div>
          ) : (
            <>
              {/* Filter pills by type */}
              <div style={{ marginBottom: "16px" }}>
                <p className="muted" style={{ marginBottom: "8px", fontWeight: "600" }}>
                  {materials.length} material{materials.length !== 1 ? "s" : ""} available
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
                {materials.map((m) => (
                  <article
                    key={m.id}
                    style={{
                      background: "#fff",
                      border: "1px solid #e2e8f0",
                      borderRadius: "12px",
                      padding: "16px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "8px",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
                    }}
                  >
                    {/* File type badge + icon */}
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <div
                        style={{
                          width: "44px",
                          height: "44px",
                          borderRadius: "10px",
                          background: m.file_type === "pdf" ? "#fee2e2" : m.file_type === "image" ? "#dcfce7" : m.file_type === "note" ? "#fef3c7" : "#e0e7ff",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "22px",
                          flexShrink: 0
                        }}
                      >
                        {FILE_ICONS[m.file_type] || "📎"}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: "700", fontSize: "14px", color: "#0f172a", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {m.title}
                        </div>
                        <div style={{ fontSize: "11px", color: "#94a3b8" }}>
                          {m.file_name} • {formatBytes(m.file_size)}
                        </div>
                      </div>
                    </div>

                    {m.description && (
                      <p style={{ margin: 0, fontSize: "12.5px", color: "#475569", lineHeight: "1.5" }}>
                        {m.description}
                      </p>
                    )}

                    {/* Meta */}
                    <div style={{ fontSize: "11px", color: "#94a3b8", display: "flex", gap: "12px", flexWrap: "wrap" }}>
                      <span>👤 {m.uploaded_by_name}</span>
                      <span>🕐 {new Date(m.uploaded_at).toLocaleDateString()}</span>
                      {m.session_id && (
                        <span>📅 Session #{m.session_id}</span>
                      )}
                    </div>

                    {/* Actions */}
                    <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
                      <a
                        href={m.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="primary-button"
                        style={{
                          flex: 1,
                          textAlign: "center",
                          textDecoration: "none",
                          fontSize: "13px",
                          fontWeight: "700",
                          padding: "8px 12px"
                        }}
                      >
                        {m.file_type === "image" ? "🖼️ View" : "⬇ Download / Open"}
                      </a>
                      {canUpload && (
                        <button
                          className="secondary-button"
                          style={{ fontSize: "13px", color: "#dc2626", borderColor: "#fca5a5", padding: "8px 12px" }}
                          onClick={() => deleteMaterial(m.id)}
                        >
                          🗑
                        </button>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* ── UPLOAD MODAL ── */}
      {uploadModalOpen && (
        <div
          className="modal-backdrop"
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
        >
          <div
            className="modal-card"
            style={{ background: "#fff", borderRadius: "14px", maxWidth: "520px", width: "92%", padding: "28px", boxShadow: "0 20px 40px rgba(0,0,0,0.18)" }}
          >
            {/* Modal Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #f1f5f9", paddingBottom: "14px", marginBottom: "20px" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "18px" }}>⬆ Upload Study Material</h3>
                <p className="muted" style={{ margin: "2px 0 0 0", fontSize: "12px" }}>
                  Share PDFs, images, notes, or documents with students
                </p>
              </div>
              <button className="secondary-button compact" onClick={resetUploadModal}>✕</button>
            </div>

            <form onSubmit={handleUploadSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {/* Drag & Drop Zone */}
              <div
                onDrop={handleFileDrop}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: `2px dashed ${dragOver ? "#4f46e5" : uploadFile ? "#10b981" : "#c7d2fe"}`,
                  borderRadius: "10px",
                  padding: "24px",
                  textAlign: "center",
                  background: dragOver ? "#eef2ff" : uploadFile ? "#f0fdf4" : "#fafafa",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.txt,.md,.docx,.pptx,.xlsx"
                  onChange={handleFileInput}
                  style={{ display: "none" }}
                />
                {uploadFile ? (
                  <>
                    <div style={{ fontSize: "28px" }}>{FILE_ICONS[uploadFile.name.endsWith(".pdf") ? "pdf" : uploadFile.type.startsWith("image") ? "image" : "note"] || "📎"}</div>
                    <div style={{ fontWeight: "700", color: "#166534", marginTop: "6px" }}>{uploadFile.name}</div>
                    <div style={{ fontSize: "12px", color: "#64748b" }}>{formatBytes(uploadFile.size)}</div>
                    <div style={{ fontSize: "12px", color: "#4f46e5", marginTop: "4px" }}>Click to change file</div>
                  </>
                ) : (
                  <>
                    <div style={{ fontSize: "32px" }}>📁</div>
                    <div style={{ fontWeight: "600", color: "#4338ca", marginTop: "6px" }}>
                      Drag & drop or click to browse
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>
                      PDF, PNG, JPG, GIF, TXT, MD, DOCX, PPTX, XLSX — max 50 MB
                    </div>
                  </>
                )}
              </div>

              {/* Title */}
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>
                  Material Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Data Structures Notes — Week 3"
                  value={uploadForm.title}
                  onChange={(e) => setUploadForm((p) => ({ ...p, title: e.target.value }))}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "7px", border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                />
              </div>

              {/* Description */}
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>
                  Description (optional)
                </label>
                <textarea
                  rows="2"
                  placeholder="Brief description of the material content..."
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm((p) => ({ ...p, description: e.target.value }))}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "7px", border: "1px solid #cbd5e1", resize: "vertical", boxSizing: "border-box" }}
                />
              </div>

              {/* Link to session */}
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#334155", marginBottom: "4px" }}>
                  Link to Training Session (optional)
                </label>
                <select
                  value={uploadForm.session_id}
                  onChange={(e) => setUploadForm((p) => ({ ...p, session_id: e.target.value }))}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: "7px", border: "1px solid #cbd5e1", background: "#fff" }}
                >
                  <option value="">— General / No specific session —</option>
                  {sessions.map((s) => (
                    <option key={s.id} value={s.id}>{s.title}</option>
                  ))}
                </select>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "4px" }}>
                <button type="button" className="secondary-button" onClick={resetUploadModal}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={uploading || !uploadFile}
                  style={{ minWidth: "140px" }}
                >
                  {uploading ? "Uploading..." : "⬆ Upload Material"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}