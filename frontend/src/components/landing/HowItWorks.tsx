
import {
  Upload,
  MessageCircleQuestion,
  Sparkles,
  ArrowRight,
} from "lucide-react";

interface Step {
  number: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const steps: Step[] = [
  {
    number: "01",
    title: "Upload Documents",
    description:
      "Upload PDFs and other supported documents to build your personal knowledge base.",
    icon: <Upload size={28} />,
  },
  {
    number: "02",
    title: "Ask Questions",
    description:
      "Ask questions in your preferred language and explore information from your documents.",
    icon: <MessageCircleQuestion size={28} />,
  },
  {
    number: "03",
    title: "Get Intelligent Answers",
    description:
      "Receive relevant, AI-powered answers grounded in your uploaded knowledge.",
    icon: <Sparkles size={28} />,
  },
];

export default function HowItWorks() {
  return (
    <section className="how-it-works-section" id="how-it-works">
      <div className="how-it-works-container">

        {/* Section Header */}
        <div className="section-header">
          <span className="section-badge">
            Simple & Powerful
          </span>

          <h2>
            How It <span>Works</span>
          </h2>

          <p>
            Start exploring your knowledge in just
            three simple steps.
          </p>
        </div>

        {/* Steps */}
        <div className="steps-grid">
          {steps.map((step, index) => (
            <div className="step-wrapper" key={step.number}>

              <div className="step-card">

                <div className="step-top">
                  <span className="step-number">
                    {step.number}
                  </span>

                  <div className="step-icon">
                    {step.icon}
                  </div>
                </div>

                <h3>{step.title}</h3>

                <p>{step.description}</p>

              </div>

              {/* Arrow between cards */}
              {index < steps.length - 1 && (
                <ArrowRight
                  className="step-arrow"
                  size={24}
                />
              )}

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}