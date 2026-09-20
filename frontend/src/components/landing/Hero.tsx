
import { ArrowRight, Globe, FileText, Sparkles } from "lucide-react";

import Button from "../common/Button";

export default function Hero() {
  return (
    <section className="hero-section" id="home">
      <div className="hero-container">

        {/* Left Content */}
        <div className="hero-content">

          <div className="hero-badge">
            <Sparkles size={16} />
            AI-Powered Knowledge Assistant
          </div>

          <h1>
            Explore Knowledge.
            <br />
            <span>In Every Language.</span>
          </h1>

          <p>
            Your intelligent multilingual knowledge assistant
            for understanding documents, asking questions,
            and discovering insights across languages.
          </p>

          <div className="hero-buttons">
            <Button
              onClick={() => {
                window.location.href = "/auth";
              }}
            >
              Get Started
              <ArrowRight size={18} />
            </Button>

            <Button
              variant="outline"
              onClick={() => {
                document
                  .getElementById("how-it-works")
                  ?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              How It Works
            </Button>
          </div>

          <div className="hero-trust">
            <Globe size={18} />
            <span>Understand. Ask. Discover.</span>
          </div>

        </div>

        {/* Right Illustration */}
        <div className="hero-visual">

          <div className="hero-glow"></div>

          <div className="hero-card">

            <div className="hero-card-header">
              <div className="hero-card-icon">
                <FileText size={22} />
              </div>

              <div>
                <h3>Knowledge Explorer</h3>
                <p>Multilingual Document AI</p>
              </div>
            </div>

            <div className="hero-document">
              <div className="document-line large"></div>
              <div className="document-line"></div>
              <div className="document-line medium"></div>
              <div className="document-line short"></div>

              <div className="document-highlight">
                <span>ज्ञान</span>
                <span>Knowledge</span>
              </div>

              <div className="document-line"></div>
              <div className="document-line medium"></div>
              <div className="document-line short"></div>
            </div>

            <div className="hero-languages">
              <span>English</span>
              <span>हिन्दी</span>
              <span>తెలుగు</span>
              <span>தமிழ்</span>
            </div>

            <div className="hero-answer">
              <Sparkles size={18} />
              <div>
                <strong>AI Insights</strong>
                <p>Answers from your documents</p>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}