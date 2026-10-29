import { Navigate, createBrowserRouter } from "react-router-dom";
import { LoginPage } from "../features/auth/LoginPage";
import { HomePage } from "../features/dashboard/HomePage";
import { RequireAuth } from "./RequireAuth";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/app/home", element: <RequireAuth><HomePage /></RequireAuth> },
  { path: "*", element: <Navigate to="/app/home" replace /> },
]);
