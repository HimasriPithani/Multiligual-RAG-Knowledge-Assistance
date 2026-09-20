import { useEffect, useRef, useState } from "react";
import { ChevronDown, Check } from "lucide-react";

interface Option {
  value: string;
  label: string;
}

interface CustomSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  ariaLabel: string;
  compact?: boolean;
  icon?: React.ReactNode;
}

/**
 * Fully custom dropdown, styled entirely by our own CSS variables.
 * Replaces the native <select>, whose open-list popup is rendered by
 * the OS/browser (e.g. GTK on Linux Chrome) and ignores color-scheme
 * and page CSS, causing a white popup even in dark mode.
 */
export default function CustomSelect({
  value,
  onChange,
  options,
  ariaLabel,
  compact = false,
  icon,
}: CustomSelectProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const selected = options.find((o) => o.value === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div
      className={`custom-select${compact ? " compact" : ""}${open ? " open" : ""}`}
      ref={rootRef}
    >
      <button
        type="button"
        className="custom-select-trigger"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={ariaLabel}
      >
        {icon}
        <span className="custom-select-value">{selected?.label ?? value}</span>
        <ChevronDown size={16} className="custom-select-chevron" />
      </button>

      {open && (
        <ul className="custom-select-list" role="listbox" aria-label={ariaLabel}>
          {options.map((option) => (
            <li
              key={option.value}
              role="option"
              aria-selected={option.value === value}
              className={`custom-select-option${
                option.value === value ? " selected" : ""
              }`}
              onClick={() => {
                onChange(option.value);
                setOpen(false);
              }}
            >
              <span>{option.label}</span>
              {option.value === value && <Check size={14} />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}