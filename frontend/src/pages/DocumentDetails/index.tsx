import { useEffect, useState } from "react";
import { ArrowLeft, FileText } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

const API_BASE_URL = "http://localhost:8000";

interface DocumentItem {
  document_id: string;
  user_id: string;
  filename: string;
  file_type?: string | null;
  file_size?: number | null;
  language?: string | null;
  uploaded_at: string;
  chunk_count: number;
  status: string;
  error_message?: string | null;
}

export default function DocumentDetails() {
  const navigate = useNavigate();
  const { documentId } = useParams<{ documentId: string }>();

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDocument = async () => {
      if (!documentId) {
        setError("Document ID is missing.");
        setLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch(
          `${API_BASE_URL}/documents/${documentId}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Unable to load document."
          );
        }

        setDocument(data.document || data);
      } catch (err) {
        console.error("Failed to load document:", err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load document."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId]);

  return (
    <div className="dashboard-page">
      <main className="dashboard-main">
        <button
          type="button"
          className="document-action"
          onClick={() => navigate("/documents")}
        >
          <ArrowLeft size={16} />
          Back to Documents
        </button>

        <header className="dashboard-header">
          <div>
            <h1>Document Details</h1>
            <p>View information about your uploaded document.</p>
          </div>
        </header>

        {loading && <p>Loading document...</p>}

        {error && (
          <p className="documents-error">
            {error}
          </p>
        )}

        {!loading && !error && document && (
          <section className="document-details-card">
            <div className="document-details-icon">
              <FileText size={40} />
            </div>

            <h2>{document.filename}</h2>

            <div className="document-details-list">
              <p>
                <strong>Document ID:</strong>{" "}
                {document.document_id}
              </p>

              <p>
                <strong>File type:</strong>{" "}
                {document.file_type || "Unknown"}
              </p>

              <p>
                <strong>Language:</strong>{" "}
                {document.language || "Unknown"}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                {document.status}
              </p>

              <p>
                <strong>Chunks:</strong>{" "}
                {document.chunk_count}
              </p>

              <p>
                <strong>Uploaded at:</strong>{" "}
                {new Date(
                  document.uploaded_at
                ).toLocaleString()}
              </p>
            </div>

            {document.status === "ready" && (
              <div className="document-viewer-placeholder">
                <h3>Document Viewer</h3>

                <p>
                  Your document has been processed successfully.
                  The PDF viewer will be connected next.
                </p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}