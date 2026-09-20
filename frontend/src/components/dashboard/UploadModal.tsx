import { useState } from "react";

interface UploadModalProps {
  onClose: () => void;
  onUploadSuccess: () => void;
}

const API_BASE_URL = "http://localhost:8000";

export default function UploadModal({
  onClose,
  onUploadSuccess,
}: UploadModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a document first.");
      return;
    }

    setUploading(true);
    setError("");
    setMessage("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Please sign in before uploading a document.");
      }

      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setMessage("Document uploaded successfully.");

      // Reload the document list in Dashboard.
      await onUploadSuccess();

      // Close the modal after refreshing the list.
      setTimeout(() => {
        onClose();
      }, 700);
    } catch (error) {
      console.error("Upload failed:", error);

      setError(
        error instanceof Error ? error.message : "Upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-modal">
      <div className="upload-modal-content">
        <h2>Upload Document</h2>

        <p>Add a PDF or text document to your knowledge base.</p>

        <input
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={(event) => {
            const file = event.target.files?.[0] || null;

            setSelectedFile(file);
            setError("");
            setMessage("");
          }}
        />

        {selectedFile && <p>{selectedFile.name}</p>}

        {message && <p className="auth-success">{message}</p>}

        {error && <p className="auth-error">{error}</p>}

        <div className="upload-actions">
          <button
            type="button"
            onClick={onClose}
            disabled={uploading}
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
          >
            {uploading ? "Uploading..." : "Upload Document"}
          </button>
        </div>
      </div>
    </div>
  );
}