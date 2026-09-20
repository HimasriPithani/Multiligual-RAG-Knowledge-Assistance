
import { Link } from "react-router-dom";

import Logo from "../common/Logo";
import Button from "../common/Button";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">

        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <Logo />
        </Link>

        {/* Navigation Links */}
        <div className="navbar-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#tech-stack">Tech Stack</a>
          <a href="#about">About</a>
        </div>

        {/* Authentication Buttons */}
        <div className="navbar-actions">
          <Link to="/auth">
            <Button variant="outline">
              Login
            </Button>
          </Link>

          <Link to="/auth">
            <Button>
              Get Started
            </Button>
          </Link>
        </div>

      </div>
    </nav>
  );
}