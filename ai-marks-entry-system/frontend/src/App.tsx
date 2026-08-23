import { useEffect, useRef, useState } from "react";
import "./App.css";

interface Student {
  enrollment_no: string;
  name: string;
  marks: number | string;
  status: string;
  issues: string[];
}

function App() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [uploadedFile, setUploadedFile] = useState("");
  const [filter, setFilter] = useState("ALL");
  const [confirmed, setConfirmed] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/students")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch students");
        }

        return response.json();
      })
      .then((data) => {
        const formattedData = data.map((student: any) => ({
          enrollment_no: String(student.enrollment_no),
          name: student.name,
          marks: student.marks,
          status: "MATCHED",
          issues: [],
        }));

        setStudents(formattedData);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not connect to backend");
        setLoading(false);
      });
  }, []);

  // --------------------------------
  // OPEN FILE PICKER
  // --------------------------------

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  // --------------------------------
  // UPLOAD EXCEL
  // --------------------------------

  const handleUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setError("");
    setConfirmed(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      console.log("Uploading:", file.name);

      const response = await fetch(
        "http://127.0.0.1:8000/api/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      console.log("FastAPI response:", data);

      if (!data.success) {
        setError(data.error || "Invalid Excel file");
        return;
      }

      setStudents(data.records);
      setUploadedFile(data.filename);
      setFilter("ALL");

    } catch (err) {
      console.error(err);
      setError("Could not upload the Excel file");
    } finally {
      setUploading(false);

      // Allows selecting the same file again
      event.target.value = "";
    }
  };

  // --------------------------------
  // COUNTS
  // --------------------------------

  const matchedCount = students.filter(
    (student) => student.status === "MATCHED"
  ).length;

  const reviewCount = students.filter(
    (student) => student.status !== "MATCHED"
  ).length;

  const unmatchedCount = students.filter(
    (student) => student.status === "UNMATCHED"
  ).length;

  // --------------------------------
  // FILTER
  // --------------------------------

  const filteredStudents = students.filter((student) => {
    if (filter === "ALL") {
      return true;
    }

    if (filter === "MATCHED") {
      return student.status === "MATCHED";
    }

    if (filter === "REVIEW") {
      return student.status !== "MATCHED";
    }

    if (filter === "UNMATCHED") {
      return student.status === "UNMATCHED";
    }

    return true;
  });

  // --------------------------------
  // CONFIRM MARKS
  // --------------------------------

  const handleConfirm = async () => {
    if (students.length === 0) {
      setError("No marks available to confirm.");
      return;
    }

    if (reviewCount > 0) {
      setError(
        "Please resolve all records requiring review before confirmation."
      );
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/confirm",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            records: students,
          }),
        }
      );

      const data = await response.json();

      if (!data.success) {
        setError(data.message || "Confirmation failed.");
        return;
      }

      setConfirmed(true);
      setError("");

    } catch {
      setError("Could not connect to backend.");
    }
  };

  // --------------------------------
  // STATUS STYLE
  // --------------------------------

  const getStatusClass = (status: string) => {
    switch (status) {
      case "MATCHED":
        return "status-badge matched";

      case "DUPLICATE":
        return "status-badge duplicate";

      case "UNMATCHED":
        return "status-badge unmatched";

      case "INVALID MARKS":
        return "status-badge invalid";

      case "MISSING MARKS":
        return "status-badge missing";

      default:
        return "status-badge review";
    }
  };

  // --------------------------------
  // UI
  // --------------------------------

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>AI Marks Entry System</h1>
          <p>Internal Examination Management</p>
        </div>

        <span className="status">
          ● Backend Connected
        </span>
      </header>

      <main className="container">

        {/* SUMMARY */}

        <section className="summary-grid">

          <div className="card">
            <span>Total Records</span>
            <strong>{students.length}</strong>
          </div>

          <div className="card">
            <span>Matched</span>
            <strong>{matchedCount}</strong>
          </div>

          <div className="card">
            <span>Review</span>
            <strong>{reviewCount}</strong>
          </div>

          <div className="card">
            <span>Unmatched</span>
            <strong>{unmatchedCount}</strong>
          </div>

        </section>

        {/* MAIN PANEL */}

        <section className="panel">

          <div className="panel-header">

            <div>
              <h2>Student Records</h2>

              <p>
                {uploadedFile
                  ? `Uploaded: ${uploadedFile}`
                  : "Students retrieved from FastAPI backend"}
              </p>
            </div>

            <div className="review-controls">

              {/* FILTER */}

              <select
                value={filter}
                onChange={(event) =>
                  setFilter(event.target.value)
                }
              >
                <option value="ALL">
                  All Records
                </option>

                <option value="MATCHED">
                  Matched
                </option>

                <option value="REVIEW">
                  Needs Review
                </option>

                <option value="UNMATCHED">
                  Unmatched
                </option>
              </select>

              {/* HIDDEN FILE INPUT */}

              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls"
                onChange={handleUpload}
                disabled={uploading}
                style={{ display: "none" }}
              />

              {/* UPLOAD BUTTON */}

              <button
                type="button"
                className="upload-button"
                onClick={openFilePicker}
                disabled={uploading}
              >
                {uploading
                  ? "Uploading..."
                  : "Upload Excel"}
              </button>

              {/* CONFIRM */}

              <button
                type="button"
                className="confirm-button"
                onClick={handleConfirm}
                disabled={
                  confirmed ||
                  students.length === 0
                }
              >
                {confirmed
                  ? "Marks Confirmed ✓"
                  : "Confirm Marks"}
              </button>

            </div>
          </div>

          {/* LOADING */}

          {loading && (
            <p className="message">
              Loading students...
            </p>
          )}

          {/* ERROR */}

          {error && (
            <p className="error">
              {error}
            </p>
          )}

          {/* TABLE */}

          {!loading && !error && (
            <>

              <table>

                <thead>
                  <tr>
                    <th>Enrollment No.</th>
                    <th>Student Name</th>
                    <th>Marks</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>

                  {filteredStudents.length > 0 ? (

                    filteredStudents.map(
                      (student, index) => (

                        <tr
                          key={`${student.enrollment_no}-${index}`}
                        >

                          <td>
                            {student.enrollment_no}
                          </td>

                          <td>
                            {student.name}
                          </td>

                          <td>
                            {student.marks}
                          </td>

                          <td>

                            <span
                              className={getStatusClass(
                                student.status
                              )}
                            >
                              {student.status}
                            </span>

                          </td>

                        </tr>

                      )
                    )

                  ) : (

                    <tr>
                      <td
                        colSpan={4}
                        className="empty-state"
                      >
                        No records found for this filter.
                      </td>
                    </tr>

                  )}

                </tbody>

              </table>

              {/* CONFIRMATION */}

              {confirmed && (

                <div className="confirmation-message">

                  ✓ All marks have been reviewed and confirmed.

                </div>

              )}

            </>
          )}

        </section>

      </main>

    </div>
  );
}

export default App;