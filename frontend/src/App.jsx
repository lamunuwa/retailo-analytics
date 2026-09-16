import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft, ArrowRight, BarChart3, Camera, Check, ChevronDown, CircleOff,
  CheckCircle2, Eye, EyeOff, FileVideo, LayoutDashboard, LockKeyhole, LogOut,
  Mail, MapPin, Menu, MousePointer2, Pencil, Plus, RefreshCw, Settings,
  ShieldCheck, Store, Trash2, TrendingUp, Video, X, XCircle,
} from "lucide-react";
import retailoCameraLogo from "../../docs/images/retailocameralogo.svg";
import retailoLogo from "../../docs/images/retailologo.svg";
import {
  changeAccountPassword,
  clearStoredSession,
  getCurrentUser,
  hasStoredSession,
  loginAccount,
  logoutAccount,
  registerAccount,
} from "./authApi";
import {
  createCamera,
  createStore,
  createZone,
  deleteCamera,
  deleteZone,
  generateRecommendations,
  getAnalyticsSummary,
  getCameras,
  getInsights,
  getRecommendations,
  getSessionResult,
  getSessions,
  getTraffic,
  getZones,
  resolveDemoContext,
  saveDemoContext,
  updateCamera,
  updateRecommendationStatus,
  updateZone,
} from "./dataApi";

const dashboardRanges = {
  Hoy: 1,
  "7 días": 7,
  "30 días": 30,
};

function analyticsPeriod(range) {
  const end = new Date();
  const start = new Date(end);
  start.setHours(0, 0, 0, 0);
  start.setDate(start.getDate() - (dashboardRanges[range] - 1));
  return { start: start.toISOString(), end: end.toISOString() };
}

function formatMoney(value = 0) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 0,
  }).format(value);
}

function conversionRate(units = 0, visits = 0) {
  return visits > 0 ? Math.min(100, (units * 100) / visits) : 0;
}

function Brand() {
  return (
    <div className="brand">
      <img className="brand-logo" src={retailoLogo} alt="RetaiLO" />
    </div>
  );
}

function userInitials(name = "Usuario") {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function UserMenu({ user, onChangePassword, onLogout }) {
  const [open, setOpen] = useState(false);
  const initials = userInitials(user?.name);
  return (
    <div className="user-menu">
      <button className="user-menu__trigger" type="button" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span><small>CUENTA</small><strong>{user?.name ?? "Usuario"}</strong></span><i>{initials}</i><ChevronDown size={14} />
      </button>
      {open && (
        <div className="user-menu__popover">
          <div><i>{initials}</i><span><strong>{user?.name ?? "Usuario"}</strong><small>{user?.email}</small></span></div>
          <button type="button" onClick={() => { setOpen(false); onChangePassword(); }}><LockKeyhole size={15} /> Cambiar contraseña</button>
          <button type="button" onClick={onLogout}><LogOut size={15} /> Cerrar sesión</button>
        </div>
      )}
    </div>
  );
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await onAuthenticated(mode, form);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  const changeMode = () => {
    setMode(mode === "register" ? "login" : "register");
    setError("");
  };

  return (
    <main className="auth-screen">
      <header className="auth-topbar">
        <Brand />
        <div className="auth-switch">
          <span>{mode === "register" ? "¿Ya tienes una cuenta?" : "¿Primera vez aquí?"}</span>
          <button type="button" onClick={changeMode}>
            {mode === "register" ? "Iniciar sesión" : "Crear cuenta"}
          </button>
        </div>
      </header>

      <section className="auth-story">
        <span className="overline overline--yellow">ANALÍTICA VISUAL PARA RETAIL</span>
        <h1>Lo que pasa en tu tienda,<br /><em>ahora tiene sentido.</em></h1>
        <p>Procesamos video local para ayudarte a comparar actividad, zonas y ventas sin identificar a ninguna persona.</p>

        <div className="auth-process" aria-label="Flujo de procesamiento de RetaiLO">
          <div><span>01</span><strong>Procesamiento</strong><small>Video local</small></div><i />
          <div><span>02</span><strong>Detección</strong><small>Personas por zona</small></div><i />
          <div><span>03</span><strong>Comparación</strong><small>Actividad y compras</small></div><i />
          <div><span>04</span><strong>Recomendaciones</strong><small>Acciones claras</small></div>
        </div>
      </section>

      <form className="auth-card" onSubmit={submit}>
        <div className="auth-card__heading">
          <span className="overline">{mode === "register" ? "NUEVA CUENTA" : "BIENVENIDO DE NUEVO"}</span>
          <h2>{mode === "register" ? "Crea tu espacio" : "Entra a tu panel"}</h2>
          <p>{mode === "register" ? "Primero tus datos. Después configuramos la tienda." : "Accede con la cuenta asociada a tu tienda."}</p>
        </div>

        {mode === "register" && (
          <label className="auth-field"><span>NOMBRE</span><input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Tu nombre" autoComplete="name" /></label>
        )}
        <label className="auth-field">
          <span>CORREO</span><div><Mail size={17} /><input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} placeholder="tu@negocio.mx" autoComplete="email" /></div>
        </label>
        <label className="auth-field">
          <span>CONTRASEÑA</span>
          <div><LockKeyhole size={17} /><input required minLength={mode === "register" ? 6 : 1} type={showPassword ? "text" : "password"} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete={mode === "register" ? "new-password" : "current-password"} /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
        </label>

        {error && <div className="auth-error" role="alert">{error}</div>}
        <label className="auth-consent"><input type="checkbox" defaultChecked /><span><Check size={12} /></span>Mantener sesión iniciada</label>
        <button className="auth-submit" type="submit" disabled={submitting}>{submitting ? <i className="spinner" /> : <>{mode === "register" ? "Crear cuenta y continuar" : "Entrar"}<ArrowRight size={17} /></>}</button>
        <div className="auth-security"><ShieldCheck size={18} /><p><strong>Privacidad por diseño.</strong> RetaiLO analiza patrones agregados; nunca usa reconocimiento facial.</p></div>
      </form>
    </main>
  );
}

function PasswordModal({ onClose, onSubmit }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    if (newPassword !== confirmation) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await onSubmit({ current_password: currentPassword, new_password: newPassword });
      setSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmation("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <form className="password-modal" onSubmit={submit} role="dialog" aria-modal="true" aria-labelledby="password-title">
        <header><div><span className="overline">SEGURIDAD DE LA CUENTA</span><h2 id="password-title">Cambiar contraseña</h2></div><button type="button" onClick={onClose} aria-label="Cerrar"><X size={18} /></button></header>
        <p>Usa al menos 6 caracteres. No solicitamos confirmación por correo.</p>
        <label className="auth-field"><span>CONTRASEÑA ACTUAL</span><input required type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} autoComplete="current-password" /></label>
        <label className="auth-field"><span>NUEVA CONTRASEÑA</span><input required minLength={6} type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} autoComplete="new-password" /></label>
        <label className="auth-field"><span>CONFIRMAR CONTRASEÑA</span><input required minLength={6} type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" /></label>
        {error && <div className="auth-error" role="alert">{error}</div>}
        {success && <div className="auth-success" role="status">Contraseña actualizada correctamente.</div>}
        <footer><button type="button" className="setup-back" onClick={onClose}>Cancelar</button><button type="submit" className="setup-primary" disabled={submitting}>{submitting ? "Guardando..." : "Guardar contraseña"}</button></footer>
      </form>
    </div>
  );
}

const onboardingCopy = {
  1: { overline: "01 / TU NEGOCIO", title: <>Dale un lugar<br />a los datos.</>, body: "Crea la tienda que concentrará cámaras, zonas y resultados. Con el nombre basta para esta demostración." },
  2: { overline: "02 / FUENTE DE VIDEO", title: <>Conecta la vista<br />de tu tienda.</>, body: "Por ahora trabajaremos con el video local incluido. La fuente podrá cambiar a webcam o RTSP cuando exista hardware." },
  3: { overline: "03 / ÁREAS DE INTERÉS", title: <>Cuatro puntos.<br />Una zona clara.</>, body: "Traza el polígono directamente sobre la cámara y asígnalo a un área. Este paso es opcional y podrás configurarlo después." },
};

function SetupSteps({ current }) {
  const labels = ["Tienda", "Cámara", "Zonas"];
  return (
    <div className="setup-steps">
      {labels.map((label, index) => {
        const number = index + 1;
        return <div className={`setup-step ${number === current ? "is-active" : ""} ${number < current ? "is-complete" : ""}`} key={label}><span>{number < current ? <Check size={13} /> : number}</span><b>{label}</b>{index < labels.length - 1 && <i />}</div>;
      })}
    </div>
  );
}

function DemoMap() {
  return (
    <div className="demo-map" aria-label="Mapa de demostración deshabilitado">
      <div className="demo-map__roads" />
      <div className="demo-map__blocks">{[1, 2, 3, 4, 5, 6, 7].map((item) => <i key={item} />)}</div>
      <span className="demo-pin"><MapPin size={20} /></span>
      <div className="demo-map__lock"><CircleOff size={18} /><strong>Mapa de demostración</strong><span>La selección de ubicación no está disponible.</span></div>
    </div>
  );
}

function StoreSetup({ onContinue }) {
  const [name, setName] = useState("Sucursal Centro");
  const [address, setAddress] = useState("Av. Universidad 1200, Monterrey");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await onContinue({ name });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <form className="setup-card" onSubmit={submit}>
      <header><span>01 / NUEVA TIENDA</span><h2>Registra tu primera sucursal</h2><Store size={25} /></header>
      <div className="setup-card__body">
        <label className="setup-field"><span>NOMBRE DE LA TIENDA</span><input required value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Sucursal Centro" /></label>
        <label className="setup-field"><span>DIRECCIÓN · DEMO</span><div><MapPin size={17} /><input required value={address} onChange={(event) => setAddress(event.target.value)} /></div></label>
        <DemoMap />
        <div className="setup-note"><Check size={15} /><span>El nombre se guardará en la API. La dirección y el mapa permanecen como demostración visual.</span></div>
        {error && <div className="auth-error" role="alert">{error}</div>}
      </div>
      <footer><button className="setup-primary" type="submit" disabled={submitting}>{submitting ? "Registrando..." : <>Registrar tienda <ArrowRight size={16} /></>}</button></footer>
    </form>
  );
}

function CameraSetup({ onBack, onContinue }) {
  const [name, setName] = useState("Cámara principal");
  const [description, setDescription] = useState("Vista general del piso de venta");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await onContinue({ name, description, source_type: "demo_video" });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <form className="setup-card" onSubmit={submit}>
      <header><span>02 / PRIMERA CÁMARA</span><h2>Configura una fuente</h2><Camera size={25} /></header>
      <div className="setup-card__body">
        <label className="setup-field"><span>NOMBRE</span><input required value={name} onChange={(event) => setName(event.target.value)} /></label>
        <label className="setup-field"><span>TIPO DE FUENTE</span><div className="setup-select"><Video size={17} /><select disabled defaultValue="demo_video"><option value="demo_video">Video demo local</option></select><ChevronDown size={16} /></div></label>
        <div className="demo-source"><FileVideo size={28} /><div><strong>demo-supermarket.mp4</strong><span>Fuente incluida · Control bloqueado</span></div><span className="demo-badge">DEMO</span></div>
        <label className="setup-field"><span>DESCRIPCIÓN</span><textarea value={description} onChange={(event) => setDescription(event.target.value)} /></label>
        <div className="setup-warning"><CircleOff size={16} /><span>No hay una cámara física conectada. Webcam y RTSP quedan fuera del alcance de esta demo.</span></div>
        {error && <div className="auth-error" role="alert">{error}</div>}
      </div>
      <footer><button className="setup-back" type="button" onClick={onBack}><ArrowLeft size={15} /> Atrás</button><button className="setup-primary" type="submit" disabled={submitting}>{submitting ? "Registrando..." : <>Registrar cámara <ArrowRight size={16} /></>}</button></footer>
    </form>
  );
}

function ZonesSetup({ onBack, onSkip, onFinish }) {
  const [points, setPoints] = useState([{ x: 105, y: 78 }, { x: 510, y: 72 }, { x: 540, y: 295 }, { x: 90, y: 305 }]);
  const [activePoint, setActivePoint] = useState(0);
  const [selectedZone, setSelectedZone] = useState("Bebidas");
  const [newZoneName, setNewZoneName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const zoneTypes = [
    ["Bebidas", "product_area"], ["Snacks", "product_area"],
    ["Refrigeradores", "fridges"], ["Caja", "checkout"], ["Nueva zona", "other"],
  ];

  const updatePoint = (index, axis, rawValue) => {
    const limit = axis === "x" ? 640 : 360;
    const value = Math.min(limit, Math.max(0, Number(rawValue) || 0));
    setPoints((current) => current.map((point, pointIndex) => pointIndex === index ? { ...point, [axis]: value } : point));
  };

  const placePoint = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = Math.round(((event.clientX - rect.left) / rect.width) * 640);
    const y = Math.round(((event.clientY - rect.top) / rect.height) * 360);
    setPoints((current) => current.map((point, index) => index === activePoint ? { x, y } : point));
  };

  const finish = async () => {
    const selectedType = zoneTypes.find(([name]) => name === selectedZone)?.[1] ?? "other";
    const name = selectedZone === "Nueva zona" ? newZoneName.trim() : selectedZone;
    if (!name) {
      setError("Escribe el nombre de la nueva zona.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await onFinish({ name, zone_type: selectedType, points });
    } catch (requestError) {
      setError(requestError.message);
      setSubmitting(false);
    }
  };

  return (
    <div className="setup-card">
      <header><span>03 / ZONAS OPCIONALES</span><h2>Dibuja una zona en la cámara</h2><MousePointer2 size={25} /></header>
      <div className="setup-card__body">
        <p className="setup-intro">Selecciona un vértice y haz clic sobre la imagen para colocarlo. Las coordenadas coinciden con el video demo: 640 × 360 px.</p>
        <div className="polygon-editor">
          <div className="polygon-camera" onClick={placePoint} role="button" tabIndex="0" aria-label="Vista demo para colocar los puntos del polígono">
            <img src={retailoCameraLogo} alt="" />
            <span className="polygon-camera__demo"><i /> CÁMARA DEMO · 640 × 360</span>
            <svg viewBox="0 0 640 360" preserveAspectRatio="none" aria-hidden="true">
              <polygon points={points.map((point) => `${point.x},${point.y}`).join(" ")} />
              {points.map((point, index) => <g key={index} className={index === activePoint ? "is-active" : ""}><circle cx={point.x} cy={point.y} r="12" /><text x={point.x} y={point.y + 4}>{index + 1}</text></g>)}
            </svg>
            <span className="polygon-camera__hint"><MousePointer2 size={13} /> Clic para mover el punto {activePoint + 1}</span>
          </div>
          <div className="point-grid">
            {points.map((point, index) => (
              <div className={index === activePoint ? "is-active" : ""} key={index}>
                <button type="button" onClick={() => setActivePoint(index)}>PUNTO {index + 1}</button>
                <label>X <input type="number" min="0" max="640" value={point.x} onChange={(event) => updatePoint(index, "x", event.target.value)} /></label>
                <label>Y <input type="number" min="0" max="360" value={point.y} onChange={(event) => updatePoint(index, "y", event.target.value)} /></label>
              </div>
            ))}
          </div>
        </div>
        <div className="zone-assignment">
          <div><span className="overline">ASIGNAR POLÍGONO A</span><small>Tipo enviado a la API</small></div>
          <div className="zone-type-options">
            {zoneTypes.map(([name, type]) => <button className={selectedZone === name ? "is-selected" : ""} type="button" onClick={() => setSelectedZone(name)} key={name}><span>{selectedZone === name && <Check size={12} />}</span><strong>{name}</strong><small>{type}</small></button>)}
          </div>
          {selectedZone === "Nueva zona" && <label className="new-zone-field"><span>NOMBRE DE LA NUEVA ZONA</span><input autoFocus value={newZoneName} onChange={(event) => setNewZoneName(event.target.value)} placeholder="Ej. Panadería" /></label>}
        </div>
        <div className="setup-note"><Check size={15} /><span>Polígono válido: 4 puntos distintos listos para enviarse a la API.</span></div>
        {error && <div className="auth-error" role="alert">{error}</div>}
      </div>
      <footer><button className="setup-back" type="button" onClick={onBack}><ArrowLeft size={15} /> Atrás</button><button className="setup-skip" type="button" onClick={onSkip} disabled={submitting}>Omitir por ahora</button><button className="setup-primary" type="button" onClick={finish} disabled={submitting}>{submitting ? "Guardando..." : <>Terminar <ArrowRight size={16} /></>}</button></footer>
    </div>
  );
}

function Onboarding({ user, onChangePassword, onComplete, onLogout }) {
  const [step, setStep] = useState(1);
  const [store, setStore] = useState(null);
  const [camera, setCamera] = useState(null);
  const copy = onboardingCopy[step];
  const registerStore = async (payload) => {
    const createdStore = await createStore(payload);
    setStore(createdStore);
    saveDemoContext(createdStore, null);
    setStep(2);
  };
  const registerCamera = async (payload) => {
    const createdCamera = await createCamera(store.id, payload);
    setCamera(createdCamera);
    saveDemoContext(store, createdCamera);
    setStep(3);
  };
  const registerZone = async (payload) => {
    await createZone(camera.id, payload);
    onComplete({ store, camera });
  };
  return (
    <main className="onboarding-screen">
      <header className="onboarding-topbar"><Brand /><SetupSteps current={step} /><UserMenu user={user} onChangePassword={onChangePassword} onLogout={onLogout} /></header>
      <section className="onboarding-content">
        <div className="onboarding-story">
          <span className="overline overline--blue">{copy.overline}</span><h1>{copy.title}</h1><p>{copy.body}</p>
        </div>
        {step === 1 && <StoreSetup onContinue={registerStore} />}
        {step === 2 && <CameraSetup onBack={() => setStep(1)} onContinue={registerCamera} />}
        {step === 3 && <ZonesSetup onBack={() => setStep(2)} onSkip={() => onComplete({ store, camera })} onFinish={registerZone} />}
      </section>
    </main>
  );
}

function MetricBox({ number, label, detail, featured = false }) {
  const numericValue = Number.parseFloat(String(number).replace(/[^\d.-]/g, ""));
  const prefix = String(number).trim().startsWith("$") ? "$" : "";
  const suffix = String(number).trim().endsWith("%") ? "%" : "";
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (!Number.isFinite(numericValue)) return undefined;
    let frame;
    const startedAt = performance.now();
    const duration = 1100;
    const animate = (now) => {
      const progress = Math.min((now - startedAt) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(numericValue * eased);
      if (progress < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [numericValue]);

  const formattedValue = suffix === "%"
    ? displayValue.toFixed(1)
    : prefix
      ? displayValue.toLocaleString("en-US", { maximumFractionDigits: 2 })
      : Math.round(displayValue).toLocaleString("en-US");
  return <article className={`metric-box ${featured ? "metric-box--featured" : ""}`}><span>{label}</span><strong>{prefix}{formattedValue}{suffix}</strong><small>{detail}</small></article>;
}

function ZoneComparison({ metrics }) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect();
      }
    }, { threshold: 0.2 });
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, [metrics.length]);

  if (!metrics.length) {
    return <div className="dashboard-empty">Aún no hay métricas por zona. Ejecuta el video y registra ventas para compararlas.</div>;
  }
  return (
    <div className={`editorial-chart ${isVisible ? "is-visible" : ""}`} ref={sectionRef}>
      <div className="editorial-chart__legend"><span><i /> Actividad detectada</span><span><i /> Ventas</span><em>Conversión estimada</em></div>
      {metrics.map((zone, index) => (
        <div className="editorial-row" key={zone.zone_id}>
          <span className="editorial-row__index">{String(index + 1).padStart(2, "0")}</span><div className="editorial-row__name"><strong>{zone.zone_name}</strong><small>{zone.zone_type.replaceAll("_", " ")}</small></div>
          <div className="editorial-row__bars"><span style={{ width: `${zone.traffic_share}%` }}><i>{zone.traffic_share}</i></span><span style={{ width: `${zone.sales_share}%` }}><i>{zone.sales_share}</i></span></div><strong className="editorial-row__conversion">{conversionRate(zone.units_sold, zone.visits).toFixed(1)}%</strong>
        </div>
      ))}
    </div>
  );
}

const recommendationLabels = {
  pending: "PENDIENTE",
  accepted: "ACEPTADA",
  rejected: "RECHAZADA",
};

function RecommendationHistory({ recommendations, pendingId, onStatusChange }) {
  return (
    <section className="recommendation-section" id="historial">
      <header><div><span className="overline overline--blue">04 / DECISIONES</span><h2>Historial de recomendaciones</h2></div><p>Cada hallazgo conserva la decisión tomada. Las recomendaciones pendientes pueden aceptarse o rechazarse desde aquí.</p></header>
      <div className="recommendation-list">
        {!recommendations.length && <div className="dashboard-empty">Todavía no hay recomendaciones. Procesa el video y registra ventas para generar la primera.</div>}
        {recommendations.map((item) => {
          const date = new Date(item.created_at);
          const evidence = item.message.replace("de las visitas", "de la actividad detectada");
          return (
            <article className={`recommendation-item recommendation-item--${item.status}`} key={item.id}>
              <div className="recommendation-item__meta"><span>#{item.id} · {item.zone_name}</span><time>{date.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" })}</time></div>
              <p>{evidence}</p>
              <div className="recommendation-item__footer">
                <em>{recommendationLabels[item.status]}</em>
                {item.status === "pending" && <div><button type="button" onClick={() => onStatusChange(item.id, "accepted")} disabled={pendingId === item.id}><CheckCircle2 size={14} /> Aceptar</button><button type="button" onClick={() => onStatusChange(item.id, "rejected")} disabled={pendingId === item.id}><XCircle size={14} /> Rechazar</button></div>}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function CameraManagementPanel({ storeId, cameras, onChanged }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  const resetForm = () => {
    setName("");
    setDescription("");
    setEditingId(null);
    setError("");
  };

  const edit = (camera) => {
    setEditingId(camera.id);
    setName(camera.name);
    setDescription(camera.description ?? "");
    setError("");
  };

  const submit = async (event) => {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      const payload = { name, description: editingId ? description : description || null };
      if (editingId) await updateCamera(editingId, payload);
      else await createCamera(storeId, { ...payload, source_type: "demo_video" });
      resetForm();
      await onChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setPending(false);
    }
  };

  const remove = async (camera) => {
    if (!window.confirm(`¿Desactivar la cámara "${camera.name}"?`)) return;
    setPending(true);
    setError("");
    try {
      await deleteCamera(camera.id);
      await onChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setPending(false);
    }
  };

  return (
    <article className="management-panel">
      <header><div><span className="overline overline--blue">04 / CÁMARAS</span><h2>Gestionar cámaras</h2></div><Camera size={23} /></header>
      <form className="management-form" onSubmit={submit}>
        <label><span>NOMBRE</span><input required maxLength={100} value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Cámara de caja" /></label>
        <label><span>DESCRIPCIÓN</span><input maxLength={255} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Ubicación o vista" /></label>
        <div className="management-locked"><Video size={15} /><span>Fuente fija: video demo local</span></div>
        {error && <div className="auth-error" role="alert">{error}</div>}
        <div className="management-form__actions"><button className="management-add" type="submit" disabled={pending}>{editingId ? <Pencil size={15} /> : <Plus size={15} />} {pending ? "Guardando..." : editingId ? "Guardar cambios" : "Agregar cámara"}</button>{editingId && <button className="management-cancel" type="button" onClick={resetForm} disabled={pending}>Cancelar</button>}</div>
      </form>
      <div className="management-list">
        {!cameras.length && <div className="management-list__empty">No hay cámaras activas.</div>}
        {cameras.map((camera) => <div className={`management-item ${editingId === camera.id ? "is-editing" : ""}`} key={camera.id}><span className="management-item__icon"><Camera size={17} /></span><div><strong>{camera.name}</strong><small>ID {camera.id} · {camera.description || "Sin descripción"}</small></div><em><i /> ACTIVA</em><div className="management-item__actions"><button type="button" onClick={() => edit(camera)} disabled={pending} aria-label={`Editar ${camera.name}`}><Pencil size={15} /></button><button className="is-danger" type="button" onClick={() => remove(camera)} disabled={pending} aria-label={`Eliminar ${camera.name}`}><Trash2 size={15} /></button></div></div>)}
      </div>
    </article>
  );
}

function ZoneManagementPanel({ cameras, zones, onChanged }) {
  const [cameraId, setCameraId] = useState(cameras[0]?.id ?? "");
  const [name, setName] = useState("");
  const [zoneType, setZoneType] = useState("product_area");
  const [points, setPoints] = useState([
    { x: 20, y: 20 }, { x: 620, y: 20 }, { x: 620, y: 340 }, { x: 20, y: 340 },
  ]);
  const [editingId, setEditingId] = useState(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!cameras.some((camera) => camera.id === Number(cameraId))) {
      setCameraId(cameras[0]?.id ?? "");
    }
  }, [cameras, cameraId]);

  const updatePoint = (index, axis, rawValue) => {
    const maximum = axis === "x" ? 640 : 360;
    const value = Math.min(maximum, Math.max(0, Number(rawValue) || 0));
    setPoints((current) => current.map((point, pointIndex) => pointIndex === index ? { ...point, [axis]: value } : point));
  };

  const resetForm = () => {
    setEditingId(null);
    setName("");
    setZoneType("product_area");
    setPoints([{ x: 20, y: 20 }, { x: 620, y: 20 }, { x: 620, y: 340 }, { x: 20, y: 340 }]);
    setCameraId(cameras[0]?.id ?? "");
    setError("");
  };

  const edit = (zone) => {
    setEditingId(zone.id);
    setCameraId(zone.camera_id);
    setName(zone.name);
    setZoneType(zone.zone_type);
    setPoints(zone.points.map((point) => ({ ...point })));
    setError("");
  };

  const submit = async (event) => {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      const payload = { name, zone_type: zoneType, points };
      if (editingId) await updateZone(editingId, payload);
      else await createZone(Number(cameraId), payload);
      resetForm();
      await onChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setPending(false);
    }
  };

  const remove = async (zone) => {
    if (!window.confirm(`¿Desactivar la zona "${zone.name}"?`)) return;
    setPending(true);
    setError("");
    try {
      await deleteZone(zone.id);
      if (editingId === zone.id) resetForm();
      await onChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setPending(false);
    }
  };

  return (
    <article className="management-panel">
      <header><div><span className="overline overline--blue">05 / ZONAS</span><h2>Gestionar zonas</h2></div><MousePointer2 size={23} /></header>
      <form className="management-form" onSubmit={submit}>
        <div className="management-form__row">
          <label><span>CÁMARA</span><select required value={cameraId} onChange={(event) => setCameraId(event.target.value)} disabled={!cameras.length || Boolean(editingId)}>{cameras.map((camera) => <option value={camera.id} key={camera.id}>{camera.name} · ID {camera.id}</option>)}</select></label>
          <label><span>TIPO</span><select value={zoneType} onChange={(event) => setZoneType(event.target.value)}><option value="product_area">Área de producto</option><option value="checkout">Caja</option><option value="entrance_exit">Entrada / salida</option><option value="fridges">Refrigeradores</option><option value="other">Otra</option></select></label>
        </div>
        <label><span>NOMBRE</span><input required maxLength={100} value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Bebidas" /></label>
        <div className="management-points"><span>POLÍGONO · VIDEO 640 × 360</span><div>{points.map((point, index) => <fieldset key={index}><legend>P{index + 1}</legend><label>X<input type="number" min="0" max="640" value={point.x} onChange={(event) => updatePoint(index, "x", event.target.value)} /></label><label>Y<input type="number" min="0" max="360" value={point.y} onChange={(event) => updatePoint(index, "y", event.target.value)} /></label></fieldset>)}</div></div>
        {error && <div className="auth-error" role="alert">{error}</div>}
        <div className="management-form__actions"><button className="management-add" type="submit" disabled={pending || !cameras.length}>{editingId ? <Pencil size={15} /> : <Plus size={15} />} {pending ? "Guardando..." : editingId ? "Guardar cambios" : "Agregar zona"}</button>{editingId && <button className="management-cancel" type="button" onClick={resetForm} disabled={pending}>Cancelar</button>}</div>
      </form>
      <div className="management-list">
        {!zones.length && <div className="management-list__empty">No hay zonas activas.</div>}
        {zones.map((zone) => <div className={`management-item ${editingId === zone.id ? "is-editing" : ""}`} key={zone.id}><span className="management-item__icon"><MapPin size={17} /></span><div><strong>{zone.name}</strong><small>ID {zone.id} · {zone.camera_name} · {zone.zone_type.replaceAll("_", " ")}</small></div><div className="management-item__actions"><button type="button" onClick={() => edit(zone)} disabled={pending} aria-label={`Editar ${zone.name}`}><Pencil size={15} /></button><button className="is-danger" type="button" onClick={() => remove(zone)} disabled={pending} aria-label={`Eliminar ${zone.name}`}><Trash2 size={15} /></button></div></div>)}
      </div>
    </article>
  );
}

function Dashboard({ user, store, onChangePassword, onLogout }) {
  const [range, setRange] = useState("Hoy");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [activeSection, setActiveSection] = useState("resumen");
  const navRef = useRef(null);
  const indicatorRef = useRef(null);
  const [dashboard, setDashboard] = useState({
    summary: null,
    traffic: [],
    insights: [],
    recommendations: [],
    cameras: [],
    zones: [],
    sessions: [],
  });
  const [loading, setLoading] = useState(false);
  const [recommendationPending, setRecommendationPending] = useState(null);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState(null);

  const refresh = async () => {
    if (!store?.id) return;
    setLoading(true);
    setError("");
    const period = analyticsPeriod(range);
    try {
      const [summary, traffic, insights, cameras] = await Promise.all([
        getAnalyticsSummary(store.id, period),
        getTraffic(store.id, period),
        getInsights(store.id, period),
        getCameras(store.id),
      ]);
      const [sessionGroups, zoneGroups] = await Promise.all([
        Promise.all(cameras.map((item) => getSessions(item.id))),
        Promise.all(cameras.map((item) => getZones(item.id))),
      ]);
      const sessions = sessionGroups.flat().sort((left, right) => new Date(right.started_at) - new Date(left.started_at));
      const zones = zoneGroups.flatMap((cameraZones, index) => cameraZones.map((zone) => ({ ...zone, camera_name: cameras[index].name })));
      const results = await Promise.all(sessions.map((item) => getSessionResult(item.id)));
      const sessionHistory = sessions.map((item, index) => ({ ...item, result: results[index] }));
      if (summary.total_sessions > 0) {
        await generateRecommendations(store.id, period);
      }
      const recommendations = await getRecommendations(store.id);
      setDashboard({ summary, traffic, insights, recommendations, cameras, zones, sessions: sessionHistory });
      setUpdatedAt(new Date());
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, [store?.id, range]);

  if (!store) {
    return (
      <main className="report-screen">
        <header className="report-topbar"><Brand /><span /><UserMenu user={user} onChangePassword={onChangePassword} onLogout={onLogout} /></header>
        <div className="dashboard-no-store"><Store size={35} /><h1>No hay una tienda configurada</h1><p>Crea una cuenta nueva para completar el flujo inicial de la demostración.</p></div>
      </main>
    );
  }

  const summary = dashboard.summary ?? {
    total_sessions: 0,
    total_visits: 0,
    total_units_sold: 0,
    total_revenue: 0,
  };
  const conversion = conversionRate(summary.total_units_sold, summary.total_visits);
  const pendingRecommendations = dashboard.recommendations.filter((item) => item.status === "pending");
  const recommendation = pendingRecommendations.find((item) => item.insight_type === "HIGH_TRAFFIC_LOW_SALES")
    ?? pendingRecommendations[0]
    ?? dashboard.recommendations[0];
  const insight = dashboard.insights[0];

  const changeRecommendationStatus = async (recommendationId, status) => {
    setRecommendationPending(recommendationId);
    setError("");
    try {
      await updateRecommendationStatus(recommendationId, status);
      await refresh();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setRecommendationPending(null);
    }
  };

  useEffect(() => {
    const updateIndicator = () => {
      const activeLink = navRef.current?.querySelector(`[data-section="${activeSection}"]`);
      if (!activeLink || !indicatorRef.current) return;
      indicatorRef.current.style.width = `${activeLink.offsetWidth}px`;
      indicatorRef.current.style.transform = `translateX(${activeLink.offsetLeft}px)`;
    };
    updateIndicator();
    window.addEventListener("resize", updateIndicator);
    return () => window.removeEventListener("resize", updateIndicator);
  }, [activeSection]);
  const heroTitle = recommendation?.message?.replace("de las visitas", "de la actividad detectada")
    ?? insight?.message?.replace("de las visitas", "de la actividad detectada")
    ?? "Tu próxima corrida aparecerá aquí.";
  return (
    <main className="report-screen">
      <header className="report-topbar">
        <Brand />
        <nav ref={navRef} className={mobileMenu ? "is-open" : ""}><span ref={indicatorRef} className="report-nav-indicator" aria-hidden="true" /><a className={activeSection === "resumen" ? "is-active" : ""} data-section="resumen" href="#resumen" onClick={() => setActiveSection("resumen")}><LayoutDashboard size={15} /> Resumen</a><a className={activeSection === "zonas" ? "is-active" : ""} data-section="zonas" href="#zonas" onClick={() => setActiveSection("zonas")}><BarChart3 size={15} /> Zonas</a><a className={activeSection === "historial" ? "is-active" : ""} data-section="historial" href="#historial" onClick={() => setActiveSection("historial")}><FileVideo size={15} /> Historial</a><a className={activeSection === "configuracion" ? "is-active" : ""} data-section="configuracion" href="#configuracion" onClick={() => setActiveSection("configuracion")}><Settings size={15} /> Configurar</a></nav>
        <UserMenu user={user} onChangePassword={onChangePassword} onLogout={onLogout} />
        <button className="report-menu" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Abrir menú">{mobileMenu ? <X /> : <Menu />}</button>
      </header>

      <div className="report-body" id="resumen">
        <section className="report-hero">
          <div className="report-hero__meta"><span>{store.name.toUpperCase()} · TIENDA #{store.id} · REPORTE DEL DÍA</span><span>{updatedAt ? `ACTUALIZADO ${updatedAt.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" })}` : "SIN ACTUALIZAR"}</span></div>
          <div className="report-hero__content"><div className="report-symbol"><TrendingUp size={31} /></div><div><span className="overline">HALLAZGO PRINCIPAL</span><h1>{heroTitle}</h1>{recommendation && <div className="report-hero__actions"><span className={`recommendation-status recommendation-status--${recommendation.status}`}>{recommendationLabels[recommendation.status]}</span>{recommendation.status === "pending" && <><button type="button" onClick={() => changeRecommendationStatus(recommendation.id, "accepted")} disabled={recommendationPending === recommendation.id}><CheckCircle2 size={15} /> Aceptar</button><button type="button" onClick={() => changeRecommendationStatus(recommendation.id, "rejected")} disabled={recommendationPending === recommendation.id}><XCircle size={15} /> Rechazar</button></>}</div>}</div><div className="report-score"><strong>{conversion.toFixed(1)}%</strong><span>CONVERSIÓN<br />ESTIMADA</span></div></div>
        </section>

        <section className="report-controls"><span>PERIODO ANALIZADO</span><div>{Object.keys(dashboardRanges).map((item) => <button className={range === item ? "is-active" : ""} onClick={() => setRange(item)} key={item}>{item}</button>)}</div><button className={`report-refresh ${loading ? "is-loading" : ""}`} type="button" onClick={refresh} disabled={loading}><RefreshCw size={14} /> {loading ? "ACTUALIZANDO" : "RECARGAR DATOS"}</button><span className="report-demo"><i /> DATOS DE DEMOSTRACIÓN</span></section>
        {error && <div className="dashboard-error" role="alert">{error} <button type="button" onClick={refresh}>Reintentar</button></div>}

        <section className="metric-strip"><MetricBox number={`${conversion.toFixed(1)}%`} label="CONVERSIÓN ESTIMADA" detail="Unidades / actividad registrada" featured /><MetricBox number={formatMoney(summary.total_revenue)} label="VENTAS REGISTRADAS" detail={`${summary.total_units_sold} unidades demo`} /><MetricBox number={summary.total_sessions} label="SESIONES ANALIZADAS" detail="Procesamientos completos" /><MetricBox number={dashboard.traffic.length} label="ZONAS MONITOREADAS" detail="Cobertura configurada" /></section>

        <section className="analysis-section" id="zonas">
          <header><div><span className="overline overline--blue">01 / LECTURA POR ÁREA</span><h2>El pulso de tu tienda,<br />zona por zona.</h2></div><p>Comparamos señales relativas del video con ventas registradas. No inferimos identidades ni permanencia individual.</p></header>
          <ZoneComparison metrics={dashboard.traffic} />
        </section>

        <section className="report-columns">
          <article className="evidence-panel" id="procesamientos">
            <header><span className="overline overline--blue">02 / HISTORIAL</span><h2>Procesamientos recientes</h2><span>{dashboard.sessions.length} REGISTROS</span></header>
            {!dashboard.sessions.length && <div className="dashboard-empty">Todavía no se ha ejecutado el video demo para esta tienda.</div>}
            {dashboard.sessions.slice(0, 5).map((session, index) => {
              const date = new Date(session.started_at);
              return <div className={`finding-row ${index === 0 ? "finding-row--featured" : ""}`} key={session.id}><span>{date.toLocaleDateString("es-MX", { day: "2-digit", month: "short" }).toUpperCase()}<br />{date.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" })}</span><div><strong>Sesión #{session.id} · {session.status === "completed" ? "procesamiento completo" : session.status === "failed" ? "procesamiento fallido" : "procesando video"}</strong><p>{session.result ? `${session.result.processed_frames} cuadros procesados · ${session.result.elapsed_seconds.toFixed(1)} segundos` : "Esperando resultados agregados del agente local."}</p></div><em className={`history-status ${session.status === "running" ? "history-status--new" : ""}`}>{session.status.toUpperCase()}</em></div>;
            })}
          </article>

          <article className="demo-camera-panel" id="camaras">
            <header><div><span className="overline">03 / DISPOSITIVOS</span><h2>Cámaras activas</h2></div><span className="camera-count">{dashboard.cameras.length}</span></header>
            <div className="camera-list">
              {!dashboard.cameras.length && <div className="dashboard-empty">No hay cámaras activas.</div>}
              {dashboard.cameras.map((item) => <article key={item.id}><span className="camera-list__icon"><Camera size={20} /></span><div><strong>{item.name}</strong><small>ID {item.id} · {item.description || "Video demo local"} · {item.source_type}</small></div><em className="camera-state camera-state--active"><i /> ACTIVA</em></article>)}
            </div>
            <div className="camera-disabled"><CircleOff size={17} /><p><strong>Hardware no disponible</strong>El estado activo corresponde a la fuente demo. Los controles físicos permanecen deshabilitados.</p></div>
          </article>
        </section>

        <RecommendationHistory recommendations={dashboard.recommendations} pendingId={recommendationPending} onStatusChange={changeRecommendationStatus} />

        <section className="configuration-section" id="configuracion">
          <header><div><span className="overline overline--blue">CONFIGURACIÓN DE LA DEMO</span><h2>Tu tienda, lista para probar.</h2></div><p>Agrega o desactiva cámaras y zonas sin salir del dashboard. Los cambios se guardan directamente en la API.</p></header>
          <div className="configuration-grid"><CameraManagementPanel storeId={store.id} cameras={dashboard.cameras} onChanged={refresh} /><ZoneManagementPanel cameras={dashboard.cameras} zones={dashboard.zones} onChanged={refresh} /></div>
        </section>

        <footer className="report-footer"><Brand /><span>PRIVACIDAD POR DISEÑO · SIN RECONOCIMIENTO FACIAL</span><span>RETAILO ANALYTICS · 2026</span></footer>
      </div>
    </main>
  );
}

export default function App() {
  const [screen, setScreen] = useState("auth");
  const [user, setUser] = useState(null);
  const [store, setStore] = useState(null);
  const [camera, setCamera] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [changingPassword, setChangingPassword] = useState(false);
  const navigate = (next) => { window.history.replaceState(null, "", next === "auth" ? "#login" : `#${next}`); window.scrollTo({ top: 0, behavior: "smooth" }); setScreen(next); };

  useEffect(() => {
    if (!hasStoredSession()) {
      setCheckingSession(false);
      return;
    }
    getCurrentUser()
      .then(async (currentUser) => {
        setUser(currentUser);
        const context = await resolveDemoContext();
        setStore(context.store);
        setCamera(context.camera);
        navigate(context.store ? "dashboard" : "onboarding");
      })
      .catch(() => clearStoredSession())
      .finally(() => setCheckingSession(false));
  }, []);

  const authenticate = async (mode, payload) => {
    const currentUser = mode === "register"
      ? await registerAccount(payload)
      : await loginAccount({ email: payload.email, password: payload.password });
    setUser(currentUser);
    if (mode === "register") {
      navigate("onboarding");
      return;
    }
    const context = await resolveDemoContext();
    setStore(context.store);
    setCamera(context.camera);
    navigate(context.store ? "dashboard" : "onboarding");
  };

  const completeOnboarding = (context) => {
    setStore(context.store);
    setCamera(context.camera);
    saveDemoContext(context.store, context.camera);
    navigate("dashboard");
  };

  const logout = async () => {
    await logoutAccount().catch(() => clearStoredSession());
    setUser(null);
    setStore(null);
    setCamera(null);
    setChangingPassword(false);
    navigate("auth");
  };

  if (checkingSession) return <main className="session-loading"><Brand /><i className="spinner" /><span>Validando sesión...</span></main>;

  const passwordModal = changingPassword && <PasswordModal onClose={() => setChangingPassword(false)} onSubmit={changeAccountPassword} />;
  if (screen === "auth") return <AuthScreen onAuthenticated={authenticate} />;
  if (screen === "onboarding") return <><Onboarding user={user} onComplete={completeOnboarding} onChangePassword={() => setChangingPassword(true)} onLogout={logout} />{passwordModal}</>;
  return <><Dashboard user={user} store={store} camera={camera} onChangePassword={() => setChangingPassword(true)} onLogout={logout} />{passwordModal}</>;
}
