# ADR-004: Comunicación HTTP entre frontend, API y Vision

- **Estado:** Aceptado
- **Fecha:** 2026-09-15
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

RetaiLO está dividido en un frontend, una API y un módulo de Vision que ejecuta el procesamiento de video con YOLO. Estos componentes tienen responsabilidades distintas y necesitan comunicarse sin compartir directamente la lógica interna de los demás.

La API está implementada con FastAPI. El frontend se sirve mediante nginx y el módulo de Vision se ejecuta como un servicio separado dentro de Docker Compose. Por ello, el contrato HTTP es el punto de integración entre los tres componentes.

## Decisión

Usar la API como punto central de comunicación. El frontend y Vision se comunican con ella mediante HTTP y consumen sus recursos a través de rutas y esquemas definidos por FastAPI. El frontend no se comunica directamente con Vision ni con YOLO.

### Frontend y API

El frontend realiza solicitudes con `fetch` usando rutas relativas bajo `/api`. El nginx del contenedor frontend sirve los archivos estáticos y reenvía las solicitudes que comienzan con `/api/` al servicio `api:8000`, eliminando el prefijo `/api` al aplicar `proxy_pass`.

El cliente del frontend usa la API para registrar y consultar tiendas, cámaras, zonas, sesiones, resultados de video, analíticas y recomendaciones. Para autenticación, usa `/api/auth`, guarda el `access_token` recibido y envía el token en el encabezado `Authorization: Bearer` para consultar el usuario actual, cambiar la contraseña y cerrar sesión.

### Vision y API

Vision usa `RetailoAnalyticsClient`, un cliente Python basado en `requests`. La URL base se configura mediante `API_BASE_URL`; en Docker Compose toma por defecto `http://api:8000`, por lo que el contenedor Vision se comunica directamente con el servicio de API en la red interna.

El flujo de procesamiento es el siguiente:

1. Vision consulta las zonas activas de una cámara mediante `GET /cameras/{camera_id}/zones`.
2. Vision crea una sesión mediante `POST /cameras/{camera_id}/sessions` y recibe el `session_id`.
3. YOLO procesa localmente el video y Vision transforma los conteos por zona en métricas asociadas a los identificadores recibidos de la API.
4. Al finalizar correctamente, Vision publica el resultado agregado mediante `POST /sessions/{session_id}/video-results`.
5. Si el procesamiento falla o no se pueden publicar los resultados, Vision actualiza la sesión mediante `PATCH /sessions/{session_id}` con estado `failed`. Cuando el resultado se publica correctamente, la API guarda el resultado y cambia internamente la sesión a estado `completed`.

El resultado enviado incluye frames procesados, tiempo transcurrido, personas detectadas, fechas de inicio y fin, y métricas por zona. La API valida que los `zone_id` correspondan a la cámara de la sesión y que las métricas cumplan las reglas del esquema.

La API también ofrece consultas de resultados, analíticas, ventas y recomendaciones para que el frontend pueda mostrar la información procesada. No existe una comunicación directa documentada entre el navegador y el contenedor Vision.

FastAPI genera el esquema OpenAPI y expone documentación interactiva en `/docs`; la ruta raíz redirige a esa documentación. Los esquemas de entrada y salida, junto con los códigos HTTP, forman el contrato compartido por los clientes.

## Opciones Consideradas

- Hacer que el frontend se comunique directamente con Vision y que Vision escriba directamente en la base de datos.
- Mantener un punto de comunicación distinto para cada módulo, duplicando contratos y lógica de integración.
- Usar la API como punto central y permitir que frontend y Vision intercambien datos mediante HTTP y esquemas FastAPI.

## Consecuencias

**Positivas (Beneficios):**

- La API centraliza la persistencia y las reglas del dominio; frontend y Vision no necesitan acceder directamente a la base de datos.
- El frontend puede consumir datos de tiendas, procesamiento, analíticas y recomendaciones usando el mismo contrato HTTP.
- Vision puede ejecutar YOLO localmente y publicar únicamente el estado y los resultados agregados que la API necesita.
- El uso de `API_BASE_URL` permite que Vision apunte al servicio correcto según se ejecute localmente o dentro de Docker Compose.
- OpenAPI y los esquemas FastAPI hacen visible el contrato que deben respetar ambos clientes.

**Negativas (Riesgos / Deuda técnica asumida):**

- La API es un punto central de disponibilidad: si no responde, el frontend y Vision no pueden completar sus operaciones HTTP.
- Los cambios en rutas o esquemas pueden romper al frontend y al cliente de Vision al mismo tiempo.
- La comunicación actual de Vision está orientada al flujo de sesiones y resultados agregados; no se observa un canal HTTP para transmitir video desde el frontend hacia Vision.
- La autenticación Bearer está implementada en el cliente del frontend, mientras que el cliente de Vision mostrado no envía ese token en sus solicitudes.
