# Proyecto Entregable: Manejo de Azure AI Services

Este repositorio contiene el proyecto entregable para el ejercicio "Manejo de Azure".  
El objetivo principal es desarrollar una aplicación web que utiliza los servicios de **Azure AI Services** para el manejo de sistemas de información.

##  Escenario del Proyecto

El proyecto simula un escenario real dentro de un **sistema CRM**, específicamente en el módulo de atención al cliente.  
El objetivo es poder analizar quejas y sugerencias de los clientes que se reciben como imágenes escaneadas.  
La aplicación debe ser capaz de procesar estas imágenes, extraer el texto y entender el contenido, incluso si este se encuentra en diferentes idiomas.

##  Funcionalidades

La solución consiste en una aplicación web, desarrollada y publicada en Azure, que implementa el siguiente flujo de trabajo:

### Parte 1: Procesamiento de Imagen y Traducción

1. **Carga y Almacenamiento de Imágenes:**
   * La aplicación web incluye un selector de ficheros que permite al usuario elegir una imagen (que contiene el texto a analizar).
   * Una vez seleccionada, la imagen se sube a la web.
   * La imagen se almacena de forma persistente en un **servicio de almacenamiento de Azure** (por ejemplo, Azure Blob Storage).  
     La elección del servicio más apropiado forma parte de la investigación del ejercicio.

2. **Extracción de Texto (OCR) y Traducción:**
   * Una vez almacenada la imagen, la aplicación utiliza el servicio **Azure Computer Vision** para realizar un Reconocimiento Óptico de Caracteres (OCR) y extraer todo el texto contenido en ella.
   * El sistema detecta automáticamente el idioma del texto extraído y utiliza el servicio **Azure Translator** para realizar la traducción.

### Parte 2: Análisis de Contenido

La aplicación se completa integrando el servicio **Azure Text Analytics** para obtener información más profunda sobre el texto traducido.

* **Análisis de Sentimiento:** Se identifica el sentimiento general del texto (positivo, negativo, neutro).  
* **Extracción de Frases Clave:** Se obtienen las ideas o temas principales del comentario del cliente.  
* **Clasificación de Contenido:** Se aplica un etiquetado o clasificación sencilla al contenido, permitiendo categorizar la respuesta (por ejemplo, "Queja", "Sugerencia", "Consulta").

##  Tecnologías Utilizadas

* **Azure AI Services:**
  * **Computer Vision:** Para el reconocimiento de texto (OCR).  
  * **Translator:** Para la detección de idioma y traducción automática.  
  * **Text Analytics:** Para el análisis de sentimiento, extracción de frases clave y clasificación.  

* **Azure Storage:**
  * Servicio de almacenamiento (por ejemplo, Blob Storage) para guardar los ficheros de imagen subidos.  

* **Azure App Service** (o similar):
  * Plataforma para la publicación y despliegue de la aplicación web en la nube.  

##  Parte 3: Análisis de Dataset y Dashboard

El ejercicio incluye una tercera parte que consiste en:

1. Utilizar un dataset de respuestas de usuarios y aplicar el mismo análisis de la Parte 2.  
2. Generar un fichero **CSV** con toda la información extraída y analizada (texto, categoría, sentimiento).  
3. Importar este CSV en **Excel** y crear un cuadro de mando con gráficos que permitan visualizar los sentimientos y categorías encontrados.  


