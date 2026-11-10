# Guion Técnico de Sustentación Oral (17 Minutos) — NexusAI 2.0
## Actividad 4: Tejiendo Redes — Arquitectura de Software entre Hilos y Nodos

- **Duración total:** 17 minutos exactos (1 020 segundos) distribuidos en 22 intervenciones.
- **Rango por intervención:** Entre 30 y 50 segundos por turno (rotación dinámica tipo diálogo técnico).
- **Expositores y Roles:**
  - **[JC] Juan Carlos Benítez Rojas:** Líder de Proyecto y Arquitecto de Software (11 intervenciones).
  - **[JJ] Juan José Córdoba Eraso:** Desarrollador Principal y Evaluador de Calidad (11 intervenciones).
- **Formato de Entrega:** Video con cámaras activas y pantalla compartida, subido a YouTube en modo «No listado».

---

## 🛠️ Checklist Técnico Previo a la Grabación (5 Minutos)

1. **Terminal 1 (Clúster):** `cd prototipo && python run_cluster.py --workers 3 --threads 16 --worker-threads 4`.
2. **Navegador Web:** `http://127.0.0.1:8088/dashboard.html` en pantalla completa.
3. **Terminal 2 (Carga y Caos):** Lista para ejecutar `load_test.py` y `chaos_test.py`.
4. **Visor de PDF:** Abierto en el archivo `Informe_Actividad4_Tejiendo_Redes.pdf` en los diagramas UML.
5. **Resolución y Legibilidad:** Aumentar el zoom de consola (Ctrl + +) para garantizar calidad 1080p.

---

## ⏱️ Tabla Resumen de Intervenciones (17:00 Exactos)

| Turno | Intervalo | Duración | Expositor | Rol Asignado | Tema Principal |
|:---:|:---:|:---:|---|---|---|
| **01** | 00:00 – 00:45 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Portada formal del informe en PDF mostrando título, unidad, docente y nombres de los integrantes. Cámaras de ambos expositores activas. |
| **02** | 00:45 – 01:30 | 45 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Diagrama de bloques general o animación introductoria del pipeline cognitivo (Triage, RAG, Compliance). |
| **03** | 01:30 – 02:15 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Diagrama de Componentes |
| **04** | 02:15 – 03:00 | 45 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Diagrama de Componentes |
| **05** | 03:00 – 03:50 | 50 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Diagrama de Secuencia |
| **06** | 03:50 – 04:35 | 45 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Diagrama de Secuencia |
| **07** | 04:35 – 05:20 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Diagrama de Despliegue |
| **08** | 05:20 – 06:10 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Tabla 6 del informe |
| **09** | 06:10 – 07:00 | 50 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Tabla 6 del informe |
| **10** | 07:00 – 07:45 | 45 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Tabla 6 del informe |
| **11** | 07:45 – 08:30 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Estructura de archivos en el editor de código mostrando la carpeta `prototipo/` y sus 9 módulos. |
| **12** | 08:30 – 09:20 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Fragmentos de código en `coordinator.py` y `worker.py` mostrando ThreadPoolExecutor y threading.Lock. |
| **13** | 09:20 – 10:05 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Pantalla dividida |
| **14** | 10:05 – 10:55 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Terminal ejecutando `python load_test.py --tasks 120 --concurrency 24 --label demo_nominal` y el dashboard actualizando gráficas. |
| **15** | 10:55 – 11:40 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Terminal inyectando latencia en w2 |
| **16** | 11:40 – 12:30 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Terminal inyectando fallo 100% en w2 |
| **17** | 12:30 – 13:15 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Terminal ejecutando prueba de guardrails |
| **18** | 13:15 – 14:05 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Terminal matando proceso de w3 (`chaos_test.py stop`), corriendo carga y luego reiniciando w3. |
| **19** | 14:05 – 14:55 | 50 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Figuras 4 y 5 del informe |
| **20** | 14:55 – 15:45 | 50 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Figura 8 del informe y Tabla 10 |
| **21** | 15:45 – 16:30 | 45 seg | **JC (Juan Carlos)** | Líder de Proyecto y Arquitecto de Software | Tabla 11 del informe |
| **22** | 16:30 – 17:00 | 30 seg | **JJ (Juan José)** | Desarrollador Principal y Evaluador de Calidad | Repositorio en GitHub `Alboguaci/tejiendo-redes-nexusai` mostrando el informe PDF de 50 páginas y placa de créditos finales. |

---

## 🎬 Guion Dialogado Verbátim

### TURNO 01 (00:00 – 00:45 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Portada formal del informe en PDF mostrando título, unidad, docente y nombres de los integrantes. Cámaras de ambos expositores activas.
* **Acción / Gesto:** Saludo formal a cámara, postura firme y presentación del equipo.

> «Un cordial saludo a la profesora Leidy Johana Polo y a nuestros compañeros. Mi nombre es Juan Carlos Benítez Rojas, líder de proyecto y arquitecto de software de esta entrega, y junto a mi compañero Juan José Córdoba Eraso presentamos la sustentación de la Actividad 4: Tejiendo redes: Arquitectura de software entre hilos y nodos. En la Actividad 2 planteamos la arquitectura conceptual de NexusAI, una plataforma orientada a microservicios cognitivos. El objetivo central que asumimos en esta entrega fue llevar esa arquitectura de los diagramas conceptuales a una red física distribuida real, con procesos independientes, hilos concurrentes y comunicación por red verificable.»

---

### TURNO 02 (00:45 – 01:30 · 45 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Diagrama de bloques general o animación introductoria del pipeline cognitivo (Triage, RAG, Compliance).
* **Acción / Gesto:** Contacto visual a cámara, tono técnico explicativo.

> «Así es, Juan Carlos. En sistemas distribuidos, la red es intrínsecamente impredecible, falible y con latencia variable. Nuestro dominio resuelve el procesamiento de solicitudes omnicanal a través de un pipeline cognitivo estructurado en tres fases: clasificación rápida de intención o triage, recuperación de contexto semántico aumentado mediante RAG, y validación estricta de políticas corporativas y compliance. Para demostrar que esta arquitectura es escalable y resiliente, decidimos descartar cualquier simulación estética en navegador y construir un clúster físico operativo en Python que mida con rigor científico la concurrencia entre hilos y nodos.»

---

### TURNO 03 (01:30 – 02:15 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Figura 1 del informe: Diagrama de Componentes de NexusAI 2.0 en PlantUML (capa cliente y capa de coordinación).
* **Acción / Gesto:** Señalar con el cursor el API Gateway y el orquestador de la Saga.

> «Comenzamos con el modelado formal del sistema, realizado en PlantUML bajo el principio de diagramas como código. En pantalla observamos el Diagrama de Componentes. La arquitectura se desacopla en cuatro niveles siguiendo el principio de inversión de dependencias. En la capa superior tenemos al cliente concurrente y el tablero web de observabilidad. Inmediatamente debajo se ubica el coordinador en el puerto 8080, que alberga el API Gateway y el orquestador de la Saga. Este componente mantiene la máquina de estados, administra un pool de despacho de dieciséis hilos para regular la admisión de tráfico y consulta al balanceador de carga y disyuntores de circuito.»

---

### TURNO 04 (02:15 – 03:00 · 45 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Figura 1 del informe: foco en los Nodos Trabajadores (w1, w2, w3) y el Event Broker en el puerto 8090.
* **Acción / Gesto:** Resaltar las interfaces REST y el flujo asíncrono hacia el broker.

> «En la parte inferior del diagrama encontramos los tres nodos trabajadores autónomos, operando en los puertos 8101, 8102 y 8103. Cada trabajador expone los servicios de Triage, RAG y Compliance tras un contrato REST homogéneo, ejecutando cada tarea en un pool privado de cuatro hilos. Lo fundamental es que los nodos desconocen la topología general y no guardan estado conversacional compartido. A su lado, el Event Broker en el puerto 8090 desacopla la auditoría: recibe eventos de forma asíncrona y los drena secuencialmente a una bitácora JSONL inmutable en disco, asegurando que la persistencia nunca bloquee la respuesta al cliente.»

---

### TURNO 05 (03:00 – 03:50 · 50 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Figura 2 del informe: Diagrama de Secuencia de la Saga (interacción de hilos T1-T8 y W1-W3 en camino feliz).
* **Acción / Gesto:** Trazar con el cursor las líneas de vida de los hilos de despacho y cómputo.

> «El segundo modelo es el Diagrama de Secuencia, diseñado específicamente para evidenciar la interacción temporal entre hilos y nodos. Como pueden apreciar en las líneas de vida, distinguimos formalmente el pool de despacho del coordinador —representado por los hilos T1 a T8— y los pools locales de cada trabajador —con sus hilos W1 a W3—. Cuando una petición POST ingresa al gateway, se reserva un hilo de despacho que emite el evento saga.started al broker e invoca al trabajador 1. El trabajador asigna un hilo interno, procesa la clasificación y retorna el control. La secuencia progresa luego hacia el trabajador 2 para la recuperación de contexto RAG, orquestando la sincronización sin retención ociosa de recursos de cómputo.»

---

### TURNO 06 (03:50 – 04:35 · 45 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Figura 2 del informe: foco en la rama inferior del diagrama (rechazo de compliance y compensación inversa).
* **Acción / Gesto:** Señalar las flechas rojas de reversión de RAG y Triage hasta el código HTTP 409.

> «Pero el diagrama modela intencionalmente la situación más crítica: en la etapa de compliance, el trabajador 3 detecta que la confianza semántica cae bajo el umbral ético de 0,90 y emite un rechazo de negocio. El orquestador reconoce que reintentar una violación de reglas es inútil y activa la compensación inversa de la Saga: primero envía una petición de compensación a RAG para liberar el contexto en caché y luego compensa Triage. Finalmente, emite saga.rolled_back y devuelve al cliente un código HTTP 409 Conflict con trazabilidad total. Se preserva así la consistencia eventual sin dejar registros inconsistentes.»

---

### TURNO 07 (04:35 – 05:20 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Figura 3 del informe: Diagrama de Despliegue en red física local y caja de equivalencia con Docker bridge.
* **Acción / Gesto:** Mostrar los puertos locales y la topología de red.

> «El tercer pilar es el Diagrama de Despliegue, que mapea la topología física y de red. Se especifican seis procesos autónomos en el sistema operativo: el cliente de pruebas, el nodo coordinador en el puerto 8080, el broker en el 8090, los tres trabajadores de cómputo en los puertos 8101, 8102 y 8103, y el servidor estático del dashboard en el 8088. Todos se comunican sobre TCP/IP local mediante HTTP estándar. El diagrama incluye la correspondencia con una red bridge de contenedores Docker, confirmando que la arquitectura desacoplada por puertos permite migrar a contenedores sin modificar una sola línea de código.»

---

### TURNO 08 (05:20 – 06:10 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Tabla 6 del informe: justificación teórica y empírica de patrones (Saga y Broker).
* **Acción / Gesto:** Resaltar las referencias bibliográficas canónicas en la tabla.

> «Entramos en la justificación de patrones de diseño. Cada patrón responde a un problema de distribución con sustento en la literatura. Primero, la Saga Orquestada, propuesta por Garcia-Molina y Salem en 1987. La elegimos porque el protocolo de confirmación en dos fases (2PC) generaría bloqueos devastadores en servicios cognitivos con tiempos variables; la orquestación centralizada nos da visibilidad total y orden inverso en compensaciones. Segundo, el Broker de Mensajería, documentado por Hohpe y Woolf. Centraliza los eventos en tópicos desacoplados con contrapresión, impidiendo que una sobrecarga en la auditoría degrade el tiempo de respuesta del pipeline principal.»

---

### TURNO 09 (06:10 – 07:00 · 50 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Tabla 6 del informe: foco en Mediator, API Gateway y Circuit Breaker.
* **Acción / Gesto:** Explicar la máquina de 3 estados del Circuit Breaker.

> «Tercero, el patrón Mediator de Gamma et al., que recae en el coordinador para que los trabajadores no se conozcan entre sí, evitando dependencias cruzadas cuadráticas. Cuarto, el Proxy y API Gateway, según Fowler y Newman, que expone una fachada REST unificada, oculta la granularidad interna y traduce estados de negocio a códigos HTTP estándar. Quinto, el disyuntor Circuit Breaker, formulado por Michael Nygard. Implementamos una máquina de tres estados: CLOSED durante la operación normal, OPEN tras tres fallos consecutivos aislando el nodo durante cinco segundos de enfriamiento, y HALF-OPEN para probar si la instancia se recuperó antes de reintegrarla.»

---

### TURNO 10 (07:00 – 07:45 · 45 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Tabla 6 del informe: foco en Bulkhead, Observer, Strategy y Retry.
* **Acción / Gesto:** Señalar la flexibilidad de intercambiar estrategias de balanceo.

> «Completamos con cuatro patrones adicionales: Bulkhead, que aísla hilos en compartimentos estancos para que la saturación de un trabajador no hunda al clúster; Observer Distribuido, que difunde eventos desde el broker hacia el dashboard en tiempo real; Strategy, que encapsula los algoritmos de balanceo Round-Robin y Least-Connections tras una interfaz intercambiable en caliente; y Retry Selectivo, que reintenta perturbaciones transitorias exclusivamente ante fallas de infraestructura, evitando reintentar errores de negocio. En total son nueve patrones articulados.»

---

### TURNO 11 (07:45 – 08:30 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Estructura de archivos en el editor de código mostrando la carpeta `prototipo/` y sus 9 módulos.
* **Acción / Gesto:** Desplegar el árbol de directorios y abrir `cluster.py`.

> «Hablemos de la implementación del prototipo. El proyecto se desarrolló en Python 3.14 utilizando estrictamente la biblioteca estándar, lo que asegura total reproducibilidad en cualquier máquina sin instalar paquetes de terceros. La solución se descompone en nueve módulos de alta cohesión: common.py contiene estructuras de datos y el disyuntor; coordinator.py aloja el gateway y la orquestación; worker.py implementa los nodos de cómputo; broker.py la mensajería asíncrona; cluster.py gobierna el ciclo de vida de los subprocesos; y las suites de prueba residen en load_test.py y chaos_test.py. Ahora Juan José explicará cómo se traduce esto en concurrencia real.»

---

### TURNO 12 (08:30 – 09:20 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Fragmentos de código en `coordinator.py` y `worker.py` mostrando ThreadPoolExecutor y threading.Lock.
* **Acción / Gesto:** Resaltar los tamaños de pool: 16 hilos en gateway y 4 hilos por worker.

> «El sistema gestiona la concurrencia física en cuatro niveles coordinados: primero, procesos autónomos con espacio de memoria aislado; segundo, servidores ThreadingHTTPServer que atienden cada socket en un hilo efímero; tercero, un pool de despacho en el coordinador de dieciséis hilos que acota la tasa de entrada; y cuarto, un pool de cómputo de cuatro hilos por cada trabajador. Esto nos brinda una capacidad simultánea de doce slots de trabajo en tres nodos. Para sincronizar contadores y estados de circuitos sin crear cuellos de botella, utilizamos candados threading.Lock de grano fino, manteniendo las secciones críticas por debajo de los diez microsegundos. Veamos esto en ejecución.»

---

### TURNO 13 (09:20 – 10:05 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Pantalla dividida: terminal a la izquierda ejecutando `python run_cluster.py` y navegador web a la derecha con `dashboard.html`.
* **Acción / Gesto:** Lanzar el comando de arranque del clúster y mostrar cómo el dashboard detecta los nodos en verde.

> «Iniciamos la demostración en vivo. En la terminal izquierda ejecutamos el comando run_cluster.py configurando tres trabajadores y dieciséis hilos. El script lanza los seis subprocesos y sondea los endpoints de salud /health. En cuanto se abren los sockets, el dashboard operacional que vemos a la derecha detecta inmediatamente al coordinador, al broker y a los tres trabajadores en estado óptimo. El tablero reporta en tiempo real el throughput, percentiles de latencia, circuitos y la cola de eventos. Juan José procederá a inyectar la carga de trabajo.»

---

### TURNO 14 (10:05 – 10:55 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Terminal ejecutando `python load_test.py --tasks 120 --concurrency 24 --label demo_nominal` y el dashboard actualizando gráficas.
* **Acción / Gesto:** Ejecutar la carga y señalar las métricas en consola y en el dashboard.

> «Lanzamos una ráfaga nominal de 120 transacciones con una concurrencia cliente de 24 hilos mediante load_test.py. Observen la consola: el clúster alcanza un throughput superior a 26 transacciones por segundo con un percentil 95 de solo 1 033 milisegundos. En el dashboard, el contador llega a 120 tareas completadas con cero errores de sistema. Miren la tabla del broker: los eventos publicados coinciden exactamente con los consumidos y la cola se mantiene en cero porque el hilo de persistencia drena continuamente hacia el archivo JSONL. Ahora someteremos el clúster a fallos intencionales.»

---

### TURNO 15 (10:55 – 11:40 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Terminal inyectando latencia en w2: `python chaos_test.py latency --worker http://127.0.0.1:8102 --ms 300` y corriendo carga.
* **Acción / Gesto:** Mostrar en el dashboard el aumento de latencia y la disminución de throughput.

> «Primer escenario de caos: inyectamos 300 milisegundos de latencia artificial en el trabajador w2. El clúster no se cae, pero experimenta degradación: el throughput desciende a 8,8 rps y el p95 sube a 4 128 ms. Esto ocurre porque con balanceo Round-Robin ingenuo, un tercio de las peticiones va hacia el nodo retrasado y retiene los hilos de despacho del coordinador. Este experimento nos enseñó que el mamparo por trabajador no protege al coordinador cuando el balanceo es ciego a la carga; más adelante mostraremos cómo lo resolvimos.»

---

### TURNO 16 (11:40 – 12:30 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Terminal inyectando fallo 100% en w2: `python chaos_test.py fail --worker http://127.0.0.1:8102 --rate 1.0` y corriendo carga.
* **Acción / Gesto:** Mostrar en el dashboard el cambio del disyuntor de w2 a rojo OPEN y la continuidad del servicio.

> «Segundo escenario de caos: configuramos a w2 para fallar el 100 % de sus llamadas. Miren atentamente el dashboard: tras el tercer fallo consecutivo, el indicador de w2 cambia a rojo en estado OPEN. El Circuit Breaker aísla el nodo y el reintento desvía el tráfico hacia w1 y w3. La consola reporta un resultado categórico: 120 transacciones atendidas con 100 % de éxito a 17,8 rps, cero errores para el cliente. El sistema perdió capacidad temporalmente, pero preservó la disponibilidad absoluta sin sufrir caídas en cascada.»

---

### TURNO 17 (12:30 – 13:15 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Terminal ejecutando prueba de guardrails: `python chaos_test.py guardrail --tasks 120 --rate 0.25`.
* **Acción / Gesto:** Señalar en el dashboard la columna de transacciones compensadas (31) y código HTTP 409.

> «Tercer escenario: forzamos que el 25 % de las transacciones sea rechazado en la etapa de compliance por violar guardrails de seguridad. Observen el tablero: 89 transacciones completaron normalmente y 31 fueron rechazadas y compensadas por la Saga. El orquestador ejecutó la reversión inversa de RAG y Triage en menos de 100 milisegundos, retornando al cliente un código HTTP 409 con traza auditable. La tasa de atención fue del 100 %, demostrando que una compensación ordenada es una respuesta de negocio válida y no un fallo de arquitectura.»

---

### TURNO 18 (13:15 – 14:05 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Terminal matando proceso de w3 (`chaos_test.py stop`), corriendo carga y luego reiniciando w3.
* **Acción / Gesto:** Mostrar cómo w3 pasa a HALF-OPEN y vuelve a CLOSED recuperando el throughput.

> «Cuarto escenario de caos: simulamos una falla catastrófica apagando físicamente el proceso del trabajador w3. El clúster absorbe la pérdida y atiende la totalidad de la carga operando con dos nodos. Posteriormente, reiniciamos el proceso de w3 en una terminal secundaria. El disyuntor entra automáticamente en estado HALF-OPEN, envía una petición de prueba, comprueba que el nodo responde y conmuta nuevamente a CLOSED, recuperando el caudal nominal de 23,5 rps de forma completamente elástica y transparente.»

---

### TURNO 19 (14:05 – 14:55 · 50 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Figuras 4 y 5 del informe: gráficas de Escalabilidad, Throughput y reducción de latencia p95.
* **Acción / Gesto:** Explicar las curvas de speedup frente al límite lineal ideal.

> «Revisemos los resultados cuantitativos consolidados sobre una muestra de 1 200 transacciones. En escalabilidad horizontal obtuvimos un comportamiento casi lineal: con un nodo registramos 9,24 rps; con dos nodos subimos a 18,14 rps con un speedup de 1,96× y 98,2 % de eficiencia; y con tres nodos alcanzamos 26,74 rps, un speedup de 2,89× con una eficiencia sobresaliente del 96,5 %, superando con creces la meta mínima del 80 %. Simultáneamente, la latencia en el percentil 95 cayó de 3 185 milisegundos a solo 1 043 ms, una reducción de más del triple gracias al alivio de colas.»

---

### TURNO 20 (14:55 – 15:45 · 50 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Figura 8 del informe y Tabla 10: Comparación de balanceo Round-Robin vs Least-Connections.
* **Acción / Gesto:** Resaltar el incremento del 129% de throughput y la reducción del 62% en p95.

> «Lo más enriquecedor del proyecto fueron los cinco ajustes derivados de la medición empírica. El primero fue resolver la trampa de localhost en Windows: la resolución intentaba IPv6 antes de IPv4, penalizando cada llamada en más de dos segundos; forzar 127.0.0.1 abatió la latencia de 2 042 ms a 2,15 ms, un factor de 951 veces más rápido. El segundo ajuste fue la estrategia Least-Connections: bajo un nodo lento, como vimos antes, Round-Robin colapsa a 8,9 rps; al balancear por menor número de tareas activas, el throughput saltó a 20,59 rps, un 129 % más de caudal, reteniendo el 75,7 % de la capacidad del clúster.»

---

### TURNO 21 (15:45 – 16:30 · 45 seg) — 🔵 [JUAN CARLOS] JUAN CARLOS BENÍTEZ ROJAS
* **Rol:** *Líder de Proyecto y Arquitecto de Software*
* **En Pantalla:** Tabla 11 del informe: Balance de Metas cumplidas y conclusiones arquitectónicas.
* **Acción / Gesto:** Contacto visual a cámara, tono de síntesis y reflexión profesional.

> «Los ajustes restantes incluyeron dotar al broker de contrapresión con descarte ordenado y consumidor dedicado, tipificar en los contratos los errores de negocio frente a fallos de infraestructura para evitar reintentos inútiles, y calibrar el pool del gateway a dieciséis hilos. Como conclusión central, confirmamos que la arquitectura de software no es un ejercicio estático de diseño: las colas, las latencias de transporte y la contención física son propiedades emergentes que solo se comprenden cuando el software se somete a carga en red.»

---

### TURNO 22 (16:30 – 17:00 · 30 seg) — 🔴 [JUAN JOSÉ] JUAN JOSÉ CÓRDOBA ERASO
* **Rol:** *Desarrollador Principal y Evaluador de Calidad*
* **En Pantalla:** Repositorio en GitHub `Alboguaci/tejiendo-redes-nexusai` mostrando el informe PDF de 50 páginas y placa de créditos finales.
* **Acción / Gesto:** Mostrar el repositorio en el navegador y despedida final del equipo.

> «Todo el código fuente, los diagramas PlantUML, las suites de prueba y el informe técnico consolidado de 50 páginas bajo normas APA 7ma Edición se encuentran disponibles en nuestro repositorio público de GitHub: Alboguaci/tejiendo-redes-nexusai. Agradecemos a la profesora Leidy Johana Polo por su valiosa orientación académica. Muchas gracias por su atención.»

---
