
import { useRef, useState } from "react";
import { api } from "../api";

export default function ImportCSV() {
  const fileInput = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Only .csv files are supported.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api("/api/admin/import-students", {
        method: "POST",
        body: formData
      });

      setResult(response);
      setFile(null);

      if (fileInput.current) {
        fileInput.current.value = "";
      }
    } catch (err) {
      setError(err.message || "CSV upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="section-heading">
        <div>
          <span className="eyebrow">DATA MANAGEMENT</span>
          <h2>Import student records</h2>
          <p className="muted">
            Upload a CSV file to create or update student records.
          </p>
        </div>
      </div>

      {error && <div className="notice error">{error}</div>}

      {result && (
        <div className="notice success">
          <strong>Import request completed.</strong>
          <pre className="result-json">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      <form className="panel import-panel" onSubmit={handleUpload}>
        <div className="upload-icon">⇧</div>
        <h3>Upload a student CSV</h3>
        <p className="muted">
          Select the file from your computer. It does not need to be in a
          particular folder.
        </p>

        <label className="drop-zone" htmlFor="csv-file">
          <span className="drop-icon">▤</span>
          <strong>{file ? file.name : "Choose your CSV file"}</strong>
          <span>
            {file
              ? `${(file.size / 1024).toFixed(1)} KB`
              : "Click to browse files on your computer"}
          </span>
          <input
            ref={fileInput}
            id="csv-file"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => {
              setFile(event.target.files?.[0] || null);
              setError("");
              setResult(null);
            }}
          />
        </label>

        <button className="primary-button upload-button" disabled={loading || !file}>
          {loading ? "Uploading..." : "Upload and import →"}
        </button>
      </form>

      <section className="panel">
        <h3>Required CSV columns</h3>
        <p className="muted">
          Use these column names in the first row of your CSV file.
        </p>

        <div className="required-columns">
          <span>roll_number</span>
          <span>name</span>
          <span>email</span>
        </div>

        <h4>Optional columns</h4>
        <div className="required-columns optional-columns">
          <span>branch</span>
          <span>cgpa</span>
          <span>graduation_year</span>
          <span>skills</span>
        </div>

        <div className="csv-example">
          <div className="csv-example-header">
            <strong>Example CSV format</strong>
            <span>CSV</span>
          </div>
          <pre>{`roll_number,name,email,branch,cgpa,graduation_year,skills
STU001,Sample Student,student1@example.com,CSE,8.5,2027,Java SQL
STU002,Another Student,student2@example.com,IT,7.8,2027,Python HTML`}</pre>
        </div>

        <p className="privacy-note">
          Use synthetic data for testing. Do not upload real student data to a
          public repository.
        </p>
      </section>
    </div>
  );
}