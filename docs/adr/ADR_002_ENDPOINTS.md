# ADR-002: Organización de endpoints por dominio funcional

- **Estado:** Aceptado
- **Fecha:** 2026-09-15
- **Autores:** Anna Valentina (LaMunuwa)

## Contexto

RetaiLO está pensado para crecer como producto. La API necesita representar la estructura operativa de una tienda: registrar tiendas, asociar cámaras y configurar zonas dentro de cada cámara. Para la demo también debe permitir crear sesiones de procesamiento, guardar resultados y consultar analíticas. Además, el frontend necesitó autenticación para registrar usuarios, iniciar sesión y administrar la sesión actual.

La plataforma también contempla recomendaciones derivadas de las analíticas y del procesamiento de YOLO. Se consideró entrenar un modelo local sencillo, posiblemente con regresión lineal, para apoyar esa parte, pero todavía no se ha definido cómo integrarlo.

## Decisión

Exponer endpoints separados por dominio funcional: autenticación, tiendas, cámaras, sesiones, zonas, resultados, analíticas, ventas, recomendaciones y health check. Las relaciones principales se expresan mediante rutas anidadas, por ejemplo, cámaras de una tienda, zonas de una cámara, sesiones de una cámara y resultados de una sesión.

La API también mantiene endpoints específicos para consultar analíticas de una tienda, generar y actualizar recomendaciones, e ingerir eventos de detección. La posible integración de un modelo local queda como una evolución futura y no forma parte de la decisión actual.

## Opciones Consideradas

- Concentrar toda la funcionalidad en pocos endpoints genéricos.
- Crear endpoints únicamente para la demo actual y posponer la separación por dominios.
- Organizar los endpoints por recursos y relaciones del dominio, dejando espacio para ampliar analíticas y recomendaciones.

## Consecuencias

**Positivas (Beneficios):**

- La API refleja el flujo del producto desde la tienda hasta las recomendaciones.
- Cada recurso tiene operaciones de creación, consulta y actualización donde aplica.
- La estructura facilita que el frontend consuma capacidades concretas.
- Se puede ampliar el producto sin convertir un único endpoint en un punto de acoplamiento excesivo.

**Negativas (Riesgos / Deuda técnica asumida):**

- Aumenta la cantidad de rutas que deben documentarse, probarse y mantenerse.
- Las relaciones entre recursos requieren validaciones y coordinación entre endpoints.
- La integración futura de un modelo de machine learning todavía carece de un contrato técnico definido.
