import { FormEvent, useState } from "react";
import { ArrowLeft, Send, Bot, User, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://localhost:8000";

interface SourceItem {
  document_id?: string;
  filename?: string;
  page?: number;
  score?: number;
  text?: string;
}

interface ChatResponse {
  answer: string;
  sources?: SourceItem[];
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
}

export default function AskQuestion() {
  const navigate = useNavigate();

  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("English");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError("Please login before asking a question.");
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previousMessages) => [
      ...previousMessages,
      userMessage,
    ]);

    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          language,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to get an answer."
        );
      }

      const chatResponse: ChatResponse = data;

      const assistantMessage: Message = {
        role: "assistant",
        content:
          chatResponse.answer || "No answer was returned.",
        sources: chatResponse.sources || [],
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        assistantMessage,
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to get an answer."
      );
    } finally {
      setLoading(false);
    }
  };

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
            <h1>Ask a Question</h1>
            <p>
              Ask questions and find answers from your documents.
            </p>
          </div>
        </header>

        <section className="chat-container">
          <div className="chat-header">
            <div className="chat-title">
              <Bot size={24} />
              <div>
                <h2>Multilingual Knowledge Assistant</h2>
                <p>
                  Ask questions using the documents in your knowledge base.
                </p>
              </div>
            </div>

            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              className="language-select"
              aria-label="Answer language"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi</option>
              <option value="Telugu">Telugu</option>
              <option value="Tamil">Tamil</option>
              <option value="Kannada">Kannada</option>
              <option value="Malayalam">Malayalam</option>
              <option value="Bengali">Bengali</option>
              <option value="Marathi">Marathi</option>
            </select>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-empty-state">
                <Bot size={40} />
                <h3>How can I help you?</h3>
                <p>
                  Ask a question about the documents you uploaded.
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`chat-message ${
                  message.role === "user"
                    ? "chat-message-user"
                    : "chat-message-assistant"
                }`}
              >
                <div className="chat-message-icon">
                  {message.role === "user" ? (
                    <User size={18} />
                  ) : (
                    <Bot size={18} />
                  )}
                </div>

                <div className="chat-message-content">
                  <strong>
                    {message.role === "user"
                      ? "You"
                      : "Knowledge Assistant"}
                  </strong>

                  <p>{message.content}</p>

                  {message.sources &&
                    message.sources.length > 0 && (
                      <div className="chat-sources">
                        <h4>Sources</h4>

                        {message.sources.map((source, sourceIndex) => (
                          <div
                            key={`${source.document_id}-${sourceIndex}`}
                            className="chat-source"
                          >
                            <strong>
                              {source.filename ||
                                source.document_id ||
                                "Document source"}
                            </strong>

                            {source.page && (
                              <span>
                                Page {source.page}
                              </span>
                            )}

                            {source.text && (
                              <p>{source.text}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-message chat-message-assistant">
                <div className="chat-message-icon">
                  <Bot size={18} />
                </div>

                <div className="chat-message-content">
                  <strong>Knowledge Assistant</strong>
                  <p className="chat-loading">
                    <Loader2 size={16} className="spin-icon" />
                    Searching your documents...
                  </p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="documents-error">
              {error}
            </div>
          )}

          <form
            className="chat-input-container"
            onSubmit={askQuestion}
          >
            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask something about your documents..."
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="primary-button"
            >
              {loading ? (
                <Loader2 size={18} className="spin-icon" />
              ) : (
                <Send size={18} />
              )}
              Ask
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}