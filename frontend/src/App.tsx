import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import AskQuestion from "./pages/AskQuestion";
import Languages from "./pages/Languages";
import DocumentDetails from "./pages/DocumentDetails";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/auth" element={<Auth />} />

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/documents" element={<Documents />} />

        <Route
          path="/documents/:documentId"
          element={<DocumentDetails />}
        />

        <Route path="/ask-question" element={<AskQuestion />} />

        <Route path="/languages" element={<Languages />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;