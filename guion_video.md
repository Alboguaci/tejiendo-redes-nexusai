# Guion del video demostrativo — NexusAI 2.0

**Duración objetivo:** 12 a 15 minutos
**Formato:** YouTube, visibilidad «No listado»
**Integrantes:** Juan Carlos Benítez Rojas y Juan José Córdoba Eraso

El video se graba en una sola sesión, con el clúster ya probado y el navegador
abierto en el tablero. Cada bloque tiene una duración sugerida y un objetivo
concreto: no se trata de leer el informe, sino de demostrar que el sistema
existe y que las cifras salen de él.

---

## Antes de grabar (5 minutos)

```bash
cd Actividad4_Tejiendo_Redes/prototipo
python run_cluster.py --workers 3 --threads 16 --worker-threads 4
```

1. Abrir `http://127.0.0.1:8088/dashboard.html` y dejarlo en una pestaña.
2. Abrir una terminal en `prototipo/` y otra en `pruebas/`.
3. Abrir el PDF del informe en las páginas de los tres diagramas.
4. Verificar que no queden procesos en los puertos 8080, 8088, 8090 y 8101–8103.
5. Silenciar notificaciones y cerrar aplicaciones que consuman CPU.

---

## Bloque 1 · Presentación (0:00 – 1:00)

**En pantalla:** portada del informe.

**Narración sugerida:**

> «Buenos días. Somos Juan Carlos Benítez y Juan José Córdoba, del curso de
> Arquitectura de Software. En esta actividad retomamos NexusAI, la plataforma de
> atención automatizada que diseñamos en la Actividad 2, y la llevamos de los
> diagramas a un prototipo distribuido que se ejecuta de verdad. El video muestra
> la arquitectura, el código, la demostración en vivo con fallos inyectados y los
> resultados medidos.»

---

## Bloque 2 · Problema y arquitectura (1:00 – 3:30)

**En pantalla:** Figura 1, diagrama de componentes.

**Puntos que se deben decir:**

1. El problema: una plataforma que recibe solicitudes omnicanal y ejecuta tres
   etapas cognitivas —triage, recuperación de contexto y cumplimiento— que deben
   completarse o revertirse juntas.
2. La decisión central: orquestación centralizada con cómputo distribuido. Un
   gateway que conoce el estado de cada transacción y tres nodos que solo saben
   ejecutar pasos.
3. Los cinco componentes: cliente, gateway, broker, nodos y tablero.
4. Por qué no hay estado compartido: los nodos se comunican por HTTP y eventos,
   no por memoria común.

**Frase de cierre del bloque:**

> «Esta separación es la que permite escalar agregando nodos y aislar fallos sin
> detener el sistema.»

---

## Bloque 3 · Modelo dinámico y despliegue (3:30 – 5:00)

**En pantalla:** Figura 2 (secuencia) y Figura 3 (despliegue).

1. Recorrer la secuencia: cliente → gateway → pool de despacho → nodo → broker →
   respuesta; señalar la rama de compensación cuando el guardrail rechaza.
2. Explicar los cuatro niveles de concurrencia: proceso, servidor, despacho y
   cómputo.
3. Mostrar el despliegue: seis procesos, seis puertos, y la equivalencia con
   contenedores en una red bridge.

---

## Bloque 4 · Recorrido del código (5:00 – 7:00)

**En pantalla:** editor con `coordinator.py`, `worker.py` y `broker.py`.

1. `coordinator.py`: clase `SagaOrchestrator` con el arreglo de pasos y el método
   de compensación inversa; `CircuitBreaker` con los tres estados; las dos
   estrategias de balanceo.
2. `worker.py`: `ThreadPoolExecutor` de cuatro hilos por nodo, latencias
   simuladas y endpoint de caos.
3. `broker.py`: topics, cola acotada, bitácora JSONL y consumidor de auditoría.

**Frase clave:**

> «El código no tiene dependencias externas: se ejecuta con la biblioteca estándar
> de Python, y eso hace que la demostración sea reproducible en cualquier equipo.»

---

## Bloque 5 · Demostración en vivo, caso feliz (7:00 – 8:30)

**En pantalla:** terminal con `load_test.py` y tablero al lado.

```bash
python load_test.py --tasks 120 --concurrency 24 --label demo_feliz
```

1. Señalar el throughput y el p95 que imprime la consola.
2. Cambiar al tablero y mostrar: throughput, completadas, compensadas, p95,
   Sagas en vuelo y tasa de atención.
3. Mostrar la tabla de nodos con el estado `CLOSED` del Circuit Breaker y la
   tabla del broker con publicados iguales a consumidos y cola en cero.

---

## Bloque 6 · Fallos inyectados (8:30 – 11:00)

### 6.1 Nodo lento

```bash
python chaos_test.py latency --worker http://127.0.0.1:8102 --ms 300
python load_test.py --tasks 120 --concurrency 24 --label demo_lento
```

> «El sistema no falla: se degrada. El throughput baja porque un tercio de los
> pasos llega al nodo lento y retiene hilos de despacho.»

### 6.2 Nodo defectuoso y Circuit Breaker

```bash
python chaos_test.py fail --worker http://127.0.0.1:8102 --rate 1.0
python load_test.py --tasks 120 --concurrency 24 --label demo_breaker
```

Mostrar en el tablero cómo el breaker de w2 pasa a `OPEN` y el tráfico se
redirige: **todas las transacciones se completan**.

### 6.3 Guardrail y compensación de la Saga

```bash
python chaos_test.py reset
python chaos_test.py guardrail --url http://127.0.0.1:8080 --tasks 120 --rate 0.25
```

El subcomando ejecuta su propia carga y muestra las transacciones compensadas.
Mostrar en el tablero el contador de compensadas y explicar que una compensación
correcta no es un error: es una respuesta de negocio (HTTP 409).

### 6.4 Caída y recuperación

```bash
python chaos_test.py reset
python chaos_test.py stop --worker http://127.0.0.1:8103
python load_test.py --tasks 120 --concurrency 24 --label demo_caida
```

Para recuperar el nodo, abrir una terminal nueva en `prototipo/` y ejecutar:

```bash
python worker.py --id w3 --port 8103 --threads 4 --broker http://127.0.0.1:8090
```

```bash
python load_test.py --tasks 60 --concurrency 12 --label demo_recuperacion
```

> «El sistema pierde capacidad, no servicio. Al reiniciar el nodo, el estado
> HALF_OPEN permite una petición de prueba y el nodo vuelve a operar.»

---

## Bloque 7 · Resultados (11:00 – 12:45)

**En pantalla:** Figuras 5 a 9 del informe.

1. Escalabilidad: 9,24 → 18,14 → 26,74 rps; speedup 2,89× con eficiencia 96,5 %.
2. Latencia: p95 de 3 185 ms a 1 043 ms.
3. Robustez: 100 % atendido en los seis escenarios y cero errores de sistema.
4. Estrategias: 8,99 rps con round-robin frente a 20,59 rps con
   least-connections bajo el mismo nodo lento.
5. Sobrecarga de coordinación: 258 ms, un 31 % de la latencia extremo a extremo.

**Frase clave:**

> «Cada cifra del informe sale de una corrida reproducible con el comando que
> acabamos de ejecutar.»

---

## Bloque 8 · Patrones y conclusiones (12:45 – 14:30)

1. Mencionar los nueve patrones y el problema que resuelve cada uno, en una frase.
2. Señalar los tres hallazgos que cambiaron el diseño: `localhost` frente a
   `127.0.0.1`, el broker sin consumidor y el Bulkhead incompleto en el
   coordinador.
3. Declarar limitaciones: un solo equipo, latencias simuladas, estado en memoria,
   sin seguridad.
4. Cerrar con el aporte: la arquitectura no solo está dibujada, está medida.

**Cierre:**

> «Gracias por su atención. El repositorio, el informe y los diagramas están
> disponibles en los enlaces de la entrega.»

---

## Lista de verificación posterior

- [ ] El video dura entre 12 y 15 minutos.
- [ ] La visibilidad es «No listado».
- [ ] Se ve el clúster real ejecutándose, no solo diapositivas.
- [ ] Se muestra al menos un fallo inyectado y su recuperación.
- [ ] Se muestra el tablero con métricas en vivo.
- [ ] El audio es claro y no hay notificaciones ni ruido de fondo.
- [ ] El enlace del video está en el Anexo E del informe y en el README.
