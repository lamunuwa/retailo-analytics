# Bitácora de uso de IA

Documentación de la interacción con inteligencia artificial generativa utilizada como asistencia para el desarrollo del proyecto.

> Regla de oro: Se puede usar libremente IA, con la condición de registrar criterio, validación y qué se aceptó/rechazó y por qué.

El orden de registro es ascendente. En la parte superior estará el registro más reciente. No es necesario registrar interacciones triviales como autocompletados, breves preguntas, etc.

---

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

---
