import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Mail, Lock, User } from "lucide-react";

import Logo from "../../components/common/Logo";
import Button from "../../components/common/Button";

const API_BASE_URL = "http://localhost:8000";

export default function Auth() {
  const navigate = useNavigate();

  const [isRegistering, setIsRegistering] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const endpoint = isRegistering
        ? `${API_BASE_URL}/auth/register`
        : `${API_BASE_URL}/auth/login`;

      const requestBody = isRegistering
        ? {
            name: name.trim(),
            email: email.trim().toLowerCase(),
            password,
          }
        : {
            email: email.trim().toLowerCase(),
            password,
          };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Authentication failed. Please try again."
        );
      }

      // Save JWT token for future API requests.
      localStorage.setItem("access_token", data.access_token);

      // Save logged-in user information.
      localStorage.setItem("user", JSON.stringify(data.user));

      setSuccess(
        isRegistering
          ? "Account created successfully."
          : "Signed in successfully."
      );

      // Redirect after successful authentication.
      navigate("/dashboard");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const switchAuthMode = () => {
    setIsRegistering((previousMode) => !previousMode);
    setError("");
    setSuccess("");
    setPassword("");
  };

  return (
    <div className="auth-page">
      <div className="auth-left">
        <Link to="/" className="auth-back-link">
          <ArrowLeft size={18} />
          Back to home
        </Link>

        <div className="auth-brand">
          <Logo />

          <h1>
            Explore Knowledge.
            <span> In Every Language.</span>
          </h1>

          <p>
            Connect with documents, discover insights, and ask questions using
            an intelligent multilingual assistant.
          </p>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-card-heading">
            <h2>{isRegistering ? "Create your account" : "Welcome back"}</h2>

            <p>
              {isRegistering
                ? "Start exploring your knowledge base."
                : "Sign in to continue to your knowledge assistant."}
            </p>
          </div>

          {error && (
            <div className="auth-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="auth-success" role="status">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            {isRegistering && (
              <div className="form-group">
                <label htmlFor="name">Full name</label>

                <div className="input-wrapper">
                  <User size={18} />

                  <input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    required
                    minLength={2}
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email address</label>

              <div className="input-wrapper">
                <Mail size={18} />

                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>

              <div className="input-wrapper">
                <Lock size={18} />

                <input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={isRegistering ? 8 : 1}
                />
              </div>
            </div>

            {!isRegistering && (
              <div className="auth-options">
                <label className="remember-me">
                  <input type="checkbox" />
                  Remember me
                </label>

                <button
                  type="button"
                  className="forgot-password"
                  onClick={() =>
                    alert("Password recovery will be added next.")
                  }
                >
                  Forgot password?
                </button>
              </div>
            )}

            <Button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : isRegistering
                  ? "Create account"
                  : "Sign in"}
            </Button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <p className="auth-switch">
            {isRegistering
              ? "Already have an account?"
              : "Don't have an account?"}

            <button type="button" onClick={switchAuthMode}>
              {isRegistering ? "Sign in" : "Create account"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}