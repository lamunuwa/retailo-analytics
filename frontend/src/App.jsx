import { useState } from "react";
import {
  ArrowLeft, ArrowRight, BarChart3, Camera, Check, ChevronDown, CircleOff,
  Eye, EyeOff, FileVideo, LayoutDashboard, Lightbulb, LockKeyhole, LogOut,
  Mail, MapPin, Menu, MousePointer2, ShieldCheck,
  Sparkles, Store, TrendingUp, Video, X,
} from "lucide-react";
import retailoCameraLogo from "../../docs/images/retailocameralogo.svg";
import retailoLogo from "../../docs/images/retailologo.svg";

const dashboardRanges = {
  Hoy: { conversion: "31.8%", sales: "$18,420", sessions: "6" },
  "7 días": { conversion: "29.4%", sales: "$126,730", sessions: "38" },
  "30 días": { conversion: "30.1%", sales: "$538,900", sessions: "164" },
};

const zones = [
  { name: "Bebidas", activity: 92, sales: 45, conversion: "18%", color: "#ffd152" },
  { name: "Snacks", activity: 73, sales: 70, conversion: "34%", color: "#909cc2" },
  { name: "Refrigeradores", activity: 58, sales: 62, conversion: "36%", color: "#f0c848" },
  { name: "Caja", activity: 41, sales: 49, conversion: "29%", color: "#737fa9" },
];

function Brand() {
  return (
    <div className="brand">
      <img className="brand-logo" src={retailoLogo} alt="RetaiLO" />
    </div>
  );
}

function UserMenu({ onLogout }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="user-menu">
      <button className="user-menu__trigger" type="button" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span><small>CUENTA</small><strong>Andrea M.</strong></span><i>AM</i><ChevronDown size={14} />
      </button>
      {open && (
        <div className="user-menu__popover">
          <div><i>AM</i><span><strong>Andrea Martínez</strong><small>andrea@mitienda.mx</small></span></div>
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

  const submit = (event) => {
    event.preventDefault();
    setSubmitting(true);
    window.setTimeout(() => onAuthenticated(mode), 500);
  };

  return (
    <main className="auth-screen">
      <header className="auth-topbar">
        <Brand />
        <div className="auth-switch">
          <span>{mode === "register" ? "¿Ya tienes una cuenta?" : "¿Primera vez aquí?"}</span>
          <button type="button" onClick={() => setMode(mode === "register" ? "login" : "register")}>
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
          <p>{mode === "register" ? "Primero tus datos. Después configuramos la tienda." : "En esta demo volverás a completar la configuración inicial."}</p>
        </div>

        {mode === "register" && (
          <label className="auth-field"><span>NOMBRE</span><input required defaultValue="Andrea Martínez" placeholder="Tu nombre" /></label>
        )}
        <label className="auth-field">
          <span>CORREO</span><div><Mail size={17} /><input required type="email" defaultValue="andrea@mitienda.mx" placeholder="tu@negocio.mx" /></div>
        </label>
        <label className="auth-field">
          <span>CONTRASEÑA</span>
          <div><LockKeyhole size={17} /><input required minLength={6} type={showPassword ? "text" : "password"} defaultValue="retailo-demo" /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
        </label>

        <label className="auth-consent"><input type="checkbox" defaultChecked /><span><Check size={12} /></span>Mantener sesión iniciada</label>
        <button className="auth-submit" type="submit" disabled={submitting}>{submitting ? <i className="spinner" /> : <>{mode === "register" ? "Crear cuenta y continuar" : "Entrar"}<ArrowRight size={17} /></>}</button>
        <div className="auth-security"><ShieldCheck size={18} /><p><strong>Privacidad por diseño.</strong> RetaiLO analiza patrones agregados; nunca usa reconocimiento facial.</p></div>
      </form>
    </main>
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
  const submit = (event) => { event.preventDefault(); onContinue(); };
  return (
    <form className="setup-card" onSubmit={submit}>
      <header><span>01 / NUEVA TIENDA</span><h2>Registra tu primera sucursal</h2><Store size={25} /></header>
      <div className="setup-card__body">
        <label className="setup-field"><span>NOMBRE DE LA TIENDA</span><input required defaultValue="Sucursal Centro" placeholder="Ej. Sucursal Centro" /></label>
        <label className="setup-field"><span>DIRECCIÓN</span><div><MapPin size={17} /><input required defaultValue="Av. Universidad 1200, Monterrey" /></div></label>
        <DemoMap />
        <div className="setup-note"><Check size={15} /><span>La tienda se guardará localmente sólo durante esta demostración.</span></div>
      </div>
      <footer><button className="setup-primary" type="submit">Registrar tienda <ArrowRight size={16} /></button></footer>
    </form>
  );
}

function CameraSetup({ onBack, onContinue }) {
  const submit = (event) => { event.preventDefault(); onContinue(); };
  return (
    <form className="setup-card" onSubmit={submit}>
      <header><span>02 / PRIMERA CÁMARA</span><h2>Configura una fuente</h2><Camera size={25} /></header>
      <div className="setup-card__body">
        <label className="setup-field"><span>NOMBRE</span><input required defaultValue="Cámara principal" /></label>
        <label className="setup-field"><span>TIPO DE FUENTE</span><div className="setup-select"><Video size={17} /><select disabled defaultValue="demo_video"><option value="demo_video">Video demo local</option></select><ChevronDown size={16} /></div></label>
        <div className="demo-source"><FileVideo size={28} /><div><strong>demo-supermarket.mp4</strong><span>Fuente incluida · Control bloqueado</span></div><span className="demo-badge">DEMO</span></div>
        <label className="setup-field"><span>DESCRIPCIÓN</span><textarea defaultValue="Vista general del piso de venta" /></label>
        <div className="setup-warning"><CircleOff size={16} /><span>No hay una cámara física conectada. Webcam y RTSP quedan fuera del alcance de esta demo.</span></div>
      </div>
      <footer><button className="setup-back" type="button" onClick={onBack}><ArrowLeft size={15} /> Atrás</button><button className="setup-primary" type="submit">Registrar cámara <ArrowRight size={16} /></button></footer>
    </form>
  );
}

function ZonesSetup({ onBack, onSkip, onFinish }) {
  const [points, setPoints] = useState([{ x: 210, y: 155 }, { x: 1020, y: 145 }, { x: 1080, y: 590 }, { x: 180, y: 610 }]);
  const [activePoint, setActivePoint] = useState(0);
  const [selectedZone, setSelectedZone] = useState("Bebidas");
  const zoneTypes = [
    ["Bebidas", "product_area"], ["Snacks", "product_area"],
    ["Refrigeradores", "fridges"], ["Caja", "checkout"], ["Nueva zona", "other"],
  ];

  const updatePoint = (index, axis, rawValue) => {
    const limit = axis === "x" ? 1280 : 720;
    const value = Math.min(limit, Math.max(0, Number(rawValue) || 0));
    setPoints((current) => current.map((point, pointIndex) => pointIndex === index ? { ...point, [axis]: value } : point));
  };

  const placePoint = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = Math.round(((event.clientX - rect.left) / rect.width) * 1280);
    const y = Math.round(((event.clientY - rect.top) / rect.height) * 720);
    setPoints((current) => current.map((point, index) => index === activePoint ? { x, y } : point));
  };

  return (
    <div className="setup-card">
      <header><span>03 / ZONAS OPCIONALES</span><h2>Dibuja una zona en la cámara</h2><MousePointer2 size={25} /></header>
      <div className="setup-card__body">
        <p className="setup-intro">Selecciona un vértice y haz clic sobre la imagen para colocarlo. Las coordenadas usan la referencia original de la cámara: 1280 × 720 px.</p>
        <div className="polygon-editor">
          <div className="polygon-camera" onClick={placePoint} role="button" tabIndex="0" aria-label="Vista demo para colocar los puntos del polígono">
            <img src={retailoCameraLogo} alt="" />
            <span className="polygon-camera__demo"><i /> CÁMARA DEMO · 1280 × 720</span>
            <svg viewBox="0 0 1280 720" preserveAspectRatio="none" aria-hidden="true">
              <polygon points={points.map((point) => `${point.x},${point.y}`).join(" ")} />
              {points.map((point, index) => <g key={index} className={index === activePoint ? "is-active" : ""}><circle cx={point.x} cy={point.y} r="24" /><text x={point.x} y={point.y + 7}>{index + 1}</text></g>)}
            </svg>
            <span className="polygon-camera__hint"><MousePointer2 size={13} /> Clic para mover el punto {activePoint + 1}</span>
          </div>
          <div className="point-grid">
            {points.map((point, index) => (
              <div className={index === activePoint ? "is-active" : ""} key={index}>
                <button type="button" onClick={() => setActivePoint(index)}>PUNTO {index + 1}</button>
                <label>X <input type="number" min="0" max="1280" value={point.x} onChange={(event) => updatePoint(index, "x", event.target.value)} /></label>
                <label>Y <input type="number" min="0" max="720" value={point.y} onChange={(event) => updatePoint(index, "y", event.target.value)} /></label>
              </div>
            ))}
          </div>
        </div>
        <div className="zone-assignment">
          <div><span className="overline">ASIGNAR POLÍGONO A</span><small>Tipo enviado a la API</small></div>
          <div className="zone-type-options">
            {zoneTypes.map(([name, type]) => <button className={selectedZone === name ? "is-selected" : ""} type="button" onClick={() => setSelectedZone(name)} key={name}><span>{selectedZone === name && <Check size={12} />}</span><strong>{name}</strong><small>{type}</small></button>)}
          </div>
          {selectedZone === "Nueva zona" && <label className="new-zone-field"><span>NOMBRE DE LA NUEVA ZONA</span><input autoFocus placeholder="Ej. Panadería" /></label>}
        </div>
        <div className="setup-note"><Check size={15} /><span>Polígono válido: 4 puntos distintos listos para enviarse a la API.</span></div>
      </div>
      <footer><button className="setup-back" type="button" onClick={onBack}><ArrowLeft size={15} /> Atrás</button><button className="setup-skip" type="button" onClick={onSkip}>Omitir por ahora</button><button className="setup-primary" type="button" onClick={onFinish}>Terminar <ArrowRight size={16} /></button></footer>
    </div>
  );
}

function Onboarding({ onComplete, onLogout }) {
  const [step, setStep] = useState(1);
  const copy = onboardingCopy[step];
  return (
    <main className="onboarding-screen">
      <header className="onboarding-topbar"><Brand /><SetupSteps current={step} /><UserMenu onLogout={onLogout} /></header>
      <section className="onboarding-content">
        <div className="onboarding-story">
          <span className="overline overline--blue">{copy.overline}</span><h1>{copy.title}</h1><p>{copy.body}</p>
        </div>
        {step === 1 && <StoreSetup onContinue={() => setStep(2)} />}
        {step === 2 && <CameraSetup onBack={() => setStep(1)} onContinue={() => setStep(3)} />}
        {step === 3 && <ZonesSetup onBack={() => setStep(2)} onSkip={onComplete} onFinish={onComplete} />}
      </section>
    </main>
  );
}

function MetricBox({ number, label, detail, featured = false }) {
  return <article className={`metric-box ${featured ? "metric-box--featured" : ""}`}><span>{label}</span><strong>{number}</strong><small>{detail}</small></article>;
}

function ZoneComparison() {
  return (
    <div className="editorial-chart">
      <div className="editorial-chart__legend"><span><i /> Actividad detectada</span><span><i /> Ventas</span><em>Conversión estimada</em></div>
      {zones.map((zone, index) => (
        <div className="editorial-row" key={zone.name}>
          <span className="editorial-row__index">0{index + 1}</span><div className="editorial-row__name"><strong>{zone.name}</strong><small>{index < 2 ? "Área de producto" : index === 2 ? "Refrigeración" : "Punto de cobro"}</small></div>
          <div className="editorial-row__bars"><span style={{ width: `${zone.activity}%` }}><i>{zone.activity}</i></span><span style={{ width: `${zone.sales}%` }}><i>{zone.sales}</i></span></div><strong className="editorial-row__conversion">{zone.conversion}</strong>
        </div>
      ))}
    </div>
  );
}

function Dashboard({ onLogout }) {
  const [range, setRange] = useState("Hoy");
  const [mobileMenu, setMobileMenu] = useState(false);
  const data = dashboardRanges[range];
  return (
    <main className="report-screen">
      <header className="report-topbar">
        <Brand />
        <nav className={mobileMenu ? "is-open" : ""}><a className="is-active" href="#resumen"><LayoutDashboard size={15} /> Resumen</a><a href="#zonas"><BarChart3 size={15} /> Zonas</a><a href="#historial"><FileVideo size={15} /> Historial</a></nav>
        <UserMenu onLogout={onLogout} />
        <button className="report-menu" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Abrir menú">{mobileMenu ? <X /> : <Menu />}</button>
      </header>

      <div className="report-body" id="resumen">
        <section className="report-hero">
          <div className="report-hero__meta"><span>REPORTE · RTLO-150926</span><span>ACTUALIZADO 18:32</span></div>
          <div className="report-hero__content"><div className="report-symbol"><TrendingUp size={31} /></div><div><span className="overline">OPORTUNIDAD PRINCIPAL</span><h1>La actividad sube.<br />La conversión puede seguirla.</h1><p>Bebidas concentra la mayor actividad detectada, pero su respuesta de venta continúa debajo del promedio de la tienda.</p></div><div className="report-score"><strong>31.8%</strong><span>CONVERSIÓN<br />ESTIMADA</span></div></div>
          <div className="report-hero__actions"><button><Lightbulb size={15} /> VER RECOMENDACIÓN</button><span><Sparkles size={14} /> Basado en actividad agregada y ventas demo</span></div>
        </section>

        <section className="report-controls"><span>PERIODO ANALIZADO</span><div>{Object.keys(dashboardRanges).map((item) => <button className={range === item ? "is-active" : ""} onClick={() => setRange(item)} key={item}>{item}</button>)}</div><span className="report-demo"><i /> DATOS DE DEMOSTRACIÓN</span></section>

        <section className="metric-strip"><MetricBox number={data.conversion} label="CONVERSIÓN ESTIMADA" detail="Ventas / actividad válida" featured /><MetricBox number={data.sales} label="VENTAS REGISTRADAS" detail="Datos comerciales demo" /><MetricBox number={data.sessions} label="SESIONES ANALIZADAS" detail="Procesamientos completos" /><MetricBox number="4" label="ZONAS MONITOREADAS" detail="Cobertura configurada" /></section>

        <section className="analysis-section" id="zonas">
          <header><div><span className="overline overline--blue">01 / LECTURA POR ÁREA</span><h2>El pulso de tu tienda,<br />zona por zona.</h2></div><p>Comparamos señales relativas del video con ventas registradas. No inferimos identidades ni permanencia individual.</p></header>
          <ZoneComparison />
        </section>

        <section className="report-columns">
          <article className="evidence-panel" id="historial">
            <header><span className="overline overline--blue">02 / HISTORIAL</span><h2>Análisis recientes</h2><span>3 REGISTROS</span></header>
            <div className="finding-row finding-row--featured"><span>15 SEP<br />18:32</span><div><strong>Oportunidad detectada en Bebidas</strong><p>Actividad alta y conversión estimada 13 puntos debajo del promedio.</p></div><em className="history-status history-status--new">NUEVO</em></div>
            <div className="finding-row"><span>15 SEP<br />14:08</span><div><strong>Sesión de video completada</strong><p>La cámara principal procesó correctamente el archivo de demostración.</p></div><em className="history-status">COMPLETO</em></div>
            <div className="finding-row"><span>14 SEP<br />17:40</span><div><strong>Recomendación aceptada</strong><p>Promoción cruzada de Snacks marcada para seguimiento.</p></div><em className="history-status">REVISADO</em></div>
          </article>

          <article className="demo-camera-panel" id="camaras">
            <header><div><span className="overline">03 / DISPOSITIVOS</span><h2>Cámaras activas</h2></div><span className="camera-count">1 / 2</span></header>
            <div className="camera-list">
              <article><span className="camera-list__icon"><Camera size={20} /></span><div><strong>Cámara principal</strong><small>Video demo · demo-supermarket.mp4</small></div><em className="camera-state camera-state--active"><i /> ACTIVA</em></article>
              <article><span className="camera-list__icon"><Camera size={20} /></span><div><strong>Cámara de caja</strong><small>Sin fuente configurada</small></div><em className="camera-state"><i /> INACTIVA</em></article>
            </div>
            <div className="camera-disabled"><CircleOff size={17} /><p><strong>Hardware no disponible</strong>El estado activo corresponde a la fuente demo. Los controles físicos permanecen deshabilitados.</p></div>
          </article>
        </section>

        <footer className="report-footer"><Brand /><span>PRIVACIDAD POR DISEÑO · SIN RECONOCIMIENTO FACIAL</span><span>RETAILO ANALYTICS · 2026</span></footer>
      </div>
    </main>
  );
}

export default function App() {
  const initialScreen = window.location.hash === "#dashboard" ? "dashboard" : window.location.hash === "#onboarding" ? "onboarding" : "auth";
  const [screen, setScreen] = useState(initialScreen);
  const navigate = (next) => { window.history.replaceState(null, "", next === "auth" ? "#login" : `#${next}`); window.scrollTo({ top: 0, behavior: "smooth" }); setScreen(next); };
  if (screen === "auth") return <AuthScreen onAuthenticated={(mode) => navigate(mode === "login" ? "dashboard" : "onboarding")} />;
  if (screen === "onboarding") return <Onboarding onComplete={() => navigate("dashboard")} onLogout={() => navigate("auth")} />;
  return <Dashboard onLogout={() => navigate("auth")} />;
}
