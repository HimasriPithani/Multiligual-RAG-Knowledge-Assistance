import { CheckCircle2, Users, Target, Lightbulb } from "lucide-react";

const highlights = [
  "Access knowledge from documents in multiple languages",
  "Ask questions using natural language",
  "Receive context-aware and reliable answers",
  "Explore information through an intelligent interface",
];

export default function About() {
  return (
    <section className="about-section" id="about">
      <div className="about-container">
        <div className="about-content">
          <span className="section-label">ABOUT THE PROJECT</span>

          <h2>
            Making Knowledge
            <span> Accessible to Everyone</span>
          </h2>

          <p>
            The Multilingual RAG Knowledge Assistant combines document
            understanding, multilingual natural language processing, and
            retrieval-augmented generation to help users discover information
            quickly and accurately.
          </p>

          <div className="about-highlights">
            {highlights.map((highlight) => (
              <div className="about-highlight" key={highlight}>
                <CheckCircle2 size={20} />
                <span>{highlight}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="about-visual">
          <div className="about-card">
            <div className="about-card-icon">
              <Target size={28} />
            </div>

            <h3>Our Goal</h3>

            <p>
              Simplify access to complex information by connecting users with
              meaningful answers across languages and documents.
            </p>
          </div>

          <div className="about-card about-card-offset">
            <div className="about-card-icon">
              <Lightbulb size={28} />
            </div>

            <h3>Our Approach</h3>

            <p>
              Combine intelligent retrieval with language models to produce
              useful, context-aware responses.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}