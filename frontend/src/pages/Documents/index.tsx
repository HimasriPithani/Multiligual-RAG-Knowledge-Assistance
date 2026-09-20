import { useEffect, useState } from "react";
import { FileText, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://localhost:8000";

interface DocumentItem {
  document_id: string;
  filename: string;
  file_type?: string | null;
  language?: string | null;
  uploaded_at: string;
  chunk_count: number;
  status: string;
}

export default function Documents() {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch(`${API_BASE_URL}/documents`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Unable to load documents.");
        }

        setDocuments(data.documents || []);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load documents."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDocuments();
  }, []);

  return (
    <div className="dashboard-page">
      <main className="dashboard-main">
        <button
          type="button"
          className="document-action"
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>

        <header className="dashboard-header">
          <div>
            <h1>Documents</h1>
            <p>View all documents in your knowledge base.</p>
          </div>
        </header>

        {loading && <p>Loading documents...</p>}

        {error && <p className="documents-error">{error}</p>}

        {!loading && !error && documents.length === 0 && (
          <p className="documents-status">
            No documents uploaded yet.
          </p>
        )}

        {!loading && !error && documents.length > 0 && (
          <div className="documents-list">
            {documents.map((document) => (
              <div
                className="document-row"
                key={document.document_id}
              >
                <div className="document-icon">
                  <FileText size={24} />
                </div>

                <div className="document-info">
                  <h3>{document.filename}</h3>

                  <p>
                    {document.file_type || "Document"} ·{" "}
                    {document.language || "Unknown language"}
                  </p>

                  <span className={`document-status ${document.status}`}>
                    {document.status}
                  </span>
                </div>

                <button
                type="button"
                className="document-action"
                onClick={() =>
                    navigate(`/documents/${document.document_id}`)
                }
                >
                Open
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}