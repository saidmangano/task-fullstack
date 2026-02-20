import { useState } from "react";

const API_BASE = "/api";

export default function App() {
  const [mode, setMode] = useState("register"); // "register" | "login"
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: ""
  });
  const [status, setStatus] = useState({ type: "", text: "" });

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus({
      type: "loading",
      text: mode === "register" ? "Создаём аккаунт..." : "Входим..."
    });
    try {
      const endpoint = mode === "register" ? "register" : "login";
      const payload =
        mode === "register"
          ? form
          : { email: form.email, password: form.password };

      const res = await fetch(`${API_BASE}/${endpoint}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        let message = "Ошибка регистрации";
        if (mode === "login") message = "Ошибка входа";
        try {
          const data = await res.json();
          const firstKey = data && Object.keys(data)[0];
          if (firstKey) {
            const val = data[firstKey];
            message = Array.isArray(val) ? val[0] : String(val);
          }
        } catch {
          // ignore
        }
        setStatus({ type: "error", text: message });
        return;
      }

      const data = await res.json();
      if (mode === "login" && data?.token) {
        localStorage.setItem("token", data.token);
        setStatus({ type: "success", text: "Вход выполнен." });
      } else {
        setStatus({ type: "success", text: "Аккаунт создан." });
      }
      setForm((prev) => ({
        email: "",
        password: "",
        first_name: prev.first_name,
        last_name: prev.last_name
      }));
    } catch {
      setStatus({ type: "error", text: "Сервер недоступен." });
    }
  };

  return (
    <div className="page">
      <main className="card">
        <div className="tabs">
          <button
            type="button"
            className={mode === "register" ? "tab active" : "tab"}
            onClick={() => {
              setMode("register");
              setStatus({ type: "", text: "" });
            }}
          >
            Регистрация
          </button>
          <button
            type="button"
            className={mode === "login" ? "tab active" : "tab"}
            onClick={() => {
              setMode("login");
              setStatus({ type: "", text: "" });
            }}
          >
            Вход
          </button>
        </div>

        <h1>{mode === "register" ? "Регистрация" : "Вход"}</h1>

        <form className="form" onSubmit={onSubmit}>
          {mode === "register" ? (
            <>
              <label className="field">
                <span>Имя</span>
                <input name="first_name" value={form.first_name} onChange={onChange} />
              </label>

              <label className="field">
                <span>Фамилия</span>
                <input name="last_name" value={form.last_name} onChange={onChange} />
              </label>
            </>
          ) : null}

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span>Пароль</span>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={onChange}
              required
              minLength={8}
            />
          </label>

          <button className="btn" type="submit">
            {mode === "register" ? "Создать" : "Войти"}
          </button>

          {status.text ? (
            <div className={`notice ${status.type}`}>{status.text}</div>
          ) : null}
        </form>
      </main>
    </div>
  );
}
