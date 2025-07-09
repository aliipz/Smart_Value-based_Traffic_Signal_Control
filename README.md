# Smart Value-based Traffic Signal Control
# 🧠 Smart Value-Based Traffic Control System

Sistema inteligente de control de semáforos basado en valores, desarrollado mediante aprendizaje por refuerzo y probado en un  sistema de  simulación de tráfico urbano.

---

## 📝 Resumen

Frente al desafío global de congestión urbana, los **semáforos inteligentes** emergen como herramienta clave, combinando el procesamiento de datos en tiempo real con la toma de decisiones autónoma, logrando reducir atascos y tiempos de espera.

El análisis de los sistemas adaptativos de control de tráfico constituye un área en pleno desarrollo, donde destacan especialmente las técnicas de **aprendizaje por refuerzo**. Este paradigma permite a los agentes semafóricos descubrir de forma autónoma políticas óptimas, aprendiendo mediante la interacción continua con el entorno vial, guiados por señales de recompensa que evalúan su comportamiento.

La flexibilidad en el diseño de recompensas abre la oportunidad de incorporar **valores sociales** más allá del objetivo tradicional de eficiencia, como **sostenibilidad**, **seguridad** o **equidad**. Surge así el concepto de **semáforos inteligentes basados en valores**, sistemas cuyo comportamiento se guía explícitamente por consideraciones sociales, priorizando selectivamente unos valores u otros según necesidades urbanas específicas.

Este trabajo aborda el desafío del diseño e implementación de sistemas de control de tráfico basados en valores mediante un enfoque integral: primero, se desarrolla un entorno integrado de entrenamiento y evaluación de políticas semafóricas utilizando el simulador de tráfico SUMO; segundo, se implementa un algoritmo de aprendizaje por refuerzo multiagente con señales de recompensa especializadas, generando un **catálogo de esquemas de control** orientados a diferentes valores sociales. Este repertorio permite la selección dinámica de políticas según necesidades contextuales específicas. Finalmente, se realiza una evaluación comparativa rigurosa entre estos modelos y sistemas tradicionales, de tiempos fijos y adaptativos basados en reglas heurísticas.

---

### 🎯 Objetivos del   proyeceto

- Construir un entorno integrado (SUMO + Gymnasium) para simular y comparar políticas de control semafórico basadas en **eficiencia**, **sostenibilidad** y **equidad modal**.
- Evaluar desde modelos clásicos (**tiempos fijos**), pasando por sistemas **adaptativos basados en reglas heurísticas**, hasta agentes avanzados de **aprendizaje por refuerzo profundo**.
- Generar un catálogo de agentes RL con **perfiles de valores diferenciados** según el diseño de la recompensa.



---

## ⚙️ Tecnologías utilizadas

- **Python 3.10+**
- [**SUMO**](https://www.eclipse.org/sumo/) – Motor de simulación de tráfico
- [**Gymnasium**](https://gymnasium.farama.org/) – Entorno RL personalizable
- **PyTorch** – Entrenamiento de redes neuronales

---

## 🗂️ Estructura del repositorio

```plaintext
📁 /agents           → Implementaciones  de los  diferentes  tipos de agentes (tiempos fijos, heurísticos, de aprendizaje)
📁 /models           → Modelos entrenados, con  diferentes perfiles  de valores
📁 /plots            → Gráficas generadas a partir de los modelos entrenados
📁 /simulation       → Archivos de simulación utilizados en los experimentos: '.net`, `.rou` y `.sumoconfig`.
📄 createRoutes.py   → Script para crear flujos de vehículos aleatorios a partir de una red de tráfico
📄 graphics.txt      → Script para generar gráficas relacionadas con el entrenamiento de agentes
📄 SUMOextractor.py  → Script  con  diferentes  métodos para extraer información de archivos `.net` de la red de tráfico
📄 TrafficEnvironment.py  → Implementación del entorno (Gymnasium) con el que interactúan los agentes
📄 train.py          → Entrenamiento de nuevos agentes 
📄 test.py           →  Evaluación de agentes con métricas basadas en valores

