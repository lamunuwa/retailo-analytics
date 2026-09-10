# Bitácora de uso de IA

Documentación de la interacción con inteligencia artificial generativa utilizada como asistencia para el desarrollo del proyecto.

> Regla de oro: Se puede usar libremente IA, con la condición de registrar criterio, validación y qué se aceptó/rechazó y por qué.

El orden de registro es ascendente. En la parte superior estará el registro más reciente. No es necesario registrar interacciones triviales como autocompletados, breves preguntas, etc.

---

## [2026-09-10] Comunicacion API-YOLO por medio de SESSIONS

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Tuve un par de muchos problemas para hacer que esto funcionara; específicamente, tuve problemas con los dockers, con internal server error y, cuando ya se dignó a funcionar con el contrato de la API, no se comunicaba ni en local. Aparte de que empecé a hacer los típicos parches de arreglar código con más código y le pedí a Sol que me apoyara, usé el siguiente prompt:

> Acabo de generar un modulo completo de la API, SESSIONS. Puedes ver un poco de informacion dentro de `BACKLOG.md`, estos endpoints son los que comunican la API con la vision artificial de nuestro proyecto, deberian comportarse algo asi: uno guarda el puro estado de como esta corriendo la vision (sessions), el otro guarda los settings en general de la session (results) y el otro guarda los datos que le importan al cliente (analytics), esas son sus responsabilidades y por eso existen.
>
> Ahora mismo genere la migracion, tests y demas. Quiero que valides esto:
>
> - Primero vas a entrar al .venv para ejecutar ruff, mypy, pytest. Si fallan arreglalos. Intenta no modificar la logica de programacion, exceptuando pytest, ahi la idea es que los test obligan al codigo a cumplirlos no al revez (solo te permito modificar los tests si son tests que con este nuevo endpoint quedaron obsoletos)
> - Luego vas a validar la logica, dime si teoricamente debe funcionar, este nuevo endpoint DEBE adecuarse a lo que hay no lo que hay a el, eso es OBLIGATORIO
> - La idea de vision obviamente es que funcione en la camara, sin embargo para fines practicos del proyecto usamos videos cargados en `vision/data/demo`, si encuentras algo en vision referente a reproducirse en camara eliminalo, es innecesario

**Qué se generó / propuso:** Generó 3 cambios importantes:

- Al parecer, mi lógica de visión también incluía código muerto que quería ejecutar la cámara, entonces lo elimino.
- Corrigió Alembic.
- Corrigió la forma en la que comunicó la API (No me gustó del todo la forma, porque no termino de entender qué hizo).

**Qué se aceptó y qué se rechazó, y por qué:** Acepté todo en general, solo hubo una breve cosa: mi ChatGPT tiene cargado en su AGENTS.md que cada que necesite validar algo de dockers, lo simule y saque los logs. Aquí el problema fue que no prendían los dockers y quería mover algo dentro del .env (archivo ignorado en repo), cosa que no iba, no había forma de que eso arreglara el problema y lo decliné.

**Validación:** Pytest, Ruff y Mypy aprobaron satisfactoriamente todas las reglas de cobertura y validación de tipos. ChatGPT mencionó que Docker estaba corriendo y lo probé, abrí el Swagger, creé una tienda, una cámara y la pasé al local de visión con `API_BASE_URL=http://localhost:8000 / CAMERA_ID=1 / DEMO_VIDEO_PATH=vision/data/demo/supermarket.mp4 / python -m vision.src.main`, después traje con GET las sesiones de la cámara creada y apareció la sesión correctamente, en proceso y finalizada.

## [2026-09-09] Planteamiento del endpoint SESSION

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** Github Copilot

**Qué se pidió:** Durante el Sprint 1, funcioné como desarrolladora de la parte de YOLO y OpenCV; no entré en nada de la API más allá de revisiones básicas. Ahora necesitaba un breve roadmap más claro del que tenía para ejecutar un endpoint que conecte YOLO con nuestra API. Use este prompt:

> Desde el inicio del proyecto habiamos planteado un backlog con todo lo que deberiamos tener para entregar el proyecto 100% funcional, yo tengo que retirarme un par de dias dado que tengo otra competencia. Mi parte siempre fue la vision artificial pero ahi ya ayude bastante, en este momento quiero apoyarles con la API.
>
> Revisa `BACKLOG.md`, ahi tendras toda la informacion de que debemos hacer en los diferentes modulos de RetaiLO Analytics.
>
> Ahora mismo un partner esta desarrollando zones. Por lo que queda:
>
> - Sessions
> - Results
> - Analytics
> Todo esto tiene que ver con la coneccion vision con API, apoyare por ese lado.
>
> Despues de entender este contexto revisa: `app/src` y `vision/src`, revisa todos los modulos y capas que hay. Despues me diras que tengo que hacer para generar SESSIONS. La informacion de que hace esta en backlog, pero en general cuando yo prendo la parte de vision se autogenera un POST de que inicio la session con algunos campos.

Despues de este prompt me dio lo solicitado pero antes de ejecutar le pregunte como veia mejor el dividir responsabilidades con este prompt:

> Tambien, tanto los endpoint de sessions, results y analytics son como que van muy de la mano. Crees que es buena idea mantenerlos los 3 o mejor hacemos solo 2 o hacemos un frankstain de los 3. Dame tu opinion. Segun yo uno guarda el puro estado de como esta corriendo la vision, el otro guarda los settings en general de la session y el otro guarda los datos que le importan al cliente, esas son sus responsabilidades y por eso existen, pero que opinas tu...

**Qué se generó / propuso:** Genero el roadmap para lograr que "funcionara a la primera" el endpoint de SESSIONS junto con la comunicación API-YOLO; el contrato ya lo tenía anotado porque fue de lo primero que comenté con ChatGPT antes de siquiera empezar la semana 7.

**Qué se aceptó y qué se rechazó, y por qué:** En este tipo de solicitudes de planificación y/o estructuración de ideas no suelo rechazar muchas cosas, dado que directamente no aparecen los botones de rechazar, por lo que la única modificación que se hizo fue el segundo prompt.

**Validación:** N/A

## [2026-09-09] Correcciones finales del sprint 1

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Hice una revision un poco mas profunda que lo que comunmente hice dentro del proyecto. Hasta este punto todo funcionaba teoricamente, pero tocaba dejarlo vivo realmente. Encontre multiples puntos de mejora y algun que otro error puntual. Este fue el prompt
:
> Te voy a enlistar los errores que vas a resolver:
>
> - Primero que nada pytest no pasa, marca errores y warnings. Ejecuta el .venv y haz pytest
> - Dentro de `app/src/repos/analytics.py` tenemos un repositorio sin Protocol, no cumple correctamente con que las capas superiores no dependen de inferiores si no de abstracciones, genera un Protocol de AnalyticsRepository, para que tengamos la asbtraccion y los modulos se reproducen con esa abstract
> - En el swagger, seccion Stores, sale primero get, post, delete, patch, que aparezca en este orden: Post, get, patch, delete. Aprovecha para agregarle el Get que le falta, tenemos enlistado pero no tenemos busqueda por id
> - Revisa que las logicas de patch sean de patch y no de put
> - No tenemos router de health, el que tenemos ahorita es el basico de FastAPI. Agrega algo asi y elimina el endpoint basico de main.py:
>
> ```python
> import os
> import time
> from datetime import datetime
>
> from fastapi import APIRouter, Depends, status
> from fastapi.responses import JSONResponse
> from sqlalchemy import text
> from sqlalchemy.orm import Session
>
> from app.db import get_db
>
> router = APIRouter(tags=["HEALTH"])
>
> START = time.time()
> VERSION = os.getenv("SensorHub", "1.0.0")
>
>
> @router.get("/health", status_code=status.HTTP_200_OK)
> def health_check(db: Session = Depends(get_db)) -> JSONResponse:
>
>    uptime = round(time.time() - START, 2)
>
>     db_status = "healthy"
>     db_latency = None
>
>     try:
>         start_db_time = time.perf_counter()
>         db.execute(text("SELECT 1"))
>         db_latency = round((time.perf_counter() - start_db_time) * 1000, 2)
>     except Exception as e:
>         db_status = f"unhealthy: {str(e)}"
>
>     is_healthy = db_status == "healthy"
>     global_status = "ok" if is_healthy else "degraded"
>
>     payload = {
>         "status": global_status,
>         "version": VERSION,
>         "timestamp": datetime.now().isoformat(),
>         "uptime_seconds": uptime,
>         "checks": {
>             "database": {
>                 "status": db_status,
>                 "latency": db_latency,
>             }
>         },
>     }
>
>    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
>
>     return JSONResponse(content=payload, status_code=status_code)
>```
>
> - Agrega algo asi en main pero con los datos que manejamos:
>
> ```python
> from fastapi import FastAPI
> from fastapi.responses import RedirectResponse
>
> from app.routers import alerts, health, readings, sensors
>
> tags_metadata = [
>     {
>         "name": "SENSORS",
>         "description": "Operaciones para el manejo de inventario de sensores.",
>     },
>     {
>         "name": "READINGS",
>         "description": "Registro y consultas de lecturas de sensores.",
>     },
>     {
>         "name": "ALERTS",
>         "description": "Consultas y status de alertas generadas por sensores.",
>     },
>     {
>         "name": "HEALTH",
>         "description": "Verifica la salud del servicio",
>     },
> ]
>
> app = FastAPI(
>     title="SensorHub API",
>     version="1.0.0",
>     openapi_tags=tags_metadata,
> )
>
> app.include_router(sensors.router)
> app.include_router(readings.router)
> app.include_router(alerts.router)
>
>
> @app.get("/", include_in_schema=False)
> async def root() -> RedirectResponse:
>     return RedirectResponse(url="/docs")
> ```
>
> Al final haras lo tipico: activa el .venv, mypy, ruff, pytest y aprovecha para verificar los logs del docker, para ver que todo este bien y que corra en la ultima imagen, de ser necesario genera la migracion en alembic (aunque no deberias tocar los esquemas).

**Qué se generó / propuso:** Lo más importante son las cosas que detecto que yo no:

- Detecto algunas incompatibilidades que elimino fijando versiones específicas de FastAPI que se pueden ver en `requirements.txt`
- Agrego a la db `from sqlalchemy import create_engine` y `from sqlalchemy.engine import Engine`. Reviso incompatibilidades con Docker y producción por este cambio y no encuentro nada. Habrá que avanzar y ver cómo se comporta

De ahí en fuera, ejecuto todo tal cual se lo solicité.

**Qué se aceptó y qué se rechazó, y por qué:** Solo no acepte un archivo que nunca vi, parece ser que era para pytest, se llamaba `conftest.py`. Cuando lo decline agrego el create_engine, lo que si entiendo y lo mantuve.

**Validación:** Pytest y Ruff aprobaron satisfactoriamente todas las reglas de cobertura y validación de tipos tras la implementación.

## [2026-09-08] Módulo Cameras CRUD y estabilización de pruebas

**Quién:** @FrankArmed | Frank Asael

**Herramienta:** Gemini (AI Collaborator)

**Qué se pidió:** Refactorizar el Soft Delete en el repositorio y añadir aserciones estrictas a los Mocks del router basándose en el Peer Review.

**Qué se generó / propuso:** Validación de `is_active` en el método de actualización del repositorio y aserciones `assert_called_once_with` en todas las pruebas HTTP para garantizar que los parámetros enviados coincidan exactamente.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptaron todas las modificaciones para blindar la API frente a modificaciones de recursos inactivos (404 Not Found) y asegurar que las pruebas de los endpoints pasen únicamente si la capa HTTP transfiere los datos correctos a la capa de persistencia.

**Validación:** Pytest y Ruff aprobaron satisfactoriamente todas las reglas de cobertura y validación de tipos tras la implementación.

## [2026-09-08] Módulo Analytics Filtering

**Quién:** @FrankArmed | Frank Asael

**Herramienta:** Gemini (AI Collaborator)

**Qué se pidió:** Resolución de inestabilidad en la paginación y validación estricta de zona horaria.

**Qué se generó / propuso:** Uso de `AwareDatetime` en Pydantic y un criterio de desempate en la ordenación (`DetectionEvent.id.desc()`) para SQLAlchemy.

**Qué se aceptó y qué se rechazó, y por qué:** Se implementó todo para asegurar que bases de datos de series temporales no tengan solapamientos silenciosos de offset.

## [2026-09-08] Módulo Analytics Ingestion

**Quién:** @FrankArmed | Frank Asael

**Herramienta:** Gemini (AI Collaborator)

**Qué se pidió:** Ayudar a corregir e implementar esquemas y configuración base del repositorio SQLAlchemy.

**Qué se generó / propuso:** Estructura de validación Pydantic para ingesta y cascarones para las pruebas mock.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó la estructura propuesta por mantener aislamiento. Se refactorizó la coerción de tipos en el router para evitar directivas `type: ignore` y cumplir el tipado estricto.

## [2026-09-08] Tercera auditoría de código: optimización YOLO y ByteTracker en el PR #21

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** GitHub Copilot (VS Code) + revisión humana como Tech Lead

**Qué se pidió:** Realizar un Code Review profundo del PR #21, correspondiente a la optimización de YOLO y ByteTracker. Se evaluó el rendimiento en procesos de larga duración y la calidad de las pruebas simuladas. El prompt utilizado fue: "Actúa como un Staff Software Engineer especialista en Computer Vision y Backend. Realiza un Code Review profundo de los 5 archivos adjuntos... Evalúa fugas de memoria, robustez de tipos y la calidad real de los mocks."

**Qué produjo la IA vs Qué detectó el Humano?:**

- **Hallazgos de la IA:** Identificó una fuga de memoria (*Memory Leak*) crítica causada por el uso de `set()` en ciclos infinitos para acumular IDs de rastreo. Además, detectó "pruebas cosméticas" que validaban la deduplicación reingresando exactamente el mismo frame simulado en lugar de usar secuencias temporales lógicas.
- **Hallazgo del Humano:** A diferencia de las revisiones anteriores, validé que la autora sí cumplió estrictamente con el *Definition of Done* al actualizar `AI_LOG.md` y `BACKLOG.md`. Utilicé esto para iniciar la revisión con refuerzo positivo antes de señalar la vulnerabilidad.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó el diagnóstico de la IA sobre la retención potencialmente ilimitada de IDs, porque relaciona una estructura de datos aparentemente inocua con el ciclo de vida real de un proceso de video 24/7 y puede provocar una caída por agotamiento de memoria (*Out-Of-Memory*, OOM). También se aceptó la observación sobre las pruebas cosméticas, ya que repetir exactamente el mismo frame no demuestra el comportamiento del tracker a través del tiempo. Se rechazó cualquier conclusión que tratara la cobertura o los linters como evidencia suficiente de seguridad operacional. El veredicto fue "Request Changes" exclusivamente por la arquitectura de memoria.

**Conclusiones Clave sobre la IA en Code Reviews:**

- La IA brilló al correlacionar estructuras de datos simples (`set`) con el ciclo de vida del sistema (stream de video 24/7), previendo una caída por *Out-Of-Memory* (OOM) que los linters y el coverage jamás detectarían.
- La revisión humana confirmó el cumplimiento documental del *Definition of Done* y permitió reconocer primero ese resultado antes de señalar la vulnerabilidad técnica. Se emitió un "Request Changes" exclusivamente por la arquitectura de memoria.

**Validación:** Se contrastó el análisis estático de Copilot con la revisión humana del *Definition of Done*, `AI_LOG.md` y `BACKLOG.md`. La auditoría confirmó que la documentación requerida estaba actualizada, pero que el diseño de los acumuladores no era adecuado para procesos indefinidos y que las pruebas no modelaban secuencias temporales representativas. El PR #21 quedó pendiente de cambios hasta establecer una política de retención de IDs y reforzar las pruebas del ciclo de vida del tracker.

## [2026-09-08] Correcciones de Peer Review

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** @aleixscarbo me hizo una review de mi PR #21, me mencionó algunas cosas que yo no sabía cómo hacerlas; realmente investigando, eran optimizaciones aún más allá de lo que yo había hecho, entonces entra como parte del feature. Mencionó lo siguiente:

- `vision/src/modules/session.py` y `counting.py` (Fuga de Memoria)
  - **Qué observaste:** Los acumuladores `track_ids_by_zone` y `tracked_people_ids` utilizan la estructura `set()` para almacenar todos los IDs únicos vistos. En un despliegue real donde la cámara procese video 24/7, estos conjuntos crecerán infinitamente cada vez que ByteTracker asigne un nuevo ID, provocando un colapso del servidor por falta de memoria RAM (Out-Of-Memory).
  - **Qué propones:** Es imperativo implementar una política de expiración. Puedes limitar la sesión a ventanas temporales (ej. reiniciar contadores cada hora y guardar el total en BD) o usar un mecanismo de TTL (Time-To-Live) para purgar de la memoria los IDs que no han sido vistos en los últimos X minutos.

- `tests/vision/test_vision.py` (Pruebas Cosméticas de Tracking)
  - **Qué observaste:** Aunque la cobertura es altísima (+95%), la prueba de `ZoneCounter` (`L178`) registra exactamente el mismo objeto dos veces para validar la deduplicación, y el mock del detector en la sesión devuelve un frame estático. Esto no prueba el comportamiento real del rastreador a través del tiempo.
  - **Qué propones:** Las pruebas de tracking necesitan movimiento. Simula al menos 3 frames consecutivos donde un ID entra a la zona, permanece, y sale de la zona, para garantizar que la lógica de retención y conteo funciona bajo carga dinámica, no solo con fotos estáticas.

Directamente envié esto a ChatGPT para que me ayudara a solucionarlo; creo que ya era bastante información.

**Qué se generó / propuso:** Únicamente corrigió lo solicitado.

**Qué se aceptó y qué se rechazó, y por qué:** Tuvo una breve alucinación, olvidó que todo esto se está llevando a cabo con videos de supermercados reales antes que con la cámara web de mi laptop y borró eso de la lógica, el buscar el path del video; entonces eliminé eso y solo dejé lo que arreglaba lo mencionado por Aleixs.

**Validación:** Probo activando el .venv y ejecutando mypy, ruff, pytest. Al terminar, me dio el resumen y lo probé yo + python -m vision.src.main para ver que la lógica funcionara igual.

## [2026-09-07] Division de main.py y runtime.py

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Generé una optimización usando ByteTracker; esto hizo que contaminara de nuevo main.py. Por cada feature o refactor, siempre terminaba ensuciando ese archivo. Entonces busqué con Gemini una forma de separar código de capas, igual que en la API. Me explicó que se podía generar un runtime.py y main.py, para que se pueda ejecutar el código de la capa de servicios en un entorno de desarrollo local. Esto permitirá que los desarrolladores puedan trabajar en el código de la capa de Servicios sin tener que ejecutar el código de la capa de Datos en un entorno de desarrollo local. Use este prompt, fue en ChatGPT, aunque la solucion fue planteada por Gemini web:

> Revisa toda la carpeta de src dentro de vision/. Quiero que veas todos los modulos y main.py, apartir de eso crea un archivo en la raiz de src llamado runtime.py para dividir capas, en ese archivo meteras todos los def que veas sean parte del entorno de desarrollo mas que modulos, por ejemplo inicializaciones.
>
> Una vez los tengas ejecuta el entorno virtual y pytest para revisar que siga siendo compatible todo el entorno con el nuevo archivo.

**Qué se generó / propuso:** Planifico mover las siguientes def:

- `get_video_source`
- `get_model_path`
- `get_tracker_path`
- `get_device`

También crear `get_runtime_config` para traer el .yml de configuración (este archivo lo da Ultralytics cuando usas ByteTrack simple), y traer toda la lógica de printeo final para dejar en el main solo el ejecutar los módulos y runtime.

**Qué se aceptó y qué se rechazó, y por qué:** Acepté todo en general, menos dejar el main solo para ejecutar todo; ahí decidí dejar toda la configuración de printeo final, esto porque esa lógica de printeo es lo que se convertirá en el contrato con la API para comunicación y eso lo quería tener en el main.py.

**Validación:** Después de que generó el plan, le mencioné la restricción de antes y también le dije que lo probara activando el .venv y ejecutando mypy, ruff, pytest. Al terminar, me dio el resumen y lo probé yo + python -m vision.src.main para ver que la lógica funcionara igual.

## [2026-09-07] Auditoría dual del módulo de Analítica en el PR #18

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** GitHub Copilot (VS Code) + revisión humana como Tech Lead

**Qué se pidió:** Realizar un Code Review profundo del PR #18, correspondiente al módulo de Analítica (`DetectionEvent`). Se aplicó un modelo de auditoría dual: revisión automatizada con IA (Copilot de VS Code) para el análisis estático y verificación humana contra el *Definition of Done* (DoD). El prompt utilizado fue: "Actúa como un Staff Software Engineer extremadamente estricto pero constructivo. Realiza un Code Review profundo de los 6 archivos adjuntos... Evalúa Pydantic, paginación en SQLAlchemy 2.0 y pruebas con MagicMock."

**Qué produjo la IA vs Qué detectó el Humano?:**

- **Hallazgos de la IA:** Detectó vulnerabilidades arquitectónicas críticas en la capa de datos. Identificó el uso de datetimes "naive" en Pydantic que corromperían las series de tiempo, y advirtió sobre una paginación inestable en SQLAlchemy al ordenar únicamente por timestamp sin un ID de desempate.
- **Hallazgo del Humano:** Actuando como Tech Lead, detecté una violación administrativa directa al *Definition of Done*. El autor modificó el `BACKLOG.md` con las nuevas User Stories, pero omitió por completo registrar el trabajo de generación de código en el `AI_LOG.md`.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó el diagnóstico técnico de la IA sobre la necesidad de imponer UTC estricto y estabilizar la paginación con un criterio de desempate, porque ambos puntos afectan la integridad de los datos y la consistencia de las consultas a gran escala. También se aceptó la conclusión de que una cobertura superior al 90% no garantiza la robustez arquitectónica del módulo. Se rechazó considerar suficiente el análisis automatizado por sí solo, porque la IA no detectó la omisión administrativa del `AI_LOG.md` frente al DoD. El resultado del Peer Review fue un veredicto de "Request Changes".

**Conclusiones Clave sobre la IA en Code Reviews (Criterio Técnico):**

- La IA es excepcional detectando antipatrones de diseño y fugas de abstracción en el código estático, pero carece del contexto administrativo para hacer cumplir las reglas del equipo (como el DoD).
- Se priorizó la integridad de las series de tiempo mediante UTC estricto y la consistencia de la paginación a gran escala, demostrando que un PR con +90% de cobertura no es inmune a fallas de arquitectura de datos.

**Validación:** Se contrastó el análisis estático de Copilot con una revisión humana del proceso de entrega y del *Definition of Done*. La auditoría confirmó que el módulo requería cambios técnicos por el manejo de fechas y la paginación, y que además existía una deuda documental no identificada por la IA. Por estos motivos, el PR #18 quedó con veredicto de "Request Changes" hasta corregir ambos tipos de hallazgos.

## [2026-09-05] Resolución de Peer Review: defensa de la arquitectura de Stores

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** GitHub Copilot

**Qué se pidió:** Atender el feedback de la Project Lead, Anna, durante el Peer Review sobre la ausencia de una capa de Servicios en el CRUD de Stores. La observación planteaba que el flujo debería incluir una separación explícita entre router, servicio y repositorio antes de continuar ampliando la funcionalidad de la API.

**Qué se generó / propuso:** Se analizó la responsabilidad actual de cada capa. El router se encarga de HTTP, dependencias, códigos de estado y transformación mediante esquemas; Pydantic valida la entrada del cliente; y `StoreRepository` concentra las operaciones de persistencia con SQLAlchemy. Bajo el alcance actual, las operaciones de Stores son un CRUD directo sin reglas de negocio, orquestación, transacciones compuestas ni integraciones externas que requieran una capa intermedia.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó mantener temporalmente la arquitectura sin una capa de Servicios, aplicando YAGNI. Crear ahora un servicio que únicamente recibiera parámetros del router y llamara al repositorio produciría un Servicio Anémico o *pass-through service*: añadiría archivos, abstracciones y puntos de mantenimiento sin encapsular una decisión de negocio real. La decisión no descarta la capa para siempre; queda condicionada a que aparezcan reglas de negocio, coordinación entre repositorios, validaciones que excedan el esquema de entrada, autorización, transacciones complejas o integraciones externas. Se rechazó introducir una capa únicamente por simetría arquitectónica o por anticipar necesidades que todavía no existen, porque aumentaría la complejidad sin aportar comportamiento.

**Validación:** Se revisó el flujo completo del CRUD y se comprobó que las responsabilidades actuales están delimitadas: `StoreCreate` bloquea payloads inválidos, el router traduce la ausencia de recursos a `404` y el repositorio ejecuta la persistencia. La defensa queda respaldada por YAGNI, separación de responsabilidades y el principio de mantener las abstracciones justificadas por comportamiento real. La decisión podrá revisarse cuando el dominio de Stores deje de ser un CRUD puro.

## [2026-09-05] Corrección de desviación del backlog: actualización parcial de Stores con TDD

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** GitHub Copilot

**Qué se pidió:** Corregir una desviación detectada durante el Peer Review: la User Story original de Stores no incluía la actualización parcial exigida por `docs/agile/BACKLOG.md`, donde se define `PATCH /stores/{store_id}` como parte del CRUD. Se asumió la deuda técnica y se completó el flujo mediante TDD estricto, avanzando de RED a GREEN sin modificar el alcance hacia una capa de Servicios innecesaria.

**Qué se generó / propuso:** Primero se añadió la prueba unitaria `test_store_repository_updates_store` en `tests/api/test_store_repo.py`. La prueba construye un `MagicMock` para la sesión, configura una tienda existente y exige que `StoreRepository.update` cambie el nombre, haga `commit`, ejecute `refresh` y retorne la misma instancia. Como el método aún no existía, el estado RED quedó representado por un `AttributeError`.

Después se añadió la prueba de router `test_update_store_endpoint` en `tests/api/test_stores_router.py`. Esta prueba inyecta un repositorio simulado mediante `app.dependency_overrides[get_store_repository]`, envía `PATCH /stores/1` con `{"name": "Nombre Nuevo"}` y espera `200 OK` con el nombre actualizado. Antes de registrar la ruta, el estado RED del endpoint quedó representado por `405 Method Not Allowed`.

Para llegar a GREEN se implementó `StoreRepository.update(store_id, name)` con SQLAlchemy 2.0: búsqueda mediante `self.session.get(StoreModel, store_id)`, retorno `None` cuando no existe, actualización de `name`, `commit`, `refresh` y retorno de la entidad. Después se incorporó en FastAPI `@router.patch("/{store_id}", response_model=StoreResponse)`, reutilizando `StoreCreate`, `get_store_repository` y el mismo contrato de `404 Store not found` usado por el borrado lógico.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó implementar la actualización como una operación parcial limitada al atributo `name`, porque es el contrato definido por la historia actual y evita introducir campos no solicitados. Se mantuvo la inyección mediante la función exacta `get_store_repository` para que los overrides de las pruebas representen el flujo real de FastAPI. También se aceptó reutilizar `StoreCreate` como payload porque el esquema ya valida el nombre antes de llegar al router o al repositorio.

Se rechazó modificar el router de producción durante la fase RED, porque habría ocultado el fallo que debía demostrar la prueba. También se rechazó agregar una capa de Servicios como parte de esta corrección: el caso sigue siendo un CRUD directo y no contiene reglas de negocio que justifiquen un servicio. Finalmente, no se introdujo un `PUT` ni una actualización de campos adicionales, ya que habría desviado la implementación del requisito de `PATCH` del backlog.

**Validación:** La secuencia TDD cubrió primero el fallo por `AttributeError` del repositorio y el `405 Method Not Allowed` del router, y después la implementación mínima necesaria para convertir ambos escenarios en GREEN. La prueba del repositorio verifica el cambio de estado y las operaciones de sesión; la prueba del router verifica la inyección del mock, el contrato HTTP `200` y la serialización del nombre actualizado. El flujo final conserva el manejo de `404` cuando la tienda no existe y mantiene intactas las operaciones existentes de creación, listado y borrado lógico.

## [2026-09-02] Fase de setup y corrección de IA para CRUD de Stores

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** Gemini (TeachLead) + GitHub Copilot

**Qué se pidió:** Desarrollar el CRUD inicial para tiendas siguiendo el flujo TDD de Red-Green-Refactor. Se pidió generar pruebas para repositorio y endpoints de `stores`, así como implementar `POST /stores` y `GET /stores` con inyección de dependencias realista. Durante esta fase, la IA generó una solución de FastAPI incorrecta en la que la dependencia se construía con `Depends(session=None)`, ignorando los mocks y rompiendo el comportamiento esperado de las pruebas.

**Qué se generó / propuso:** Se generaron pruebas unitarias para repositorio y router, junto con una primera versión del CRUD de tiendas. El problema apareció cuando la inyección de dependencias se apuntó a la clase `StoreRepository` o a un valor por defecto nulo, en lugar de a la función real `get_store_repository`, lo que hacía que FastAPI no usara la instancia mockeada y provocara un `AttributeError` antes de llegar a la lógica funcional.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó corregir la inyección usando `app.dependency_overrides[get_store_repository] = lambda: mock_repo`, garantizando que FastAPI inyectara la dependency function exacta que estaba siendo mockeada. Se rechazó el enfoque de `Depends(session=None)` y cualquier variante que ocultara el mock porque no reflejaba el flujo real del sistema y hacía que la prueba fallara por un problema de infraestructura en vez de por el comportamiento que se quería validar. Esta corrección fue crítica para mantener la metodología TDD sin false negatives artificiales.

**Validación:** Se ejecutaron las pruebas de repositorio y router de tiendas con `pytest` para comprobar que la creación y listado de tiendas funcionaban correctamente bajo la inyección controlada. La validación demostró que el problema no estaba en el dominio de la lógica sino en el acoplamiento de dependencias, y que el flujo de FastAPI quedaba estable una vez ajustada la dependencia exacta.

## [2026-09-02] Fase de refactorización de linter para dependencias con Annotated

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** Gemini (TeachLead) + GitHub Copilot

**Qué se pidió:** Refactorizar la inyección de dependencias del router para evitar la advertencia `B008` de Ruff provocada por llamar funciones en valores por defecto dentro de `Depends()`. La IA había generado un estilo que funcionaba, pero violaba la recomendación moderna de dependencia tipada y limpia para FastAPI.

**Qué se generó / propuso:** Se propuso y aplicó el patrón `Annotated` para las dependencias del router, dejando la firma de `get_store_repository` como `session: Annotated[Session, Depends(get_db)]` y los parámetros de las rutas como `repo: Annotated[StoreRepository, Depends(get_store_repository)]`. Este enfoque permite mantener una resolución limpia de dependencias, una tipificación fuerte y una compatibilidad mejor con linters y validadores modernos.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó esta refactorización porque elimina la llamada directa de funciones en valores por defecto y alinea el código con el estándar recomendado por FastAPI y Ruff. Se rechazó la solución anterior porque, aunque era funcional, no era la forma esperada por la herramienta de análisis estático y añadía ruido técnico no necesario. Este ajuste mejoró la calidad del código sin cambiar la semántica de la API.

**Validación:** Se comprobó visualmente la estructura del router y se validó que la sintaxis y el patrón de dependencias eran correctos. La corrección completó la fase de limpieza técnica sin comprometer la funcionalidad del CRUD ni la capacidad de testear con mocks y overrides de dependencias.

## [2026-09-02] Fase de arquitectura: Soft Delete y validación con Pydantic para Stores

**Quién:** @aleixscarbo | Aleixs Carbonell

**Herramienta:** Gemini (TeachLead) + GitHub Copilot

**Qué se pidió:** Implementar la lógica de borrado lógico para tiendas y documentar la arquitectura de negocio asociada. La intención era evitar eliminaciones físicas que pudieran romper integridad referencial, especialmente en un sistema que podría escalar con cámaras, zonas y analíticas ligadas a cada tienda. Además, se buscaba validar la entrada del modelo con Pydantic para bloquear peticiones sin nombre antes de llegar al router.

**Qué se generó / propuso:** Se implementó `soft_delete(self, store_id: int) -> StoreModel | None` dentro de `StoreRepository`, con la secuencia `self.session.get(StoreModel, store_id)`, cambio de `is_active` a `False`, `self.session.commit()` y `self.session.refresh(store)`. Al mismo tiempo, se definió el esquema `StoreCreate` con validación de `name` y se dejó que Pydantic manejara la coerción y el rechazo antes de cualquier lógica del endpoint. El escenario de validación quedó cubierto por una prueba que envía `POST /stores` con payload vacío y espera `422`.

**Qué se aceptó y qué se rechazó, y por qué:** Se aceptó la decisión de usar borrado lógico en SQLAlchemy para mantener la integridad referencial y el historial de las tiendas. Se rechazó la eliminación física por defecto porque rompe la consistencia del modelo y obliga a tratar datos eliminados como registros huérfanos. También se aceptó delegar la validación de entrada a `Pydantic` porque cumple con el principio SRP: el router no debe validar nombres, y el sistema bloquea inmediatamente peticiones malformadas con un 422 antes de llegar al repositorio o a la base de datos. Este was not only cleaner, but more robust and easier to test.

**Validación:** Se verificó que `soft_delete_store` cambiaba `is_active` a `False` y devolvía `200 OK`, mientras que el escenario sin nombre devolvía `422` sin necesidad de mocks del repositorio. La validación mostró que la solución de arquitectura era coherente con el dominio y con las buenas prácticas de FastAPI, SQLAlchemy y Pydantic.

## [2026-09-02] Ejecución de módulos

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Simple, ejecutar lo que encontró en el prompt anterior.

> Dejame ayudarte con algunos puntos.
>
> 1. En el primero tienes razon, justo es lo que pense al crearlo, son 300 lineas de codigo para un modulo, pensaba que era mucho. Con respecto a esto no quiero tantos directorios, divideme el archivo en 4 modulos, `detection.py`, `counting.py`, `visualization.py` y `session.py`.
> 2. Aqui mencionas que es mejor upgradear mi zonecounter por otra forma y dejar el terreno listo para bytetracker, lo cual es correcto pero no es el punto de esta revision, lo voy a guardar y lo ejecutare como ADR cuando llegue el momento. por ahora dejalo asi por que ahora mismo funciona, vamos por pasos.
> 3. No entendi este punto, repitelo con mas cuidado y mejor explicacion.
> 4. Lo se, recuerda que el workflow es: generamos un modelo visual, con cv2.show para fines practicos, una vez eso funcione lo pasamos a un modelo headless
> 5. No es importante
>
> Sabiendo esto, haras lo siguiente:
>
> - Generaras los archivos que mencione en el punto 1 (`detection.py`, `counting.py`, `visualization.py` y `session.py`.) para dividir responsabilidades
> - Explicaras el punto 3
> - Una vez tengas todo funcional lo validaras con pytest-cov, para esto iniciaras el .venv, por que ahi esta instalado todo.

**Qué se generó / propuso:** Primero que nada, me explicó el punto 3. Hablaba acerca de un error de hardcodeo en una función que tenía; no es un problema en este momento, pero podría escalar al momento de hacer el contrato con la API (realmente, primero edito, luego explico, pero esto es en el resumen).

Posteriormente, genero los archivos que mencioné en el punto 1 (`detection.py`, `counting.py`, `visualization.py` y `session.py`.) para dividir responsabilidades.

Al final, cuando intentó ejecutar pytest, se dio cuenta de que los directorios de sus tests habían quedado obsoletos y los actualizó a los nuevos módulos.

**Qué se aceptó y qué se rechazó, y por qué:** Conforme iba creando, iba revisando; tengo la opción de generación más estricta que permite Codex. Todo lo acepté; no hizo más que cortar y pegar código en nuevos archivos .py y cambiar paths.

**Validación:** Primero, él comentó que su pytest, ruff y mypy pasaron bien, pytest con 99.44% de cobertura. Luego verifiqué y efectivamente pasa así y, por último, ejecuté `python -m vision.src.main` y corrió como antes del refactor.

## [2026-09-02] Revisión de nuevos módulos para YOLO

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Después de hacer varios "frankestains" para los módulos, necesitaba una revisión que validara que implementé todo correctamente, no por pytest o linters, sino por la infraestructura del código y su legibilidad. Use este prompt:

> Hice un gran feature para la parte de vision del proyecto. Mira, genere `modules` dentro de `vision/src/`, este parte todas las responsabilidades en modulos para que funcione el modelo de YOLO, agregue zonas ROI y deteccion de personas basico, no tiene ByteTrack ni nada, solo cuenta por frame (ineficiente pero util).
>
> Necesito que revises archivo por archivo si se cumple lo de dividir modulo o si hay algun modulo que hace mas de una cosa y que podria ser mas legible partirlos en 2, 3, etc. Que tenga logica.
>
> Auxi es un modulo extra, ese no lo toques. Es una copia y pega de uno que tenia y lo usare proximamente.
>
> Al final entregame un resumen de lo encontrado.

**Qué se generó / propuso:** 5 puntos, resumidamente fueron estos:

1. Mi archivo `detection.py`, lo que llamo mi "frankestain", efectivamente tenía mucha información; específicamente, hallo 5 módulos que podían ser repartidos entre más`.py` para mejorar la arquitectura de código.
2. Mencionó que una clase mía llamada `ZoneCounter` detectaba personas por frame, lo cual es ineficiente; lo mejor es dejar el terreno listo para un posible ByteTrack.
3. Un punto que no entendí (le pedí explicarlo después).
4. Interfaz incompatible. Me recalcó que el contenedor descarga headless y estoy usando cv2.show.
5. Errores mínimos de tipado o de semántica.

**Qué se aceptó y qué se rechazó, y por qué:** Acepté 1 de los 5 puntos, el no. 1, los demás, no los perdí de vista; los anoté para futuros refactors o features.

**Validación:** Aquí fue solo lectura, después son los prompts importantes.

## [2026-09-01] Ayuda con unittest.mock en los test de US 3 y 4

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Estoy intentando comprender unittest.mock; sin embargo, no termino de acertar en todas las pruebas; muchas me tiran error. En este punto necesitaba terminar; llevaba un día entero sin avanzar + otras actividades. Use este prompt:

> Dentro de `tests/vision/` genere alrededor de 14 test para empezar a programar los nuevos modulos. Me estoy frustando mucho por unittest.mock, la idea de los test ya esta plasmada, algunos ya no me tiran error, pero hay otros (en especial el ultimo) que no termino de arreglar. Integra bien esta libreria a los test que la necesiten, los test estan generados a base de BACKLOG.md, en la US 3 y 4.

**Qué se generó / propuso:** Genero el típico plan que siempre me hace de qué test va a cambiar.

**Qué se aceptó y qué se rechazó, y por qué:** Sinceramente, no rechacé nada, tampoco me di a la amplia tarea de revisar la ejecución. Simplemente, que no hubiera errores o warnings; me di por servida.

**Validación:** No encontrar errores o warnings, después de agregar la lógica, será ejecutar pytest y revisar.

## [2026-08-31] Generación de un ejemplo de test para visión

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** El primer código de YOLO es un código copia y pega de un código pasado que yo tenía. Sin embargo, el flujo correcto debe ser generar test -> generar código. Yo no sé generar un test para probar modelos de YOLO. Solicité que generara uno para probar `vision/src/main.py` y que lo explicara. Se uso este prompt:

> Me recomiendas hacer test para la parte de vision? Es que anteriormente hice para probar APIs pero nunca vi como se hacen para probar YOLO.
>
> Dame un ejemplo que pruebe mi `vision/src/main.py`y explicamelo en tu resumen.

**Qué se generó / propuso:** Generó el código dentro de `test_vision.py`, usando `unittest.mock`, una librería que evito usar durante todo SensorHub, ya que nunca la entendí. Posteriormente, le comenté esto mismo, y me dijo para qué sirve dicha librería y que sin ella estaríamos en una situación complicada para generar test de YOLO.

**Qué se aceptó y qué se rechazó, y por qué:** N/A

**Validación:** Ejecutar `pytest` o `pytest vision` y ver que pase, asi mismo investigar de que se trata `unittest.mock`.

## [2026-08-30] Redacción de BACKLOG.md

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Redactar el archivo BACKLOG.md con la información proporcionada. Se uso este prompt:

> Acabo de crear `docs/agile/BACKLOG.md` en este archivo metere las cosas que pienso que debe llevar la API para completar el cometido que quiero para RetaiLO. Tengo aqui los endpoitns que quisiera ver, agregalos de forma profesional, estructurada y explicada al documento.
>
> - Stores
>   - CRUD completo para registrar tiendas nuevas: estructura minima recomendada:
>     - POST /stores
>     - GET /stores
>     - GET /stores/{store\_id}
>     - PUT o PATCH /stores/{store\_id}
>     - DELETE /stores/{store\_id}
>
> - Body: posiblemente solo el nombre es necesario, agreguenle lo que crean es necesario.
>
> - Cameras
>
>   - CRUD completo para registrar camaras dentro de una tienda preregistrada: estructura minima recomendada:
>
>     - POST /stores/{store\_id}/cameras
>     - GET /stores/{store\_id}/cameras
>     - GET /cameras/{camera\_id}
>     - PUT o PATCH /cameras/{camera\_id}
>     - DELETE /cameras/{camera\_id}
> - Body:
>
> ```json
> {
>   "name": "Cámara principal",
>   "source_type": "demo_video"
> }
> ```
>
> - Tipos: demo\_video
>
> - Zones:
>   - CRUD completo para registrar zonas por medio de puntos especificos, se sacan usando una interfaz interactiva: estructura minima recomendada:
>
>     - POST /cameras/{camera\_id}/zones
>     - GET /cameras/{camera\_id}/zones
>     - GET /zones/{zone\_id}
>     - PUT o PATCH /zones/{zone\_id}
>     - DELETE /zones/{zone\_id}
>
> - Body:
>
> ```json
> {
>   "name": "Refrigeradores",
>   "zone_type": "product_area",
>   "points": [
>        {"x": 120, "y": 80},
>        {"x": 430, "y": 85},
>        {"x": 450, "y": 300},
>        {"x": 110, "y": 295}
>    ]
> }
> ```
>
> - Tipos: fridges, clean products...
>
> - Video\_results
>   - De nuevo, un Append-Only que sirve solo para la demostracion, no para producto real, muestra el resultado de una session, aqui no tengo una estructura minima recomendada, pero posiblemente contenga un resume de frames procesados, personas detectadas, tiempo transcurrido, metricas por zona, etc.
>
> - Analytics
>   - Get-Only, este si es producto real: estructura minima recomendada:
>     - GET /stores/{store\_id}/analytics/summary
>     - GET /stores/{store\_id}/analytics/traffic
>     - GET /stores/{store\_id}/analytics/insights
>
> - Body recomendado en insigts:
>
> ```json
> {
>   "type": "HIGH_TRAFFIC_LOW_SALES",
>   "zone_id": "zone_001",
>   "zone_name": "Fridges",
>   "message": "La zona Refrigeradores concentra 42% de las visitas, pero los productos ubicados en esa zona representan solo 18% de las ventas.",
>   "suggestion": "Revisar disponibilidad, precio, promociones o acomodo de productos."
> }
>
> ```
>
> - Recommendations
>   - Esta es una opcional si se ve util, puede ir dentro de Analytics, pero podria concentrar una forma de registro automatico por cada session analizada.
>
> Para simular las ventas deberia haber como minimo un endpoint mas, como este es solo demo y no tiene literalmente nada que ver con el producto, dejo completamente a consideracion del desarrollador la forma de implementarlo, solo no debe ser muy complejo ni llevar mas del 10% del tiempo de desarrollo. Lo mismo pasa para un posible dashboard frontend, este si es 100% opcional dependiendo de la carga de trabajo de los desarrolladores de la API.
>
>Por la parte del desarrollo de la vision artificial, las peticiones son mas simples, literalmente la camara debe poder correr ligero, poder correr en CUDA, poder detectar y contar, poder correr en videos, poder mandar informacion a la API, es decir es mas sencillo, el desarrollo de la inteligencia de vision es mas orientado a que haga esto bien mas que a cuantas funcionalidades tiene, igual arreglalo profesionalmente, recuerda que es un trabajo paralelo.

**Qué se generó / propuso:** Redacto en forma de tablas los endpoints que mencioné para ser legibles, y mantener los feats por una escala de P0 a P2, donde P0 son los más importantes. Con esto genero la redacción. Sin embargo, ya nada más le cambié al archivo las escalas por unas MoSCoW, sus iniciales, y retiré algunos textos que notaba innecesarios, al final agregue una seccion para User Stories y una plantilla recomendada.

**Qué se aceptó y qué se rechazó, y por qué:** N/A

**Validación:** Lectura del texto generado.

## [2026-08-29] Revision del repositorio

**Quién:** @LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** Analizar y aclarar si mi estructura de Docker era correcta para empezar a trabajar; usé este prompt:

> El repositorio actual esta creado para albergar un nuevo proyecto llamado RetaiLO Analytics, en el README.md puedes encontrar mas informacion de que se trata este proyecto. El dia de ayer inicie generando una estructura de repositorio basica para poder comenzar a trabajar, sin embargo no estoy del todo segura si es correcta esta distribucion, te explico cual fue mi vision, ahora mismo quiero aclarar la parte de Docker:
>El proyecto se divide en 2 pilares sumamente importantes, app/ que es donde vivira la API REST y vision/ que es donde vivira toda la logica de la parte de vision artificial. Dada la estructura y la orientacion del proyecto propuse 2 Dokerfile, uno para la API REST que esta ira a produccion y otro para el servicio de vision que esta no ira a produccion, solo tendra su contenedor para facilitar que corra en todas las maquinas, esto es correcto o hay una mejor forma de hacerlo? En caso de que si sea la mejor forma, tambien revisa el contenido en el Dockerfile de API que es el que ya rellene y generame uno para la parte de vision.
>Tambien revisa el docker-compose.yml y el .dockerignore que van de la mano con la parte de dockers del proyecto

**Qué se generó / propuso:** Confirmo que la estructura es posiblemente la mejor, al menos para empezar. Me propuso lo siguiente:

1. Conservar `app/Dockerfile` modificando el contexto de build.
2. Crear `vision/Dockerfile`.
3. Separar dependencias y meterlas en `requirements/`.
4. Ajustar `docker-compose.yml` para agregar vision.
5. Corregir `.dockerignore`

**Qué se aceptó y qué se rechazó, y por qué:** Lo único que rechacé fue el crear `requirements/` y meter las dependencias ahí. Antes de que generara nada, le comenté que me parecía mejor dividirlo en un requirements en `app/` para el Dockerfile que tenga solo lo que es necesario para el contenedor, otro en `vision/` que tenga igual, lo necesario nada más, y el que está en la carpeta madre que tenga lo que debe descargar uno como desarrollador.

**Validación:** Revisé archivo por archivo; en los `Dockerfiles` y en el `docker-compose.yml` me parece que hizo un excelente trabajo, es legible y cumple con lo que mencionaba; lo mismo pasa con los `requirements.txt` aunque aquí le faltaron algunas librerías como NumPy, que yo uso para trabajar en visión artificial. Intentaré trabajar solo con las que puso, esperando que sea un flujo más eficiente.

El único lugar donde podría argumentar que falló fue en `.dockerignore` porque no puso ningún tipo de orden, solo escribió cosas; aproveché eso para borrarlo y copiar y pegar lo que tenía en SensorHub.
