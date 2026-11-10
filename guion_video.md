# Guion Técnico de Sustentación Oral — NexusAI 2.0
## Actividad 4: Tejiendo Redes — Arquitectura de Software entre Hilos y Nodos

- **Duración total estimada:** 13 minutos y 30 segundos (Rango oficial exigido: 12 a 15 minutos).
- **Modalidad:** Grabación de pantalla con cámara activa de los expositores, subida a YouTube en modo «No listado».
- **Expositores y Roles:**
  - **[JC] Juan Carlos Benítez Rojas:** Líder de Proyecto y Arquitecto de Software.
  - **[JJ] Juan José Córdoba Eraso:** Desarrollador Principal y Evaluador de Calidad.

---

## 🛠️ Preparación Técnica Previa a la Grabación (Checklist de 5 Minutos)

Antes de presionar el botón de grabar, ambos expositores deben verificar:
1. **Entorno del Clúster:** Abrir una terminal en `Actividad4_Tejiendo_Redes/prototipo` y arrancar el clúster:
   ```bash
   python run_cluster.py --workers 3 --threads 16 --worker-threads 4
   ```
2. **Tablero de Control:** Abrir `http://127.0.0.1:8088/dashboard.html` en el navegador principal a pantalla completa o media pantalla.
3. **Segunda Terminal:** Dejar abierta y lista una segunda ventana de consola en la carpeta `prototipo/` para lanzar las cargas y el caos.
4. **Documentos de Soporte:** Tener abierto el PDF del informe en las páginas de los tres diagramas UML y las gráficas comparativas.
5. **Cero Distracciones:** Silenciar notificaciones del sistema operativo y cerrar programas pesados en segundo plano para evitar contención de CPU durante los benchmarks en vivo.

---

## ⏱️ Cronograma de Intervención por Bloques

| Bloque | Intervalo | Duración | Responsable | Tema Central |
|---|:---:|:---:|:---:|---|
| **Bloque 1** | 00:00 – 01:15 | 1:15 | JC y JJ | Apertura, presentación y contexto de NexusAI 2.0 |
| **Bloque 2** | 01:15 – 03:45 | 2:30 | JC | Modelado UML formal (Componentes, Secuencia y Despliegue) |
| **Bloque 3** | 03:45 – 05:15 | 1:30 | JC | Justificación teórica de los 9 patrones de diseño |
| **Bloque 4** | 05:15 – 07:00 | 1:45 | JJ | Arquitectura de código y 4 niveles de concurrencia |
| **Bloque 5** | 07:00 – 10:15 | 3:15 | JJ | Demostración en vivo: caso nominal y 4 escenarios de caos |
| **Bloque 6** | 10:15 – 12:15 | 2:00 | JJ y JC | Resultados cuantitativos y 5 ajustes arquitectónicos empíricos |
| **Bloque 7** | 12:15 – 13:30 | 1:15 | JC y JJ | Conclusiones, revisión de entregables y cierre |

---

## 🎬 GUION DIALOGADO VERBÁTIM

---

### BLOQUE 1 · Apertura y Contextualización del Proyecto (00:00 – 01:15)

**[EN PANTALLA: Portada formal del informe en PDF mostrando título, curso, docente y nombres de los integrantes. Cámaras de ambos expositores activas en la esquina superior].**

**[00:00] JUAN CARLOS:**
> «Un cordial saludo a la profesora Leidy Johana Polo y a nuestros compañeros. Mi nombre es Juan Carlos Benítez Rojas, líder de proyecto y arquitecto de software de esta entrega.»

**[00:13] JUAN JOSÉ:**
> «Y mi nombre es Juan José Córdoba Eraso, desarrollador principal y evaluador de calidad del equipo.»

**[00:20] JUAN CARLOS:**
> «Hoy sustentamos la Actividad 4: *Tejiendo redes: Arquitectura de software entre hilos y nodos*. En la Actividad 2 diseñamos conceptualmente la plataforma **NexusAI**, concebida para la orquestación inteligente de flujos cognitivos empresariales. Aquel diseño definió una visión cloud-native sólida, pero descansaba sobre un prototipo simulado en el navegador. 
> 
> El objetivo y el desafío que asumimos en esta cuarta actividad fue categórico: llevar a NexusAI de los diagramas conceptuales a una **red física distribuida real**, compuesta por procesos independientes, hilos de ejecución concurrentes, servidores HTTP nativos y un bus de eventos persistente. En los próximos doce minutos demostraremos cómo nuestra arquitectura escala de forma casi lineal y sostiene el cien por ciento de disponibilidad ante fallas severas de infraestructura.»

---

### BLOQUE 2 · Modelado Arquitectónico UML Formal (01:15 – 03:45)

**[EN PANTALLA: Transición fluida a la Figura 1 del informe: Diagrama de Componentes en alta resolución].**

**[01:15] JUAN CARLOS:**
> «Iniciamos con el modelado formal del sistema, desarrollado bajo el enfoque de diagramas como código con PlantUML. Diseñamos con exactitud un diagrama por cada una de las tres perspectivas requeridas.
> 
> En pantalla observamos el **Diagrama de Componentes**. La arquitectura se estructura en cuatro capas desacopladas mediante inversión de dependencias:
> 1. En la cúspide encontramos a los clientes omnicanal y el tablero de telemetría.
> 2. La capa de coordinación alberga el API Gateway y el orquestador de la Saga. Este componente centraliza el enrutamiento inteligente, gestiona un pool de despacho dedicado y consulta tanto al balanceador de carga como al registro de Circuit Breakers.
> 3. La capa de cómputo está conformada por nodos trabajadores idénticos y autónomos (`w1`, `w2` y `w3`), cada uno encapsulando los servicios cognitivos de *Triage*, *RAG* y *Compliance* tras una interfaz REST uniforme.
> 4. Finalmente, la capa de persistencia la constituye el Event Broker, encargado de auditar de manera asíncrona cada transición de estado en disco. 
> 
> Lo crucial aquí es que las dependencias son estrictamente descendentes: los trabajadores ignoran quién los invoca y no conocen a sus pares, lo que permite añadir o remover nodos en caliente sin alterar al coordinador.»

**[EN PANTALLA: Transición a la Figura 2: Diagrama de Secuencia de la Saga con interacción de hilos].**

**[02:15] JUAN CARLOS:**
> «Pasamos al **Diagrama de Secuencia**. A diferencia de diagramas convencionales que solo ilustran llamadas de red, este modelo desagrega explícitamente la interacción entre **nodos e hilos**.
> 
> Como se aprecia, cuando el cliente envía una petición POST al gateway, este toma un hilo libre del pool de despacho (identificados como hilos T1 a T8). Este hilo despacha la etapa de clasificación hacia el trabajador 1, que a su vez activa un hilo de su pool local (W1). El flujo nominal progresa hacia la etapa de recuperación RAG en el trabajador 2.
> 
> Sin embargo, el diagrama modela intencionalmente el escenario más complejo: en la etapa de cumplimiento normativo, el trabajador 3 detecta que la confianza semántica viola las políticas de seguridad. En lugar de reintentar inútilmente una falla de negocio, el orquestador inicia la **compensación inversa de la Saga**: primero revierte el contexto de RAG y luego la clasificación inicial. El cliente recibe una respuesta controlada con código HTTP 409 Conflict, asegurando que ninguna transacción quede en un estado inconsistente a medias.»

**[EN PANTALLA: Transición a la Figura 3: Diagrama de Despliegue en red física y mapeo a Docker].**

**[03:05] JUAN CARLOS:**
> «Cerramos el modelado con el **Diagrama de Despliegue**. Representa la topología de red física: seis procesos de sistema operativo independientes comunicándose sobre la interfaz de red local en puertos dedicados: el coordinador en el puerto 8080, el broker en el 8090, los tres nodos de cómputo en los puertos 8101, 8102 y 8103, y el tablero web en el 8088.
> 
> El diagrama incluye además la correspondencia directa hacia una red bridge en contenedores Docker, demostrando que el desacoplamiento por sockets garantiza portabilidad inmediata hacia entornos orquestados como Kubernetes.»

---

### BLOQUE 3 · Selección y Justificación Teórica de Patrones de Diseño (03:45 – 05:15)

**[EN PANTALLA: Tabla 6 del informe: Síntesis de correspondencia entre problemas y patrones].**

**[03:45] JUAN CARLOS:**
> «Para resolver los desafíos de concurrencia y tolerancia a fallos, seleccionamos y articulamos **nueve patrones de diseño canónicos**, justificando cada uno desde la literatura de ingeniería de software:
> 
> 1. **Saga Orquestada:** Resuelve la consistencia distribuida sin recurrir a bloqueos pesados de dos fases (2PC), garantizando atomicidad mediante compensación reversa (Garcia-Molina & Salem, 1987).
> 2. **Broker de Mensajería:** Desacopla temporalmente a productores y consumidores mediante colas asíncronas con persistencia en bitácora (Hohpe & Woolf, 2003).
> 3. **Mediator:** Centraliza la topología en el coordinador, evitando dependencias punto a punto cuadráticas entre nodos (Gamma et al., 1994).
> 4. **Proxy y API Gateway:** Provee un punto de acceso único, validación de esquemas y traducción unificada de estados a códigos HTTP (Fowler, 2014; Newman, 2021).
> 5. **Circuit Breaker:** Previene fallos en cascada aislando nodos degradados tras tres fallos sucesivos en una máquina de estados Closed, Open y Half-Open (Nygard, 2018).
> 6. **Bulkhead:** Confinamiento estanco de recursos; implementamos mamparos tanto en el despacho del gateway como en pools de hilos locales por cada trabajador (Nygard, 2018).
> 7. **Observer Distribuido:** Notificación desacoplada de telemetría y eventos hacia el tablero y el auditor (Gamma et al., 1994).
> 8. **Strategy:** Permite intercambiar dinámicamente algoritmos de balanceo entre Round-Robin y Least-Connections sin alterar la lógica de negocio (Gamma et al., 1994).
> 9. **Retry Selectivo:** Reintenta automáticamente perturbaciones transitorias de red, distinguiendo formalmente entre caídas de nodo y rechazos de negocio (Sommerville, 2016).
> 
> Ahora le cedo la palabra a Juan José, quien nos guiará a través del código y la ejecución del prototipo.»

---

### BLOQUE 4 · Arquitectura del Código y Modelo de Concurrencia (05:15 – 07:00)

**[EN PANTALLA: Editor de código VS Code / OpenCode mostrando la estructura de carpetas en `prototipo/` y el archivo `coordinator.py`].**

**[05:15] JUAN JOSÉ:**
> «Muchas gracias, Juan Carlos. Como desarrollador del clúster, una de las principales decisiones de implementación fue construir NexusAI 2.0 utilizando **exclusivamente la biblioteca estándar de Python 3.14**. Prescindimos de frameworks web externos para demostrar que los principios de sistemas distribuidos —sockets TCP, manejo de concurrencia e hilos— pueden materializarse de forma transparente y determinista.
> 
> La solución se organiza en nueve módulos limpios: `coordinator.py` para el gateway y la orquestación, `worker.py` para los nodos de cómputo, `broker.py` para la mensajería y la bitácora JSONL, `cluster.py` para el control de ciclo de vida de procesos, junto a nuestras suites de carga y caos en `load_test.py` y `chaos_test.py`.»

**[EN PANTALLA: Fragmento de código de `worker.py` resaltando `ThreadPoolExecutor(max_workers=4)` y luego `coordinator.py` con `ThreadPoolExecutor(max_workers=16)`].**

**[05:55] JUAN JOSÉ:**
> «El núcleo del sistema reside en su **modelo jerárquico de concurrencia**, articulado en cuatro niveles:
> 
> - **Primero, aislamiento a nivel de proceso:** Cada nodo corre en un proceso independiente del sistema operativo. Si un trabajador experimenta una fuga de memoria o un error crítico, no puede corromper el espacio de memoria del coordinador ni de los otros nodos.
> - **Segundo, servidores HTTP multihilo:** Utilizamos la clase `ThreadingHTTPServer`, que delega cada conexión socket entrante a un hilo efímero, garantizando que el socket principal nunca se bloquee al recibir tráfico.
> - **Tercero, pool de despacho en el coordinador:** Limitado a dieciséis hilos concurrentes. Este mamparo regula el flujo de entrada y previene la saturación del host ante avalanchas de peticiones.
> - **Cuarto, mamparos de cómputo en trabajadores:** Cada trabajador confina sus ejecuciones a un pool estricto de cuatro hilos. Esto significa que con tres nodos activos, el clúster ofrece una capacidad instantánea de doce tareas simultáneas.
> 
> Todas las estructuras compartidas —como los contadores de métricas y los disyuntores— están protegidas por candados `threading.Lock` reentrantes de grano fino, manteniendo las secciones críticas por debajo de los diez microsegundos.»

---

### BLOQUE 5 · Demostración en Vivo: Flujo Nominal y Batería de Caos (07:00 – 10:15)

**[EN PANTALLA: Disposición en pantalla dividida: a la izquierda, la terminal de comandos de Windows; a la derecha, el navegador web con `dashboard.html` en vivo].**

**[07:00] JUAN JOSÉ:**
> «Pasemos a la demostración en vivo. En pantalla tenemos a la derecha nuestro tablero de observabilidad en tiempo real, conectado a los endpoints de telemetría del coordinador y del broker. 
> 
> Vamos a emitir una ráfaga nominal de 120 transacciones con una concurrencia cliente de 24 hilos utilizando `load_test.py`».

**[ACCIÓN: Juan José ejecuta en la terminal: `python load_test.py --tasks 120 --concurrency 24 --label demo_nominal`].**

**[07:25] JUAN JOSÉ:**
> «Observen el comportamiento: la consola reporta una tasa superior a **26 transacciones por segundo** y un percentil 95 de solo **1 033 milisegundos**. En el tablero, el contador de tareas completadas llega a 120, cero errores de sistema, la profundidad de la cola del broker se mantiene en cero porque los eventos se drenan continuamente hacia el archivo JSONL, y los tres Circuit Breakers permanecen en estado verde `CLOSED`.
> 
> Ahora someteremos la arquitectura a fallos reales mediante nuestra herramienta de caos.»

#### Demostración de Caos 1: Nodo Lento (+300 ms de latencia)
**[ACCIÓN: En terminal ejecuta: `python chaos_test.py latency --worker http://127.0.0.1:8102 --ms 300` y lanza una carga: `python load_test.py --tasks 120 --concurrency 24 --label demo_lento`].**

**[08:00] JUAN JOSÉ:**
> «Inyectamos 300 milisegundos de latencia artificial en el trabajador 2. El clúster no falla, pero se degrada: el throughput desciende a 8,8 rps y el p95 sube a 4 128 ms. ¿Por qué? Porque bajo la estrategia Round-Robin, un tercio de las peticiones queda atascada en el nodo lento, reteniendo los hilos de despacho del coordinador. Este hallazgo empírico fue fundamental y más adelante explicaremos cómo lo solucionamos.»

#### Demostración de Caos 2: Nodo Defectuoso y Apertura de Circuit Breaker
**[ACCIÓN: En terminal ejecuta: `python chaos_test.py fail --worker http://127.0.0.1:8102 --rate 1.0` y lanza la carga: `python load_test.py --tasks 120 --concurrency 24 --label demo_breaker`].**

**[08:35] JUAN JOSÉ:**
> «Ahora configuramos al nodo 2 para que falle el 100 % de sus peticiones. Miren el tablero: inmediatamente tras el tercer fallo consecutivo, el indicador de `w2` cambia a rojo en estado **OPEN**. 
> 
> Gracias al patrón Retry y Circuit Breaker, el coordinador deja de enrutar tráfico a ese nodo y desvía la carga hacia los nodos sanos 1 y 3. El resultado en consola es contundente: **100 % de transacciones completadas con éxito y cero errores de usuario** a 17,8 rps.»

#### Demostración de Caos 3: Rechazo de Guardrail y Compensación Saga
**[ACCIÓN: Ejecuta: `python chaos_test.py reset` y luego: `python chaos_test.py guardrail --url http://127.0.0.1:8080 --tasks 120 --rate 0.25`].**

**[09:10] JUAN JOSÉ:**
> «Restablecemos el clúster e inyectamos un 25 % de rechazos por políticas de seguridad en la etapa de cumplimiento. Miren la columna de compensaciones en el tablero: 31 transacciones fueron rechazadas y compensadas. El orquestador ejecutó la reversión en orden inverso, liberando el contexto de RAG y la clasificación, retornando al cliente un código HTTP 409 con trazabilidad auditable. La disponibilidad fue del 100 %: una compensación no es una falla de software, es una respuesta controlada de negocio.»

#### Demostración de Caos 4: Caída Total de Nodo y Reinserción Elástica
**[ACCIÓN: Ejecuta: `python chaos_test.py stop --worker http://127.0.0.1:8103` y corre la carga: `python load_test.py --tasks 120 --concurrency 24 --label demo_caida`].**

**[09:45] JUAN JOSÉ:**
> «Finalmente, provocamos la caída física total del trabajador 3, matando su proceso. La capacidad cae a dos nodos, pero el clúster procesa las 120 transacciones sin una sola caída del servicio. Al reiniciar el proceso de `w3` en una consola secundaria, el Circuit Breaker entra en estado **HALF-OPEN**, valida una petición de prueba y retorna automáticamente a **CLOSED**, recuperando el caudal nominal de inmediato.»

---

### BLOQUE 6 · Evaluación Cuantitativa y los 5 Ajustes Empíricos (10:15 – 12:15)

**[EN PANTALLA: Tabla 8 y Figuras 4 y 5 del informe: Curvas de Throughput, Speedup y Latencia por cantidad de nodos].**

**[10:15] JUAN JOSÉ:**
> «La experimentación no se limitó a demostraciones cualitativas: registramos métricas consolidadas sobre una batería de 1 200 transacciones.
> 
> En escalabilidad horizontal, los resultados evidencian un comportamiento casi lineal:
> - Con un nodo obtuvimos un throughput de 9,24 rps con un p95 de 3 185 ms.
> - Al duplicar a dos nodos, el throughput subió a 18,14 rps, un speedup de 1,96× y 98,2 % de eficiencia.
> - Al triplicar a tres nodos, alcanzamos **26,74 transacciones por segundo**, un speedup de **2,89×** y una eficiencia del **96,5 %**, reduciendo el p95 a solo **1 043 ms** (tres veces más rápido).»

**[EN PANTALLA: Tabla 10 y Figura 8 del informe: Comparativa entre Round-Robin y Least-Connections].**

**[10:55] JUAN CARLOS:**
> «Y lo más valioso del proyecto fueron los **cinco ajustes arquitectónicos** que descubrimos y aplicamos a partir de las mediciones:
> 
> 1. **Resolución de Red en Windows:** En las pruebas iniciales, el sistema tardaba 8 500 ms por transacción. Descubrimos que usar el nombre `localhost` forzaba una resolución IPv6 fallida con timeout antes de pasar a IPv4. Cambiar estrictamente a `127.0.0.1` abatió la latencia por llamada de 2 042 ms a 2,15 ms: una aceleración brutal de **951 veces**.
> 2. **Balanceo Adaptativo Least-Connections:** Como vimos en la demo, un nodo lento colapsa el balanceo Round-Robin. Implementamos la estrategia *Least-Connections*: al dirigir el tráfico hacia las instancias desocupadas, el throughput bajo el mismo nodo lento saltó de 8,99 a **20,59 rps** (un 129 % más de caudal) y retuvo el 75,7 % de la capacidad del clúster.
> 3. **Contrapresión en el Broker:** Acotamos la cola del broker a 10 000 elementos con descarte del mensaje más antiguo (*drop oldest*) e integramos un hilo consumidor dedicado, logrando auditar 9 735 eventos con una cola residual en cero.
> 4. **Tipificación de Errores en Contratos:** Diferenciamos en las respuestas JSON los errores de infraestructura de los errores de negocio (`kind: "business" | "node"`), evitando reintentos inútiles cuando una regla semántica rechaza la solicitud.
> 5. **Dimensionamiento de Pools:** Elevamos el pool de despacho del gateway de 8 a 16 hilos, garantizando una sobre-suscripción balanceada frente a los doce slots de cómputo de los tres trabajadores.»

---

### BLOQUE 7 · Conclusiones, Repositorio y Cierre (12:15 – 13:30)

**[EN PANTALLA: Navegador web mostrando el repositorio en GitHub `Alboguaci/tejiendo-redes-nexusai`, bajando por el README.md y mostrando los commits].**

**[12:15] JUAN CARLOS:**
> «Llegamos a las conclusiones finales del proyecto:
> - Primero, confirmamos que la arquitectura de software no es un ejercicio estático de dibujo: la concurrencia, las colas y la propagación de fallos son propiedades físicas emergentes que solo se comprenden cuando el software se somete a carga en red.
> - Segundo, la articulación de patrones como Saga, Circuit Breaker, Bulkhead y balanceo consciente de carga demostró ser indispensable para garantizar la disponibilidad absoluta y la integridad de los datos empresariales.
> - Como trabajo futuro, proyectamos desacoplar el estado de la Saga hacia una base de datos distribuida con replicación Raft para tolerar la caída catastrófica del propio coordinador.»

**[12:55] JUAN JOSÉ:**
> «Toda la solución se encuentra completamente versionada y disponible en nuestro repositorio público de GitHub: `Alboguaci/tejiendo-redes-nexusai`. El repositorio incluye el código fuente, los diagramas PlantUML, los resultados JSON, las gráficas vectoriales y el informe técnico consolidado de 51 páginas bajo normas APA 7ma Edición. Cualquier evaluador puede clonar el proyecto y reproducir idénticamente los resultados ejecutando una única línea de comandos.»

**[13:18] JUAN CARLOS:**
> «Agradecemos a la profesora Leidy Johana Polo por su guía durante la unidad y por impulsarnos a construir prototipos con rigor de ingeniería. Muchas gracias por su atención y quedamos atentos a sus preguntas y retroalimentación.»

**[EN PANTALLA: Placa final de créditos con nombres, programa de Ingeniería de Software, Tecnológica del Oriente y fecha: 11 de noviembre de 2026. Fin de la grabación].**

---

## 📋 Consejos de Grabación para los Expositores

1. **Ritmo de Voz:** Mantener un tono dinámico, pausado y seguro. Evitar leer de forma mecánica; interioricen las ideas centrales de cada párrafo.
2. **Coordinación de Pantalla:** Mientras Juan José ejecuta los comandos en la consola, Juan Carlos puede ir comentando los efectos en el diagrama o en el código, demostrando sinergia y trabajo colaborativo real.
3. **Cuidado con el Zoom:** En la terminal y en el editor de código, aumenten la fuente con `Ctrl + +` para que las instrucciones, puertos y latencias sean perfectamente legibles en el video final a 1080p.
4. **Visibilidad en YouTube:** Al subir el video, seleccionar obligatoriamente **«No listado» (Unlisted)** para que no sea público en búsquedas pero la docente pueda calificarlo sin requerir permisos especiales.
