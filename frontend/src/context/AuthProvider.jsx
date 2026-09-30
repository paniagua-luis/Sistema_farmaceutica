import { useEffect, useState } from "react";
import { authApi } from "../api/client";
import { decodeJwt } from "../utils/jwt";
import { AuthContext } from "./auth-context";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [username, setUsername] = useState(() => localStorage.getItem("username"));
  const [rol, setRol] = useState(() => localStorage.getItem("rol"));
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  }, [token]);

  useEffect(() => {
    if (username) localStorage.setItem("username", username);
    else localStorage.removeItem("username");
  }, [username]);

  useEffect(() => {
    if (rol) localStorage.setItem("rol", rol);
    else localStorage.removeItem("rol");
  }, [rol]);

  async function login(usernameInput, password) {
    setError(null);
    setCargando(true);
    try {
      const data = await authApi.login(usernameInput, password);
      const payload = decodeJwt(data.access_token);
      setToken(data.access_token);
      setUsername(usernameInput);
      setRol(payload?.rol ?? null);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setCargando(false);
    }
  }

  async function registrar(usernameInput, password) {
    setError(null);
    setCargando(true);
    try {
      await authApi.registrar(usernameInput, password);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setCargando(false);
    }
  }

  function logout() {
    setToken(null);
    setUsername(null);
    setRol(null);
  }

  const value = { token, username, rol, error, cargando, login, registrar, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}