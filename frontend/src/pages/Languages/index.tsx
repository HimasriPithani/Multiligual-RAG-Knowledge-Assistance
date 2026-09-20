import { ArrowLeft, Languages } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function LanguagesPage() {
  const navigate = useNavigate();

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
            <h1>Languages</h1>
            <p>Explore multilingual knowledge and translation options.</p>
          </div>
        </header>

        <section className="quick-action-card">
          <Languages size={32} />

          <h2>Language Support</h2>

          <p>
            Language selection and multilingual generation features will appear
            here.
          </p>

          <div>
            <p>Supported languages can be added next:</p>

            <ul>
              <li>English</li>
              <li>Hindi</li>
              <li>Telugu</li>
              <li>Tamil</li>
              <li>Kannada</li>
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}