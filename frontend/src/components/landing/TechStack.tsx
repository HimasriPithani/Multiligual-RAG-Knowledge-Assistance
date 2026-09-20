import type { ReactNode } from "react";

import {
  Code2,
  Server,
  Database,
  BrainCircuit,
  Languages,
  GitBranch,
} from "lucide-react";

interface Tech {
  icon: ReactNode;
  name: string;
  description: string;
}

const technologies: Tech[] = [
  {
    icon: <Code2 size={28} />,
    name: "React + TypeScript",
    description: "Responsive and type-safe frontend interface.",
  },
  {
    icon: <Server size={28} />,
    name: "FastAPI",
    description: "High-performance backend APIs and services.",
  },
  {
    icon: <BrainCircuit size={28} />,
    name: "Large Language Models",
    description: "AI-powered question answering and generation.",
  },
  {
    icon: <Database size={28} />,
    name: "Vector Database",
    description: "Semantic search using embeddings and vector storage.",
  },
  {
    icon: <Languages size={28} />,
    name: "Multilingual NLP",
    description: "Knowledge access across multiple languages.",
  },
  {
    icon: <GitBranch size={28} />,
    name: "RAG Pipeline",
    description: "Retrieval-augmented generation for grounded answers.",
  },
];

export default function TechStack() {
  return (
    <section className="tech-stack-section" id="tech-stack">
      <div className="section-container">
        <div className="section-heading">
          <span className="section-label">TECHNOLOGY</span>

          <h2>Built With Modern AI Technologies</h2>

          <p>
            A powerful combination of modern frontend, backend, NLP, and
            retrieval technologies.
          </p>
        </div>

        <div className="tech-stack-grid">
          {technologies.map((tech) => (
            <div className="tech-card" key={tech.name}>
              <div className="tech-icon">{tech.icon}</div>

              <div>
                <h3>{tech.name}</h3>
                <p>{tech.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}