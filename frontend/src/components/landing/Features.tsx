
import {
  FileText,
  Languages,
  BrainCircuit,
  ShieldCheck,
} from "lucide-react";

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: <FileText size={28} />,
    title: "Document Understanding",
    description:
      "Upload your documents and explore their content with an intelligent knowledge assistant.",
  },
  {
    icon: <Languages size={28} />,
    title: "Multilingual Support",
    description:
      "Ask questions and understand information across multiple Indian and international languages.",
  },
  {
    icon: <BrainCircuit size={28} />,
    title: "AI-Powered Answers",
    description:
      "Retrieve relevant information from your documents and generate meaningful answers using RAG.",
  },
  {
    icon: <ShieldCheck size={28} />,
    title: "Reliable Knowledge",
    description:
      "Ground answers in your uploaded documents to help you explore information with confidence.",
  },
];

export default function Features() {
  return (
    <section className="features-section" id="features">
      <div className="features-container">

        {/* Section Header */}
        <div className="section-header">
          <span className="section-badge">
            Powerful Features
          </span>

          <h2>
            Everything You Need to
            <span> Explore Knowledge</span>
          </h2>

          <p>
            A smarter way to understand documents,
            ask questions, and discover insights in
            multiple languages.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="features-grid">
          {features.map((feature) => (
            <div className="feature-card" key={feature.title}>
              <div className="feature-icon">
                {feature.icon}
              </div>

              <h3>{feature.title}</h3>

              <p>{feature.description}</p>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}