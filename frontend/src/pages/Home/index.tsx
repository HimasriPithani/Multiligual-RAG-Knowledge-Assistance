import Navbar from "../../components/landing/Navbar";
import Hero from "../../components/landing/Hero";
import Features from "../../components/landing/Features";
import HowItWorks from "../../components/landing/HowItWorks";
import TechStack from "../../components/landing/TechStack";
import About from "../../components/landing/About";
import Footer from "../../components/landing/Footer";

export default function Home() {
  return (
    <div>
      <Navbar />

      <main>
        <Hero />

        <section id="features">
          <Features />
        </section>

        <section id="how-it-works">
          <HowItWorks />
        </section>

        <section id="tech-stack">
          <TechStack />
        </section>

        <section id="about">
          <About />
        </section>
      </main>

      <Footer />
    </div>
  );
}