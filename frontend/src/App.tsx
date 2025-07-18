import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PreferencesPage from "./pages/PreferencesPage";
import ErrorPage from "./pages/AutoErrorPage";
import LandingPage from "./pages/LandingPage"; // ← 추가

export default function App() {
  return (
    <Router basename="/news-bot">
      <Routes>
        <Route path="/" element={<LandingPage />} /> {/* ✅ 루트 페이지 추가 */}
        <Route path="/preferences" element={<PreferencesPage />} />
        <Route path="/error" element={<ErrorPage />} />
        <Route
          path="*"
          element={
            <div className="text-center mt-10 text-red-500">
              404: 페이지를 찾을 수 없습니다.
            </div>
          }
        />
      </Routes>
    </Router>
  );
}