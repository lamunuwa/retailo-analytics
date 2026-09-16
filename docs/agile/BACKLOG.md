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
  "started_at": "2026-07-30T12:00:00Z"
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

- Procesar videos demo cargados en `vision/data/demo`.
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

## Sprint 2

### 15. Persistencia y seguimiento de recomendaciones

**Prioridad:** Should Have (SH)

**Dificultad:** 3 Story Points

**As** operador de una tienda, **I want to** generar y clasificar recomendaciones derivadas de los insights, **So that** pueda dar seguimiento a las acciones aceptadas o rechazadas.

```gherkin
Scenario: Generar recomendaciones sin duplicar pendientes
  Given una tienda con analíticas disponibles
  When solicito POST /stores/{store_id}/recommendations/generate
  Then se persiste una recomendación pendiente por zona e insight
  And una segunda generación reutiliza las recomendaciones pendientes existentes

Scenario: Actualizar el estado de una recomendación
  Given una recomendación existente
  When envío PATCH /recommendations/{recommendation_id}/status
  Then su estado cambia a pending, accepted o rejected
```

### 14. Analítica por tienda e integración de ventas demo

**Prioridad:** Must Have (MH)

**Dificultad:** 5 Story Points

**As** responsable de una tienda, **I want to** consultar tráfico, permanencia, ventas e insights por periodo, **So that** pueda identificar oportunidades operativas por zona.

```gherkin
Scenario: Consultar métricas agregadas por periodo
  Given resultados de video y ventas agregadas por zona
  When consulto summary, traffic o insights con start_date y end_date
  Then recibo únicamente métricas del periodo solicitado
  And los porcentajes se recalculan sobre los totales filtrados

Scenario: Cargar ventas de demostración sin datos personales
  Given una zona que pertenece a la tienda
  When envío POST /stores/{store_id}/sales con unidades, ingreso y categoría
  Then la venta agregada queda disponible para comparar traffic_share y sales_share
```

### 13. Publicación append-only de resultados de video

**Prioridad:** Must Have (MH)

**Dificultad:** 5 Story Points

**As** agente local de Vision, **I want to** publicar una sola colección de métricas al terminar una sesión, **So that** la API conserve un resumen íntegro y pueda completar la sesión atómicamente.

```gherkin
Scenario: Publicar un resultado válido
  Given una sesión running y métricas de zonas pertenecientes a su cámara
  When envío POST /sessions/{session_id}/video-results
  Then se guardan el resumen y sus métricas en una transacción
  And la sesión cambia a completed

Scenario: Proteger la integridad append-only
  Given una sesión que ya tiene resultado
  When intento publicar otro resultado
  Then la API responde 409 Conflict sin modificar el resultado original
```

### 12. Gestión de zonas poligonales por cámara

**Prioridad:** Must Have (MH)

**Dificultad:** 5 Story Points

**As** operador de RetaiLO, **I want to** crear, consultar, editar y desactivar zonas ROI, **So that** Vision procese exactamente la distribución configurada para cada cámara.

```gherkin
Scenario: Crear un polígono válido
  Given una cámara activa y cuatro o más puntos distintos con área
  When envío POST /cameras/{camera_id}/zones
  Then la API guarda la zona y devuelve 201 Created

Scenario: Rechazar zonas inválidas o duplicadas
  Given puntos colineales o un nombre ya usado en la misma cámara
  When intento crear o actualizar la zona
  Then la API responde 422 o 409 sin guardar datos inválidos
```

### 11. Contrato desacoplado entre Vision y API

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** desarrollador del agente local, **I want to** centralizar rutas y payloads del contrato HTTP, **So that** los cambios de API no queden hardcodeados dentro de la detección.

```gherkin
Scenario: Ejecutar el ciclo completo del agente
  Given una cámara con zonas configuradas en la API
  When Vision inicia una corrida
  Then consulta las zonas, crea la sesión y procesa el video
  And publica visitas, permanencia y proporción de tráfico por zone_id

Scenario: Manejar una falla transitoria
  Given un error temporal de red o servidor
  When el agente realiza una petición
  Then aplica reintentos acotados y reporta un error explícito si no se recupera
```

### 10. Gestión de Sesiones de Video (Sessions CRUD)

**Prioridad:** Must Have (MH)

**Dificultad:** 5 Story Points

**As** desarrollador de la API, **I want to** crear, consultar y actualizar sesiones de video vinculadas a cámaras, **So that** pueda rastrear el ciclo de vida del procesamiento de video (running → completed/failed) y correlacionar resultados con cada ejecución.

```gherkin
Scenario: Crear una sesión al iniciar el procesamiento de video
  Given un camera_id válido y un payload JSON con "started_at" opcional
  When el cliente/vision envía una petición POST a /cameras/{camera_id}/sessions
  Then la API valida que la cámara existe, crea la sesión con status="running"
  And responde con código 201 Created y los datos de la sesión (id, camera_id, status, started_at).

Scenario: Actualizar el estado de una sesión al finalizar
  Given un session_id válido y un payload JSON con "status" y "finished_at"
  When el cliente/vision envía una petición PATCH a /sessions/{session_id}
  Then la API valida la sesión, actualiza status (completed|failed) y finished_at
  And responde con código 200 OK y los datos de la sesión actualizada.

Scenario: Consultar el estado de una sesión en progreso
  Given un session_id válido
  When se envía una petición GET a /sessions/{session_id}
  Then la API retorna los datos completos de la sesión (id, camera_id, status, started_at, finished_at)
  And permite al cliente monitorear si el procesamiento está en curso o completado.

Scenario: Listar sesiones de una cámara específica
  Given un camera_id válido
  When se envía una petición GET a /cameras/{camera_id}/sessions
  Then la API devuelve un listado paginado de todas las sesiones históricas
  And ordena por started_at descendente por defecto.
```

## Sprint 1

### 9. Gestión de Cámaras (Cameras CRUD)

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** a desarrollador de la API, **I want to** registrar, consultar, actualizar y desactivar cámaras vinculadas a una tienda específica, **So that** pueda estructurar la procedencia del video y preparar el terreno para la configuración de zonas ROI.

```gherkin
Scenario: Crear una cámara vinculada a una tienda existente
  Given un store_id válido y un payload JSON con "name" y "source_type"
  When el cliente envía una petición POST a /stores/{store_id}/cameras
  Then la API valida la relación, guarda la cámara en la base de datos
  And responde con código 201 Created y los datos de la cámara generada.

Scenario: Listar las cámaras de una tienda específica
  Given un store_id que contiene múltiples cámaras activas
  When se envía una petición GET a /stores/{store_id}/cameras
  Then la API devuelve un listado con las cámaras correspondientes
  And omite aquellas marcadas con is_active en false.

Scenario: Desactivar una cámara (Soft Delete)
  Given el camera_id de una cámara activa
  When se envía una petición DELETE a /cameras/{camera_id}
  Then la API actualiza la cámara marcando is_active como false
  And retorna 200 OK sin eliminar el registro físicamente.
```

### 8. Ingesta de eventos de detección de personas

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** desarrollador del sistema, **I want to** enviar los datos de conteo de personas y zonas a la API mediante un endpoint de ingesta, **So that** el sistema almacene el tráfico de la tienda en tiempo real para su posterior análisis.

```gherkin
Scenario: Ingesta exitosa de detecciones
  Given un payload JSON válido con el camera_id, zone_name, people_count y timestamp
  When el agente envía una petición POST a /analytics/detections
  Then la API valida los datos, los guarda en la base de datos y responde con código 201 Created.

Scenario: Rechazar métricas incompletas
  Given un payload JSON que omite la cantidad de personas detectadas o campos obligatorios
  When el agente envía la petición POST
  Then la API responde con un error 422 Unprocessable Entity.

```

### 7. Consulta, filtrado avanzado y paginación de detecciones analíticas

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** desarrollador del sistema, **I want to** consultar y filtrar el historial de detecciones y conteo de personas mediante la API, **So that** el sistema permita la analítica y visualización del tráfico en las diferentes zonas y cámaras de la tienda.

```gherkin
Scenario: Consulta general de detecciones sin filtros
  Given que existen eventos de detección registrados en la base de datos
  When se realiza una petición GET a `/analytics/detections` sin parámetros
  Then la API responde con código 200 OK y el listado completo de los registros paginados por defecto.

Scenario: Filtrado avanzado y paginación de detecciones
  Given que se envían parámetros opcionales de filtrado como `camera_id`, `zone_name`, `start_date`, `end_date`, `limit` y `offset`
  When se realiza una petición GET a `/analytics/detections`
  Then la API procesa los filtros de manera estricta y devuelve únicamente los registros que coinciden con el criterio en orden descendente por timestamp.

```

### 6. Detección de personas en zonas específicas

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As**operador de la plataforma de RetaiLO, **I want to** detectar personas y consultar su conteo acumulado por zona, **So that** pueda observar el flujo de personas en las áreas definidas del establecimiento..

```gherkin
Scenario: Detectar y contabilizar personas por zona
  Given un modelo YOLO configurado para detectar personas y zonas ROI válidas
  When inicio una sesión de detección
  Then el sistema procesa los fotogramas
  And acumula una detección en la zona donde se encuentre cada persona
  And detecciones totales y conteos por zona

Scenario: Procesar fotogramas sin detecciones válidas (seguridad)
  Given un resultado de inferencia sin imagen original o sin personas detectadas
  When el sistema procesa el resultado
  Then ignora el resultado sin imagen
  And continúa la sesión con los fotogramas válidos sin incrementar conteos

Scenario: Visualizar el conteo durante la sesión
  Given una sesión de detección activa
  When se procesa un fotograma con personas detectadas
  Then se muestran las ROI, las cajas de detección y el conteo acumulado de cada zona
```

### 5. Zonas divididas

**Prioridad:** Must Have (MH)

**Dificultad:** 2 Story Points

**As** consumidor de RetaiLO, **I want to** configurar manualmente zonas de mi tienda, **So that** pueda visualizar y dividir mi tienda en zonas.

```gherkin
Scenario: Configurar zonas ROI válidas
  Given una configuración manual con una o más zonas nombradas
  And cada zona tiene al menos tres puntos que forman un polígono
  When inicio el procesamiento de Vision
  Then las zonas quedan disponibles para evaluar las detecciones del video

Scenario: Rechazar una configuración de zonas incompleta
  Given una configuración sin zonas o con una zona que no forma un polígono
  When intento iniciar el procesamiento de Vision
  Then recibo un error de validación que explica la configuración inválida
```

### 4. Crear esquemas Pydantic para Cameras

**Prioridad:** Must Have (MH)

**Dificulta d:** 2 Story Points

**As a** desarrollador de la API, **I want to** tener los esquemas Pydantic para la entidad Camera, **So that** la API pueda validar la creación y actualización de cámaras asociadas a una tienda.

```gherkin
Scenario: Validar creación de cámara con datos correctos
  Given un payload JSON con "name" y "source_type"
  When se procesa con el modelo de creación de cámara
  Then la validación es exitosa.

Scenario: Rechazar cámara sin campos obligatorios
  Given un payload JSON que omite "name" o "source_type"
  When se procesa con el modelo
  Then Pydantic devuelve ValidationError.
```

### 3. Gestión de Tiendas (Stores CRUD)

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** Desarrollador de la API, **I want to** registrar, consultar, actualizar y desactivar tiendas, **So that** pueda estructurar y agrupar las cámaras analíticas por sucursal física.

```gherkin
Scenario: Crear una tienda nueva con los datos mínimos
  Given un payload JSON válido que contiene el campo obligatorio "name"
  When se envía una petición POST a /stores
  Then la API responde con código 201 Created
  And la respuesta incluye el store_id generado y el campo is_active en true.

Scenario: Consultar el listado general de tiendas
  Given que existen múltiples tiendas registradas en la base de datos
  When se envía una petición GET a /stores
  Then la API devuelve una lista con los datos de las tiendas
  And la respuesta no incluye las tiendas que han sido desactivadas lógicamente.

Scenario: Desactivar una tienda (Soft Delete)
  Given el store_id de una tienda activa en el sistema
  When se envía una petición DELETE a /stores/{store_id}
  Then la API actualiza la tienda marcando is_active como false
  And la base de datos no elimina el registro físicamente para preservar el historial analítico.

Scenario: Rechazar creación de tienda sin nombre
  Given un payload JSON que omite el campo "name"
  When se envía una petición POST a /stores
  Then Pydantic rechaza la petición
  And la API responde con un error 422 Unprocessable Entity.
```

### 2. Crear esquema Pydantic VideoResult para métricas agregadas

**Prioridad:** Must Have (MH)

**Dificultad:** 2 Story Points

**As a** desarrollador de la API, **I want to** tener el esquema Pydantic para `VideoResult`, **So that** la API pueda recibir y validar correctamente las métricas agregadas que enviará la cámara.

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

### 1. Detectar personas en video de demostración

**Prioridad:** Must Have (MH)

**Dificultad:** 3 Story Points

**As** desarrolladora de visión artificial, **I want to** ejecutar un modelo YOLO sobre los frames de un video de demostración, **So that** pueda validar la detección de personas antes de implementar zonas, métricas y comunicación con la API.

```gherkin
Scenario: Detección de personas en un video de demostración
  Given un video de demostración y un modelo YOLO
  And un entorno con GPU CUDA disponible o CPU como alternativa
  When ejecuto el agente sobre el video
  Then el agente procesa los frames seleccionados
  And conserva únicamente detecciones de la clase persona que superen el umbral configurado
  And informa en consola si usa CUDA o CPU
```
