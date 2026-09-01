# Backlog & User Stories

## Propósito y alcance

RetaiLO Analytics convierte video de cámaras existentes en métricas de tráfico y permanencia por zona. El MVP detecta personas y analiza patrones; no implementa reconocimiento facial, identificación de clientes ni almacenamiento de imágenes o video en la API.

El trabajo se dividirá en dos frentes que avanzan en paralelo:

- **API REST:** configuración de tiendas, cámaras y zonas; recepción de resultados; analítica e insights.
- **CAMARA:** procesamiento local, detección y conteo por zona, y envío de métricas agregadas a la API.

Prioridades: **MH** obligatorio para la demo, **SH** deseable y **CH** opcional. Los elementos CH no deben bloquear los MH por ningún motivo.

> Todo el backlog es una puesta al aire, cada desarrollador tiene la eleccion de seguir al pie de la letra dicho plan o modificarlo, cualquier modificacion estara en ADR registrada.

---

## API REST

### STORES (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /stores` | Registra una tienda. |
| Listar | `GET /stores` | Lista las tiendas disponibles. |
| Consultar | `GET /stores/{store_id}` | Obtiene una tienda por su ID. |
| Actualizar | `PATCH o PUT /stores/{store_id}` | Actualiza campos. |
| Eliminar | `DELETE /stores/{store_id}` | Elimina o desactiva una tienda. |

Campo mínimo:

```json
{
    "name": "abarrotes LaMunuwa"
}
```

Campos opcionales sugeridos: `code`, `address`, `timezone` e `is_active`.

### CAMERAS (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /stores/{store_id}/cameras` | Registra una cámara en una tienda. |
| Listar | `GET /stores/{store_id}/cameras` | Lista las cámaras de una tienda. |
| Consultar | `GET /cameras/{camera_id}` | Obtiene los detalles de una cámara por su ID. |
| Actualizar | `PATCH o PUT /cameras/{camera_id}` | Actualiza campos. |
| Eliminar | `DELETE /cameras/{camera_id}` | Elimina o desactiva una cámara. |

Campos mínimos:

```json
{
    "name": "camara de abarrotes LaMunuwa",
    "source_type": "demo_video",
}
```

Campos opcionales sugeridos: `description` e `is_active`.

Tipos iniciales: `demo_video`. En la realidad, debería ser webcam, cam y otros tipos; por tiempo, nos acoplaremos al video demo.

### ZONES (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /cameras/{camera_id}/zones` | Registra un polígono. |
| Listar | `GET /cameras/{camera_id}/zones` | Lista zonas por cámara. |
| Actualizar | `PATCH o PUT /zones/{zone_id}` | Actualiza metadatos o puntos. |
| Eliminar | `DELETE /zones/{zone_id}` | Elimina o desactiva una zona. |

Campos mínimos:

```json
{
  "name": "Refrigeradores",
  "zone_type": "product_area",
  "points": [
    {"x": 120, "y": 80},
    {"x": 430, "y": 85},
    {"x": 450, "y": 300},
    {"x": 110, "y": 295}
  ]
}
```

`points` debe contener al menos cuatro puntos (cuadrado o rectangulo)

Tipos iniciales: `product_area`, `checkout`, `entrance_exit`, `fridges` y `other`.

> Nota: Las zonas son puntos en una cámara; en un dashboard es posible generar una interfaz interactiva; sin él se tendrán puntos preestablecidos para la DEMO.

### SESSIONS (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /cameras/{camera_id}/sessions` | Registra el inicio de una sesión y devuelve su identificador. |

Campos mínimos posibles:

```json
{
  "source_type": "demo_video",
  "started_at": "2026-07-30T12:00:00Z",
  "settings": {
    "frame_sample_rate": 5,
    "confidence_threshold": 0.45
  }
}
```

Respuesta mínima esperada:

```json
{
  "session_id": 1,
  "camera_id": 1,
  "status": "running",
  "started_at": "2026-07-30T12:00:00Z"
}
```

Al finalizar la API puede marcar automáticamente la sesión como
`completed`. Si la corrida falla, se muestra un mensaje de error.

### RESULTS (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /sessions/{session_id}/video-results` | Crea un resumen de la sesión. |
| Consultar | `GET /sessions/{session_id}/video-results` | Consulta resultados de la sesión. |

Campos mínimos:

```json
{
    "processed_frames": 1000,
    "elapsed_seconds": 10,
    "detected_people": 10,
    "started_at": "2026-07-30T12:00:00",
    "finished_at": "2026-07-30T12:01:38",
    "zone_metrics": [
        {
            "zone_id": 1,
            "visits": 10,
            "dwell_seconds": 10,
            "traffic_share": 10
        }
    ]
}
```

Aquí se comunican los datos recolectados con la API; primero, al iniciar una sesión, se crea un ID para dicha sesión y, si se logra completar, obtiene los datos y genera un resumen.

### ANALYTICS (MH)

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `GET /stores/{store_id}/analytics/summary` | Resumen de flujo, visitas y zonas destacadas. |
| Consultar | `GET /stores/{store_id}/analytics/traffic` | Tráfico y permanencia por zona. |
| Consultar | `GET /stores/{store_id}/analytics/insights` | Hallazgos y sugerencias accionables. |

Campos mínimos en `insights`:

```json
{
  "type": "HIGH_TRAFFIC_LOW_SALES",
  "zone_id": "zone_001",
  "zone_name": "Refrigeradores",
  "message": "La zona Refrigeradores concentra 42% de las visitas, pero los productos ubicados en esa zona representan solo 18% de las ventas.",
  "suggestion": "Revisar disponibilidad, precio, promociones o acomodo de productos."
}
```

En su mayoría, los endpoints del tipo GET deberían contar con paginación y/o filtro de fechas; de ser necesario, este específicamente, es estrictamente necesario el filtro de fechas.

Tipos iniciales: `HIGH_TRAFFIC_LOW_SALES`, `LOW_TRAFFIC_HIGH_SALES`, `LOW_TRAFFIC_LOW_SALES`, `HIGH_TRAFFIC_HIGH_SALES`.

### RECOMMENDATIONS (SH)

Pueden vivir dentro de `analytics/insights`. Si el tiempo lo permite, este endpoint permite persistencia y seguimiento:

| Operación | Endpoint | Propósito |
| --- | --- | --- |
| Crear | `POST /stores/{store_id}/recommendations/generate` | Crear recomendaciones en base a las analíticas. |
| Listar | `GET /stores/{store_id}/recommendations` | Listar todas las recomendaciones de una tienda. |
| Actualizar | `PATCH o PUT /recommendations/{recommendation_id}/status` | Actualizar el estado de una recomendacion. |

El body queda completamente a la imaginación del desarrollador; únicamente debe tener: `status` (`pending`, `accepted` o `rejected`).

### EXTRAS (CH)

La simulación de ventas puede ser un endpoint sencillo o una carga manual, a decisión del equipo API. Debe consumir como máximo el 5% del tiempo de desarrollo y asociar ventas con zona o categoría, nunca con una persona.

El dashboard web es opcional y no debe bloquear el MVP: los endpoints analíticos deben poder demostrar el resultado sin frontend.

---

## CAMARA

### Agente local de procesamiento (MH)

- Procesar `demo_video`, webcam y, si hay tiempo, streams RTSP.
- Detectar personas con YOLO y OpenCV.
- Configurar el umbral de confianza y el muestreo de frames.
- Contar detecciones y asignarlas a zonas poligonales configurables.
- Calcular por zona visitas/conteos, permanencia aproximada y proporción de tráfico.
- Ejecutar en CPU como baseline obligatorio para simular el equipo cliente.
- Usar CUDA como aceleración opcional de desarrollo/demo, nunca como requisito.
- Crear sesiones y publicar resultados agregados mediante un contrato con la API.
- Reportar errores de fuente, modelo y red sin enviar datos parcialmente inválidos.

### Robustez (SH)

- Seguimiento ligero para no contar repetidamente a una persona entre frames.
- Buffer local y reintentos acotados cuando la API no esté disponible.
- Configuración externa para fuente, modelo, credenciales e inferencia.
- Registro estructurado de inicio, fin, rendimiento y errores por sesión.

---

## User Stories

El orden de registro es ascendente. En la parte superior estará la US más actual; en la parte inferior, las más antiguas. No es necesario registrar como US correcciones o cambios menores; es una guía para el desarrollo de x feature.

## Sprint 1

### Feature: Crear esquema Pydantic VideoResult para métricas agregadas

**Prioridad:** Must Have (MH)

**Dificultad:** 2 Story Points

**As a** desarrolladora de la API, **I want to** tener el esquema Pydantic para `VideoResult`, **So that** la API pueda recibir y validar correctamente las métricas agregadas que enviará la cámara.

```gherkin
Scenario: Validar resultado de sesión correcto
  Given un payload JSON con métricas agregadas (frames, personas, tiempos y zonas)
  When se procesa con el modelo VideoResult
  Then la validación es exitosa y los tipos de datos son correctos.

Scenario: Rechazar resultado con datos faltantes o incorrectos
  Given un payload JSON que omite campos obligatorios o envía tipos erróneos
  When se procesa con el modelo VideoResult
  Then Pydantic devuelve un error de validación ValidationError.

```

**Definition of Done (DoD):**

* [ ] Pasa linter (`ruff check`) y tipado estricto (`mypy`).
* [ ] Pruebas unitarias completadas y exitosas (`pytest`).
* [ ] Cobertura de pruebas mantenida en >= 80%.
* [ ] Criterios de aceptación cumplidos.

---

## US-0X: Titulo

**Prioridad:** MoSCoW prioritization method

**Dificultad:** Story Points

**As** ... , **I want to** ... , **So that** ...

```gherkin
Scenario:
  Given
  When
  Then
  And
```

