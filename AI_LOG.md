# Bitácora de uso de IA

Documentación de la interacción con inteligencia artificial generativa utilizada como asistencia para el desarrollo del proyecto.

> Regla de oro: Se puede usar libremente IA, con la condición de registrar criterio, validación y qué se aceptó/rechazó y por qué.

El orden de registro es ascendente. En la parte superior estará el registro más reciente. No es necesario registrar interacciones triviales como autocompletados, breves preguntas, etc.

---

## [2026-08-31] Generacion de un ejemplo de test para vision

**Quién:** LaMunuwa | Anna Valentina

**Herramienta:** ChatGPT

**Qué se pidió:** El primer código de YOLO es un código copia y pega de un código pasado que yo tenía. Sin embargo, el flujo correcto debe ser generar test -> generar código. Yo no sé generar un test para probar modelos de YOLO. Solicité que generara uno para probar `vision/src/main.py` y que lo explicara. Se uso este prompt:

> Me recomiendas hacer test para la parte de vision? Es que anteriormente hice para probar APIs pero nunca vi como se hacen para probar YOLO.
>
> Dame un ejemplo que pruebe mi `vision/src/main.py`y explicamelo en tu resumen.

**Qué se generó / propuso:** Generó el código dentro de `test_vision.py`, usando `unittest.mock`, una librería que evito usar durante todo SensorHub, ya que nunca la entendí. Posteriormente, le comenté esto mismo, y me dijo para qué sirve dicha librería y que sin ella estaríamos en una situación complicada para generar test de YOLO.

**Qué se aceptó y qué se rechazó, y por qué:** N/A

**Validación:** Ejecutar `pytest` o `pytest vision` y ver que pase, asi mismo investigar de que se trata `unittest.mock`.

## [2026-08-30] Redaccion de BACKLOG.md

**Quién:** LaMunuwa | Anna Valentina

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

**Quién:** LaMunuwa | Anna Valentina

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
