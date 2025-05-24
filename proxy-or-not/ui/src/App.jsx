import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import Page1 from "./Page1";
import Page2 from "./Page2";

function App() {
  const [count, setCount] = useState(0);

  return (
    <BrowserRouter basename="/app">
      <div>
        <a href="https://vite.dev" target="_blank" rel="noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <nav style={{ marginBottom: 20 }}>
        <Link to="/page1" style={{ marginRight: 10 }}>
          Page 1
        </Link>
        <Link to="/page2">Page 2</Link>
      </nav>
      <div className="card">
        <button type="button" onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <Routes>
        <Route path="/page1" element={<Page1 />} />
        <Route path="/page2" element={<Page2 />} />
        <Route
          path="/"
          element={
            <div>
              <h1>Welcome to the React App</h1>
              <p>Select a page above.</p>
            </div>
          }
        />
      </Routes>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </BrowserRouter>
  );
}

export default App;
