# ADR-001: Estructura modular del repositorio

- **Estado:** Aceptado
- **Fecha:** 2026-09-15
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

RetaiLO reúne varias responsabilidades con necesidades diferentes: la API administra la lógica del producto, el módulo de Vision procesa video y detecciones, y el frontend consume la API para presentar la experiencia web. Mantener todas estas responsabilidades mezcladas en una única estructura dificultaría trabajar y evolucionar cada parte de forma independiente.

## Decisión

Organizar el repositorio en módulos separados: `app` para la API, `vision` para el procesamiento de video y `frontend` para la interfaz web. La aplicación debe mantenerse excluida de las responsabilidades específicas de Vision y del frontend, conservando una estructura limpia y enfocada.

## Opciones Consideradas

- Mantener API, procesamiento de video e interfaz web dentro de un único módulo.
- Separar únicamente la API y dejar Vision y frontend dentro de ella.
- Dividir el repositorio en los módulos independientes `app`, `vision` y `frontend`.

## Consecuencias

**Positivas (Beneficios):**

- Cada módulo puede evolucionar con sus propias dependencias y responsabilidades.
- La API queda más limpia y aislada del procesamiento pesado de Vision.
- El frontend tiene una ubicación y un ciclo de trabajo independientes.
- La separación facilita identificar qué componente debe modificarse en cada cambio.

**Negativas (Riesgos / Deuda técnica asumida):**

- Hay que mantener contratos claros entre API, Vision y frontend.
- La configuración, las dependencias y el despliegue deben coordinarse entre varios módulos.
- Pueden aparecer duplicaciones de configuración o lógica de integración.
