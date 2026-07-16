import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

// creates the root React container on our empty #root div inside index.html,
// then mounts our entire <App /> component tree inside of it.
ReactDOM.createRoot(document.getElementById("root")).render(
  // StrictMode is a development-only tool  that double-renders components 
  // to help catch accidental side effects, memory leaks and outdated API usage
  <React.StrictMode>
    <App />
  </React.StrictMode>
);