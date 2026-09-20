import { ArrowUp, Mail } from "lucide-react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import Logo from "../common/Logo";

export default function Footer() {
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <footer className="footer" id="contact">
      <div className="footer-container">
        {/* Main footer */}
        <div className="footer-main">
          {/* Brand */}
          <div className="footer-brand">
            <Logo />

            <p>
              Explore knowledge across languages with an intelligent,
              AI-powered assistant.
            </p>
          </div>

          {/* Meet the developers */}
          <div className="footer-developers">
            <h3>Meet the Developers</h3>

            <p className="footer-developers-subtitle">
              Built with passion by final year students | Kakinada Institute
              of Engineering and Technology.
            </p>

            <div className="developer-cards">
              {/* Himashri */}
              <div className="developer-card">
                <div className="developer-avatar">
                  <span>👩🏻‍💻</span>
                </div>

                <div className="developer-info">
                  <h4>Himashri Pitani</h4>

                  <p>Backend and AI Developer</p>

                  <span>NLP - LLMs - RAG - Python - FastAPI</span>

                  <div className="developer-socials">
                    <a
                      href="https://github.com/HimasriPithani"
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Himashri GitHub"
                    >
                      <FaGithub size={15} />
                    </a>

                    <a
                      href="https://www.linkedin.com/in/himasripithani/"
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Himashri LinkedIn"
                    >
                      <FaLinkedin size={15} />
                    </a>

                    <a
                      href="mailto:himasri17.p@gmail.com"
                      aria-label="Email Himashri"
                    >
                      <Mail size={15} />
                    </a>
                  </div>
                </div>
              </div>

              {/* Sashank */}
              <div className="developer-card">
                <div className="developer-avatar">
                  <span>👨🏻‍💻</span>
                </div>

                <div className="developer-info">
                  <h4>Sashank</h4>

                  <p>Frontend and UI/UX Developer</p>

                  <span>React - UI/UX - Web Development</span>

                  <div className="developer-socials">
                    <a
                      href="https://github.com/SashankTatavolu"
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Sashank GitHub"
                    >
                      <FaGithub size={15} />
                    </a>

                    <a
                      href="https://www.linkedin.com/in/sashanktatavolu/"
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Sashank LinkedIn"
                    >
                      <FaLinkedin size={15} />
                    </a>

                    <a
                      href="mailto:sashanktatavolu@gmail.com"
                      aria-label="Email Sashank"
                    >
                      <Mail size={15} />
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quote */}
          <div className="footer-quote">
            <blockquote>
              Making knowledge
              <br />
              accessible, in every language,
              <br />
              for a smarter tomorrow.
            </blockquote>

            <p>- Multilingual RAG Knowledge Assistant</p>
          </div>
        </div>

        {/* Bottom */}
        <div className="footer-bottom">
          <p>
            {new Date().getFullYear()} Multilingual RAG Knowledge Assistant.
            Built for learning, sharing and a better tomorrow.
          </p>

          <div className="footer-bottom-links">
            <a href="https://github.com" target="_blank" rel="noreferrer">
              GitHub
            </a>

            <span>|</span>

            <a href="#how-it-works">Documentation</a>

            <span>|</span>

            <a href="#contact">Contact</a>
          </div>

          <button
            className="back-to-top"
            onClick={scrollToTop}
            aria-label="Back to top"
            title="Back to top"
          >
            <ArrowUp size={18} />
          </button>
        </div>
      </div>
    </footer>
  );
}