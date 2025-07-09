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
```
---
## 🚦 ¿Cómo usar el sistema?

![Semáforo inteligente](ruta/a/tu/semaforo.png)

1. **Configura SUMO**  
   - Descarga SUMO desde su sitio oficial: [https://www.eclipse.org/sumo/](https://www.eclipse.org/sumo/)  
   - Crea la variable de entorno `SUMO_HOME` que apunte a la carpeta raíz de tu instalación de SUMO para evitar modificar el código. Si prefieres, puedes establecer directamente en el código la ruta a tu carpeta de SUMO (tendrás que  modificarlo en los scripts de train.py, test.py y SUMOextractor).

2. **Prepara el entorno Python**  
   - Asegúrate de tener Python 3.10+ instalado y un editor de código (como VSCode, PyCharm o similar).  
   - Instala las dependencias del proyecto con `pip install -r requirements.txt`.

3. **Crea o utiliza una simulación de tráfico**  
   - Para crear tu propia red, abre **NetEdit** (se instala con SUMO) y diseña la red a tu gusto.  
   > Nota: Este proyecto considera carreteras con intersecciones de 4 carriles en ambas direcciones. Para otras topologías será necesario modificar el extractor SUMO o incluso el entorno, en caso de que cambien las observaciones o acciones disponibles.  
   - Para usar la  red utilizada  en  los experimentos, copia los archivos de la carpeta `simulations` y pégalos en tu directorio de SUMO (tu `SUMO_HOME`).

4. **Ejecuta y prueba**  
   Puedes optar por:

   ### A) Probar el catálogo de modelos existentes

   - Este catálogo incluye políticas orientadas a diferentes valores sociales:  
     - Eficiencia (reduce tiempos de retraso)  
     - Equidad modal (favorece transporte público)  
     - Sostenibilidad: climática (reduce el consumo de combustible y emisiones de CO2)
     - Sostenibilidad: calidad del aire (reduce emisiones NOx)


   A1. **Selecciona el modelo que deseas probar**  
      - Elige uno de los modelos preentrenados disponibles en el catálogo.

   A2. **Ejecuta el script `test.py`**  
      - Utiliza el script `test.py` seleccionando el nombre del modelo que quieres probar. Puedes ajustar el número de episodios o activar/desactivar el modo gráfico modificando la opción `-gui` en el comando `sumo_cmd`.

   A3. **Observa  la simulación**  
      - Se abrirá la interfaz  gráfica de SUMO y podrás  obeservar la  simulacion de tráfico controlada por los semaforos selccionados. Al final, obtendrás métricas de desempeño.

   ### B) Crear tus propios agentes
   
      B1. **Define tu nuevo tipo de agente**  
      - Crea una nueva clase de agente en la carpeta `agents/`, heredando de `LearningAgent` si será un agente de aprendizaje o de `BaseAgent` en otro caso.

      B2. **Implementa los métodos necesarios**  
      - Implementa el método `act` y, en caso de ser un agente de aprendizaje, el método `act_and_train`. Estos  métodos determinarán la forma de actuar de tus  agentes, así como su proceso de entrenamiento.
      
      B3. **Personaliza la señal de recompensa**  
      -  Puedes modificar la función de recompensa que recibirán los agentes accediendo al entorno (`TrafficEnvironment.py`) y modificando el método `get_reward`.
      
      B4. **Integra tu  nuevo  tipo de  agente en el script de entrenamiento**  
      - Una vez configurado todo esto, ve al script `train.py` e incorpora tu tipo de agente en el método `train`, en la parte donde se crean los agentes, dándole el nombre que prefieras.
      
      B5. **Ejecuta el entrenamiento**  
      - Ejecuta el entrenamiento, indicando el nombre con el que quieres guardar el modelo y, opcionalmente, el número de episodios a ejecutar. Si no lo especificas, se utilizará el método de early stopping.
      
      2F. **Analiza los resultados**  
      - Espera al entrenamiento y obtendrás las gráficas: curva de aprendizaje y evolución de las diferentes métricas. Tu modelo estará listo  para ser probado.
      
      2G. **Prueba tu modelo**
      -  Vuelve a la opción A para probar tu modelo.
---


