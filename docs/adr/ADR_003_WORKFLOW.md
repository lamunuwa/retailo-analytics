# ADR-003: Un archivo Docker y de dependencias por módulo

- **Estado:** Aceptado
- **Fecha:** 2026-09-15
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

En SensorHub, el producto anterior a RetaiLO, se trabajaba con un único `Dockerfile` y un único `requirements.txt` en la carpeta raíz. RetaiLO reúne módulos con perfiles muy distintos: la API, el frontend y Vision. En particular, YOLO y las dependencias del procesamiento de video hacen que la imagen de Vision sea considerablemente más pesada que las imágenes necesarias para la API o el frontend.

## Decisión

Mantener un `Dockerfile` y un archivo de dependencias por módulo. La API, el frontend y Vision se construyen y ejecutan con sus propias configuraciones, separando la imagen pesada de YOLO de las imágenes de la API y del frontend.

## Opciones Consideradas

- Continuar con un único `Dockerfile` y un único archivo de dependencias para todo el repositorio.
- Construir una imagen común que incluya también YOLO, la API y el frontend.
- Mantener imágenes y dependencias separadas por módulo.

## Consecuencias

**Positivas (Beneficios):**

- La imagen de la API no carga las dependencias pesadas de YOLO.
- El frontend no queda acoplado al entorno de Python y Vision.
- Cada módulo puede actualizar sus dependencias sin hacer crecer innecesariamente las demás imágenes.
- Se facilita optimizar y desplegar cada componente según sus necesidades.

**Negativas (Riesgos / Deuda técnica asumida):**

- Se deben mantener varios archivos de construcción y de dependencias.
- Las versiones compartidas entre módulos pueden desalinearse si no se controlan.
- El despliegue requiere coordinar más de una imagen y sus relaciones de ejecución.
