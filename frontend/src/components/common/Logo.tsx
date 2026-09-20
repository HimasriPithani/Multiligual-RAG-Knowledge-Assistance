
import { BookOpen } from "lucide-react";

interface LogoProps {
  showText?: boolean;
}

export default function Logo({ showText = true }: LogoProps) {
  return (
    <div className="logo-container">
      <div className="logo-icon">
        <BookOpen size={24} strokeWidth={2.5} />
      </div>

      {showText && (
        <span className="logo-text">
          Multilingual RAG
        </span>
      )}
    </div>
  );
}