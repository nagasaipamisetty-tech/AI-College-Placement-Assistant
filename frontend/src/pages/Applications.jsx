
import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const statusOptions = [
  "applied",
  "shortlisted",
  "interview",
  "selected",
  "rejected"
];

export default function Applications({ user }) {
  const role = String(user.role || "").toLowerCase();
  const isStudent = role === "student";
  const canManage = ["admin", "operator"].includes(role);

  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      if (isStudent) {
        const [applicationResult, jobResult] = await Promise.all([
          api("/api/applications/mine"),
          api("/api/jobs/")
        ]);

        setApplications(
          Array.isArray(applicationResult)
            ? applicationResult
            : applicationResult.items || []
        );

        setJobs(
          (Array.isArray(jobResult) ? jobResult : jobResult.items || []).filter(
            (job) => job.status === "approved"
          )
        );
      } else if (canManage) {
        const result = await api("/api/applications/");
        setApplications(Array.isArray(result) ? result : result.items || []);
      } else {
        setError("Your role does not have access to applications.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isStudent, canManage]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function applyForJob(event) {
    event.preventDefault();

    if (!selectedJob) {
      setError("Please select a job.");
      return;
    }

    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await api("/api/applications/", {
        method: "POST",
        body: JSON.stringify({ job_id: Number(selectedJob) })
      });

      setMessage("Your application has been submitted.");
      setSelectedJob("");
      await loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function updateStatus(applicationId, status) {
    setError("");
    setMessage("");

    try {
      await api(`/api/applications/${applicationId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status })
      });

      setMessage("Application status updated.");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">APPLICATION TRACKING</span>
          <h2>{isStudent ? "My applications" : "Manage applications"}</h2>
          <p className="muted">
            {isStudent
              ? "Apply for eligible opportunities and track your progress."
              : "Review applications and update their progress."}
          </p>
        </div>
        <button className="secondary-button" onClick={loadData}>↻ Refresh</button>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {isStudent && (
        <form className="panel apply-form" onSubmit={applyForJob}>
          <h3>Apply for an opportunity</h3>
          <div className="inline-form">
            <select
              value={selectedJob}
              onChange={(event) => setSelectedJob(event.target.value)}
              required
            >
              <option value="">Select a job</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} — {job.company_name || job.company || "Company"}
                </option>
              ))}
            </select>
            <button className="primary-button" disabled={submitting}>
              {submitting ? "Applying..." : "Apply now"}
            </button>
          </div>
          <p className="muted small-text">
            The backend checks eligibility before accepting your application.
          </p>
        </form>
      )}

      <div className="panel">
        {loading ? (
          <p className="muted">Loading applications...</p>
        ) : applications.length === 0 ? (
          <div className="empty-state compact-empty">
            <h3>No applications yet</h3>
            <p>Applications will appear here when they are submitted.</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {!isStudent && <th>Student</th>}
                  <th>Job</th>
                  <th>Company</th>
                  <th>Applied on</th>
                  <th>Status</th>
                  {canManage && <th>Update status</th>}
                </tr>
              </thead>
              <tbody>
                {applications.map((application) => (
                  <tr key={application.id}>
                    {!isStudent && (
                      <td>{application.student_name || application.roll_number || application.student_id || "—"}</td>
                    )}
                    <td>
                      {application.job_title ||
                        application.job?.title ||
                        `Job #${application.job_id}`}
                    </td>
                    <td>
                      {application.company_name ||
                        application.company ||
                        application.job?.company_name ||
                        "—"}
                    </td>
                    <td>
                      {application.applied_at
                        ? new Date(application.applied_at).toLocaleDateString()
                        : "—"}
                    </td>
                    <td>
                      <span className={`status-badge ${application.status}`}>
                        {application.status || "applied"}
                      </span>
                    </td>
                    {canManage && (
                      <td>
                        <select
                          value={application.status || "applied"}
                          onChange={(event) =>
                            updateStatus(application.id, event.target.value)
                          }
                        >
                          {statusOptions.map((status) => (
                            <option key={status} value={status}>
                              {status}
                            </option>
                          ))}
                        </select>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}