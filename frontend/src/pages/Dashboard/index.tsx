import { useEffect, useRef, useState } from "react";
import {
  ChevronRight,
  Eye,
  EyeOff,
  FileText,
  Globe,
  History,
  Loader2,
  LogOut,
  Moon,
  Paperclip,
  Send,
  Settings,
  SquarePen,
  Sun,
  Trash2,
  X,
} from "lucide-react";

import "../../styles/Dashboard.css";
import CustomSelect from "../../components/dashboard/CustomSelect";

const API_BASE_URL = "http://localhost:8000";

const STORAGE_LIMIT_MB = 100;

const ACCEPTED_TYPES = ".pdf,.txt,.docx";

const LANGUAGES = [
  { value: "auto", label: "Auto" },
  { value: "en", label: "English" },
  { value: "hi", label: "हिन्दी" },
  { value: "te", label: "తెలుగు" },
  { value: "ta", label: "தமிழ்" },
  { value: "bn", label: "বাংলা" },
];

const SIDEBAR_LANGUAGES = [
  { value: "auto", label: "Auto-detect" },
  ...LANGUAGES.filter((item) => item.value !== "auto"),
];

const EXAMPLE_QUESTIONS = [
  "What are the key findings in this document?",
  "इस दस्तावेज़ का सारांश क्या है?",
  "ఈ పత్రంలో ముఖ్య అంశాలు ఏమిటి?",
  "What is the eligibility criteria?",
];

interface ChatSource {
  document?: string;
  document_id?: string;
  page?: number | null;
  chunk_id?: string;
  similarity?: number;
  text?: string | null;
}

interface MessageAttachment {
  id: string;
  name: string;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  attachments?: MessageAttachment[];
  failed?: boolean;
}

interface Attachment {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "ready" | "failed";
  documentId?: string;
  error?: string;
}

interface StoredUser {
  name?: string;
  full_name?: string;
  email?: string;
  created_at?: string;
}

interface DocumentItem {
  document_id: string;
  filename: string;
  file_type?: string | null;
  file_size?: number | null;
  language?: string | null;
  uploaded_at: string;
  status: string;
}

interface ChatSessionSummary {
  session_id: string;
  title?: string | null;
  created_at: string;
  updated_at?: string | null;
}

interface ChatSessionMessage {
  message_id: string;
  role: string;
  content: string;
  created_at: string;
}

type ActiveView = "chat" | "documents" | "history" | "settings";

const createId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const formatDate = (value?: string | null) => {
  if (!value) return "";

  try {
    return new Date(value).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return value;
  }
};

export default function Dashboard() {
  const [user, setUser] = useState<StoredUser | null>(null);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("auto");
  const [isAsking, setIsAsking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Attachments waiting in the composer, not sent yet.
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  // Attachments already sent and still "in context" for this conversation.
  const [sessionAttachments, setSessionAttachments] = useState<Attachment[]>(
    []
  );

  const [storageUsedMb, setStorageUsedMb] = useState(0);

  const [activeView, setActiveView] = useState<ActiveView>("chat");

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [deletingDocumentId, setDeletingDocumentId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [sessionsError, setSessionsError] = useState("");
  const [openingSessionId, setOpeningSessionId] = useState<string | null>(null);

  const [settingsName, setSettingsName] = useState("");
  const [settingsPassword, setSettingsPassword] = useState("");
  const [settingsPasswordVisible, setSettingsPasswordVisible] = useState(false);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [settingsMessage, setSettingsMessage] = useState("");
  const [settingsError, setSettingsError] = useState("");

  const threadEndRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("user");

    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        setUser(parsed);
        setSettingsName(parsed?.name || parsed?.full_name || "");
      } catch {
        setUser(null);
      }
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAsking]);

  const authHeaders = (): Record<string, string> => {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  /* ---------- documents + storage ---------- */

  const loadStorageUsage = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/documents`, {
        headers: authHeaders(),
      });

      if (!response.ok) return;

      const data = await response.json();

      const totalBytes = (data.documents || []).reduce(
        (sum: number, item: { file_size?: number | null }) =>
          sum + (item.file_size || 0),
        0
      );

      setStorageUsedMb(totalBytes / (1024 * 1024));
    } catch (error) {
      console.error("Failed to load storage usage:", error);
    }
  };

  useEffect(() => {
    loadStorageUsage();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoadingDocuments(true);
      setDocumentsError("");

      if (!localStorage.getItem("access_token")) {
        setDocumentsError("Please sign in to view your documents.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/documents`, {
        headers: authHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load documents.");
      }

      setDocuments(data.documents || []);
    } catch (error) {
      setDocumentsError(
        error instanceof Error ? error.message : "Unable to load documents."
      );
    } finally {
      setLoadingDocuments(false);
    }
  };

  const deleteDocument = async (documentId: string, filename: string) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?\n\nThis will remove the document and its indexed data from your knowledge base.`
    );

    if (!confirmed) return;

    try {
      setDeletingDocumentId(documentId);
      setDocumentsError("");

      const response = await fetch(
        `${API_BASE_URL}/documents/${documentId}`,
        {
          method: "DELETE",
          headers: authHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to delete document.");
      }

      // Remove it immediately from the UI
      setDocuments((previous) =>
        previous.filter((item) => item.document_id !== documentId)
      );

      // Recalculate storage usage
      await loadStorageUsage();
    } catch (error) {
      setDocumentsError(
        error instanceof Error
          ? error.message
          : "Unable to delete document."
      );
    } finally {
      setDeletingDocumentId(null);
    }
  };

  const openDocuments = () => {
    setActiveView("documents");
    loadDocuments();
  };

  /* ---------- chat history ---------- */

  const loadSessions = async () => {
    try {
      setLoadingSessions(true);
      setSessionsError("");

      if (!localStorage.getItem("access_token")) {
        setSessionsError("Please sign in to view chat history.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
        headers: authHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load chat history.");
      }

      setSessions(data.sessions || []);
    } catch (error) {
      setSessionsError(
        error instanceof Error ? error.message : "Unable to load chat history."
      );
    } finally {
      setLoadingSessions(false);
    }
  };

  const openHistory = () => {
    setActiveView("history");
    loadSessions();
  };

  const openSession = async (id: string) => {
    try {
      setOpeningSessionId(id);

      const response = await fetch(`${API_BASE_URL}/chat/sessions/${id}`, {
        headers: authHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to open this conversation.");
      }

      const loadedMessages: ChatMessage[] = (data.messages || []).map(
        (item: ChatSessionMessage) => ({
          id: item.message_id,
          role: item.role === "assistant" ? "assistant" : "user",
          content: item.content,
        })
      );

      setMessages(loadedMessages);
      setSessionId(data.session?.session_id || id);
      setAttachments([]);
      setSessionAttachments([]);
      setActiveView("chat");
    } catch (error) {
      setSessionsError(
        error instanceof Error
          ? error.message
          : "Unable to open this conversation."
      );
    } finally {
      setOpeningSessionId(null);
    }
  };

  const deleteSession = async (id: string, event: React.MouseEvent) => {
    event.stopPropagation();

    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Unable to delete this conversation.");
      }

      setSessions((previous) => previous.filter((item) => item.session_id !== id));

      if (sessionId === id) {
        setSessionId(null);
      }
    } catch (error) {
      setSessionsError(
        error instanceof Error
          ? error.message
          : "Unable to delete this conversation."
      );
    }
  };

  /* ---------- settings ---------- */

  const openSettings = () => {
    setActiveView("settings");
    setSettingsMessage("");
    setSettingsError("");
    setSettingsPassword("");
  };

  const handleSaveSettings = async (event: React.FormEvent) => {
    event.preventDefault();

    setSettingsSaving(true);
    setSettingsMessage("");
    setSettingsError("");

    try {
      const payload: Record<string, string> = {};

      if (settingsName.trim() && settingsName.trim() !== user?.name) {
        payload.name = settingsName.trim();
      }

      if (settingsPassword) {
        payload.password = settingsPassword;
      }

      if (Object.keys(payload).length === 0) {
        setSettingsMessage("Nothing to update.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/users/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to update your profile.");
      }

      const updatedUser = data.user || { ...user, name: payload.name };
      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));
      setSettingsPassword("");
      setSettingsMessage("Your changes have been saved.");
    } catch (error) {
      setSettingsError(
        error instanceof Error ? error.message : "Unable to update your profile."
      );
    } finally {
      setSettingsSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    window.location.href = "/";
  };

  /* ---------- attachments ---------- */

  const uploadFile = async (file: File, attachmentId: string) => {
    try {
      if (!localStorage.getItem("access_token")) {
        throw new Error("Sign in again to upload documents.");
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        headers: authHeaders(),
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setAttachments((previous) =>
        previous.map((item) =>
          item.id === attachmentId
            ? { ...item, status: "ready", documentId: data.document_id }
            : item
        )
      );

      loadStorageUsage();

      if (activeView === "documents") {
        loadDocuments();
      }
    } catch (error) {
      setAttachments((previous) =>
        previous.map((item) =>
          item.id === attachmentId
            ? {
                ...item,
                status: "failed",
                error:
                  error instanceof Error ? error.message : "Upload failed.",
              }
            : item
        )
      );
    }
  };

  const handleFilesSelected = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(event.target.files || []);

    files.forEach((file) => {
      const attachmentId = createId();

      setAttachments((previous) => [
        ...previous,
        {
          id: attachmentId,
          name: file.name,
          size: file.size,
          status: "uploading",
        },
      ]);

      uploadFile(file, attachmentId);
    });

    event.target.value = "";
  };

  const removeAttachment = (attachmentId: string) => {
    setAttachments((previous) =>
      previous.filter((item) => item.id !== attachmentId)
    );
  };

  const removeSessionAttachment = (attachmentId: string) => {
    setSessionAttachments((previous) =>
      previous.filter((item) => item.id !== attachmentId)
    );
  };

  /* ---------- chat ---------- */

  const askQuestion = async (rawQuestion: string) => {
    const trimmed = rawQuestion.trim();

    if (!trimmed || isAsking) return;

    // Attachments finishing upload right now are excluded — the send
    // button is disabled while anything is still "uploading", so by the
    // time this runs every attachment is either ready or failed.
    const newlyReady = attachments.filter(
      (item) => item.status === "ready" && item.documentId
    );

    const combinedContext = [
      ...sessionAttachments,
      ...newlyReady.filter(
        (item) =>
          !sessionAttachments.some((existing) => existing.id === item.id)
      ),
    ];

    const documentIds = combinedContext
      .map((item) => item.documentId)
      .filter((value): value is string => Boolean(value));

    setMessages((previous) => [
      ...previous,
      {
        id: createId(),
        role: "user",
        content: trimmed,
        attachments:
          newlyReady.length > 0
            ? newlyReady.map((item) => ({ id: item.id, name: item.name }))
            : undefined,
      },
    ]);

    setSessionAttachments(combinedContext);
    // Clear the composer of attachments that just got sent; keep any that
    // are still failed so the person can see the error or remove them.
    setAttachments((previous) => previous.filter((item) => item.status === "failed"));

    setQuestion("");
    setIsAsking(true);

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    try {
      if (!localStorage.getItem("access_token")) {
        throw new Error("Your session expired. Sign in again to ask questions.");
      }

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify({
          question: trimmed,
          language: language === "auto" ? null : language,
          document_ids: documentIds.length > 0 ? documentIds : null,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "That question could not be answered.");
      }

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      setMessages((previous) => [
        ...previous,
        {
          id: createId(),
          role: "assistant",
          content: data.answer || "No answer was returned for this question.",
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: createId(),
          role: "assistant",
          failed: true,
          content:
            error instanceof Error
              ? error.message
              : "That question could not be answered.",
        },
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    askQuestion(question);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion(question);
    }
  };

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(event.target.value);

    const element = event.target;
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 160)}px`;
  };

  const startNewChat = () => {
    setActiveView("chat");
    setMessages([]);
    setAttachments([]);
    setSessionAttachments([]);
    setQuestion("");
    setSessionId(null);
  };

  const displayName = user?.name || user?.full_name || "there";
  const initial = displayName.charAt(0).toUpperCase();

  const storagePercent = Math.min(
    (storageUsedMb / STORAGE_LIMIT_MB) * 100,
    100
  );

  const isUploading = attachments.some((item) => item.status === "uploading");

  return (
    <div className="chat-page">
      <aside className="chat-sidebar">
        <div className="chat-brand">
          <span className="chat-brand-mark">
            <FileText size={18} />
          </span>
          <span className="chat-brand-name">Multilingual RAG</span>
        </div>

        <nav className="chat-nav">
          <button
            type="button"
            className={`chat-nav-link${activeView === "chat" ? " active" : ""}`}
            onClick={startNewChat}
          >
            <SquarePen size={18} />
            New Chat
          </button>

          <button
            type="button"
            className={`chat-nav-link${
              activeView === "documents" ? " active" : ""
            }`}
            onClick={openDocuments}
          >
            <FileText size={18} />
            My Documents
            <ChevronRight size={16} className="chat-nav-chevron" />
          </button>

          <button
            type="button"
            className={`chat-nav-link${
              activeView === "history" ? " active" : ""
            }`}
            onClick={openHistory}
          >
            <History size={18} />
            Chat History
          </button>

          <button
            type="button"
            className={`chat-nav-link${
              activeView === "settings" ? " active" : ""
            }`}
            onClick={openSettings}
          >
            <Settings size={18} />
            Settings
          </button>
        </nav>

        <div className="chat-sidebar-card">
          <p className="chat-sidebar-card-title">Languages</p>

          <CustomSelect
            value={language}
            onChange={setLanguage}
            ariaLabel="Answer language"
            icon={<Globe size={16} />}
            options={SIDEBAR_LANGUAGES}
          />
        </div>

        <div className="chat-sidebar-card">
          <p className="chat-sidebar-card-title">Storage Usage</p>

          <div
            className="chat-storage-bar"
            role="progressbar"
            aria-valuenow={Math.round(storagePercent)}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <span
              className="chat-storage-fill"
              style={{ width: `${storagePercent}%` }}
            />
          </div>

          <p className="chat-storage-text">
            {storageUsedMb.toFixed(1)} MB / {STORAGE_LIMIT_MB} MB
          </p>
        </div>

        <button
          type="button"
          className="chat-user chat-user-button"
          onClick={openSettings}
        >
          <span className="chat-user-avatar">{initial}</span>

          <span className="chat-user-details">
            <span className="chat-user-name">{displayName}</span>
            <span className="chat-user-email">{user?.email}</span>
          </span>
        </button>
      </aside>

      <main className="chat-main">
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          multiple
          onChange={handleFilesSelected}
          hidden
        />

        <header className="chat-topbar">
          <div>
            <h1>Ask. Learn. Explore.</h1>
            <p>Your documents, your questions, in any language.</p>
          </div>

          <div className="chat-topbar-actions">
            <button
              type="button"
              className="chat-icon-button"
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              aria-label={
                theme === "light"
                  ? "Switch to dark mode"
                  : "Switch to light mode"
              }
            >
              {theme === "light" ? <Sun size={19} /> : <Moon size={19} />}
            </button>

            <button
              type="button"
              className="chat-logout-button"
              onClick={handleLogout}
            >
              <LogOut size={17} />
              Logout
            </button>
          </div>
        </header>

        {activeView === "documents" && (
          <div className="chat-body">
            <section className="docs-view">
              <div className="docs-view-header">
                <div>
                  <h2>My Documents</h2>
                  <p>Everything you've added to your knowledge base.</p>
                </div>

                <button
                  type="button"
                  className="docs-upload-button"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Paperclip size={16} />
                  Upload document
                </button>
              </div>

              {loadingDocuments && (
                <p className="docs-status">Loading documents...</p>
              )}

              {documentsError && (
                <p className="docs-status error">{documentsError}</p>
              )}

              {!loadingDocuments &&
                !documentsError &&
                documents.length === 0 &&
                attachments.length === 0 && (
                  <p className="docs-status">No documents uploaded yet.</p>
                )}

              {attachments.length > 0 && (
                <div className="docs-list">
                  {attachments.map((attachment) => (
                    <div
                      key={attachment.id}
                      className={`docs-row ${attachment.status}`}
                    >
                      <span className="docs-row-icon">
                        {attachment.status === "uploading" ? (
                          <Loader2 size={18} className="chat-spin" />
                        ) : (
                          <FileText size={18} />
                        )}
                      </span>

                      <div className="docs-row-info">
                        <h3>{attachment.name}</h3>
                        <p>
                          {attachment.status === "uploading"
                            ? "Uploading..."
                            : attachment.status === "failed"
                            ? attachment.error
                            : formatSize(attachment.size)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!loadingDocuments && !documentsError && documents.length > 0 && (
                <div className="docs-list">
                  {documents.map((document) => (
                    <div className="docs-row" key={document.document_id}>
                      <span className="docs-row-icon">
                        <FileText size={18} />
                      </span>

                      <div className="docs-row-info">
                        <h3>{document.filename}</h3>

                        <p>
                          {document.file_type
                            ? document.file_type.toUpperCase()
                            : "DOCUMENT"}{" "}
                          · {document.language || "Detecting language"} ·{" "}
                          {formatSize(document.file_size || 0)}
                        </p>
                      </div>

                      <span className={`docs-row-status ${document.status}`}>
                        {document.status}
                      </span>

                      <button
                        type="button"
                        className="docs-delete-button"
                        onClick={() =>
                          deleteDocument(document.document_id, document.filename)
                        }
                        disabled={deletingDocumentId === document.document_id}
                        aria-label={`Delete ${document.filename}`}
                        title="Delete document"
                      >
                        {deletingDocumentId === document.document_id ? (
                          <Loader2 size={17} className="chat-spin" />
                        ) : (
                          <Trash2 size={17} />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {activeView === "history" && (
          <div className="chat-body">
            <section className="docs-view">
              <div className="docs-view-header">
                <div>
                  <h2>Chat History</h2>
                  <p>Pick up a past conversation where you left off.</p>
                </div>
              </div>

              {loadingSessions && (
                <p className="docs-status">Loading conversations...</p>
              )}

              {sessionsError && (
                <p className="docs-status error">{sessionsError}</p>
              )}

              {!loadingSessions && !sessionsError && sessions.length === 0 && (
                <p className="docs-status">
                  No conversations yet. Ask a question to start one.
                </p>
              )}

              {!loadingSessions && !sessionsError && sessions.length > 0 && (
                <div className="docs-list">
                  {sessions.map((session) => (
                    <button
                      type="button"
                      key={session.session_id}
                      className="history-row"
                      onClick={() => openSession(session.session_id)}
                    >
                      <span className="docs-row-icon">
                        {openingSessionId === session.session_id ? (
                          <Loader2 size={18} className="chat-spin" />
                        ) : (
                          <History size={18} />
                        )}
                      </span>

                      <div className="docs-row-info">
                        <h3>{session.title || "Untitled conversation"}</h3>
                        <p>
                          {formatDate(session.updated_at || session.created_at)}
                        </p>
                      </div>

                      <span
                        className="history-delete"
                        onClick={(event) =>
                          deleteSession(session.session_id, event)
                        }
                        role="button"
                        tabIndex={-1}
                        aria-label="Delete conversation"
                      >
                        <Trash2 size={16} />
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {activeView === "settings" && (
          <div className="chat-body">
            <section className="docs-view settings-view">
              <div className="docs-view-header">
                <div>
                  <h2>Settings</h2>
                  <p>Manage your profile and account preferences.</p>
                </div>
              </div>

              <form className="settings-form" onSubmit={handleSaveSettings}>
                <label className="settings-field">
                  <span>Name</span>
                  <input
                    type="text"
                    value={settingsName}
                    onChange={(event) => setSettingsName(event.target.value)}
                    placeholder="Your name"
                  />
                </label>

                <label className="settings-field">
                  <span>Email</span>
                  <input type="email" value={user?.email || ""} disabled />
                </label>

                <label className="settings-field">
                  <span>New password</span>
                  <div className="settings-password-input">
                    <input
                      type={settingsPasswordVisible ? "text" : "password"}
                      value={settingsPassword}
                      onChange={(event) =>
                        setSettingsPassword(event.target.value)
                      }
                      placeholder="Leave blank to keep your current password"
                      minLength={8}
                    />
                    <button
                      type="button"
                      className="settings-password-toggle"
                      onClick={() =>
                        setSettingsPasswordVisible(!settingsPasswordVisible)
                      }
                      aria-label={
                        settingsPasswordVisible
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {settingsPasswordVisible ? (
                        <EyeOff size={16} />
                      ) : (
                        <Eye size={16} />
                      )}
                    </button>
                  </div>
                </label>

                <div className="settings-field">
                  <span>Appearance</span>
                  <div className="settings-theme-toggle">
                    <button
                      type="button"
                      className={theme === "light" ? "active" : ""}
                      onClick={() => setTheme("light")}
                    >
                      <Sun size={15} />
                      Light
                    </button>
                    <button
                      type="button"
                      className={theme === "dark" ? "active" : ""}
                      onClick={() => setTheme("dark")}
                    >
                      <Moon size={15} />
                      Dark
                    </button>
                  </div>
                </div>

                {settingsMessage && (
                  <p className="docs-status success">{settingsMessage}</p>
                )}

                {settingsError && (
                  <p className="docs-status error">{settingsError}</p>
                )}

                <div className="settings-actions">
                  <button
                    type="submit"
                    className="settings-save-button"
                    disabled={settingsSaving}
                  >
                    {settingsSaving ? "Saving..." : "Save changes"}
                  </button>
                </div>
              </form>
            </section>
          </div>
        )}

        {activeView === "chat" && (
          <div className="chat-body">
            {messages.length === 0 && (
              <>
                <section className="chat-greeting">
                  <h2>
                    <span className="chat-greeting-wave">👋</span> Hello{" "}
                    {displayName}!
                  </h2>
                  <p>
                    Upload documents and start asking questions in your
                    language.
                  </p>
                </section>

                <section className="chat-examples">
                  <p className="chat-examples-label">
                    Try an example question:
                  </p>

                  <div className="chat-examples-grid">
                    {EXAMPLE_QUESTIONS.map((example) => (
                      <button
                        type="button"
                        key={example}
                        className="chat-example-card"
                        onClick={() => askQuestion(example)}
                      >
                        <span className="chat-example-icon">
                          <FileText size={18} />
                        </span>
                        {example}
                      </button>
                    ))}
                  </div>
                </section>
              </>
            )}

            {messages.length > 0 && (
              <section className="chat-thread">
                {messages.map((message) => (
                  <article
                    key={message.id}
                    className={`chat-message ${message.role}${
                      message.failed ? " failed" : ""
                    }`}
                  >
                    {message.attachments && message.attachments.length > 0 && (
                      <div className="chat-message-attachments">
                        {message.attachments.map((attachment) => (
                          <span
                            key={attachment.id}
                            className="chat-message-attachment"
                          >
                            <FileText size={13} />
                            {attachment.name}
                          </span>
                        ))}
                      </div>
                    )}

                    <p className="chat-message-text">{message.content}</p>

                    {message.sources && message.sources.length > 0 && (
                      <ul className="chat-message-sources">
                        {message.sources.map((source, index) => (
                          <li key={`${message.id}-${index}`}>
                            <FileText size={14} />
                            {source.document || "Source"}
                          </li>
                        ))}
                      </ul>
                    )}
                  </article>
                ))}

                {isAsking && (
                  <article className="chat-message assistant">
                    <span className="chat-typing">
                      <span />
                      <span />
                      <span />
                    </span>
                  </article>
                )}

                <div ref={threadEndRef} />
              </section>
            )}
          </div>
        )}

        {activeView === "chat" && (
          <form className="chat-composer" onSubmit={handleSubmit}>
            {sessionAttachments.length > 0 && (
              <div className="chat-context-bar">
                <span className="chat-context-label">Using in this chat:</span>

                {sessionAttachments.map((attachment) => (
                  <span key={attachment.id} className="chat-context-chip">
                    <FileText size={12} />
                    {attachment.name}
                    <button
                      type="button"
                      onClick={() => removeSessionAttachment(attachment.id)}
                      aria-label={`Stop using ${attachment.name}`}
                    >
                      <X size={11} />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {attachments.length > 0 && (
              <div className="chat-attachments">
                {attachments.map((attachment) => (
                  <div
                    key={attachment.id}
                    className={`chat-attachment ${attachment.status}`}
                    title={attachment.error || attachment.name}
                  >
                    <span className="chat-attachment-icon">
                      {attachment.status === "uploading" ? (
                        <Loader2 size={15} className="chat-spin" />
                      ) : (
                        <FileText size={15} />
                      )}
                    </span>

                    <span className="chat-attachment-details">
                      <span className="chat-attachment-name">
                        {attachment.name}
                      </span>
                      <span className="chat-attachment-meta">
                        {attachment.status === "uploading"
                          ? "Uploading..."
                          : attachment.status === "failed"
                          ? attachment.error
                          : formatSize(attachment.size)}
                      </span>
                    </span>

                    <button
                      type="button"
                      className="chat-attachment-remove"
                      onClick={() => removeAttachment(attachment.id)}
                      aria-label={`Remove ${attachment.name}`}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <textarea
              ref={textareaRef}
              value={question}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder="Ask your question in any language..."
            />

            <div className="chat-composer-tools">
              <button
                type="button"
                className="chat-icon-button"
                onClick={() => fileInputRef.current?.click()}
                aria-label="Attach a document"
              >
                <Paperclip size={18} />
              </button>

              <div className="chat-composer-right">
                <CustomSelect
                  value={language}
                  onChange={setLanguage}
                  ariaLabel="Answer language"
                  icon={<Globe size={16} />}
                  compact
                  options={LANGUAGES}
                />

                <button
                  type="submit"
                  className="chat-send-button"
                  disabled={!question.trim() || isAsking || isUploading}
                  aria-label="Send question"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}