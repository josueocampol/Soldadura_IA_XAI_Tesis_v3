# GUÍA DETALLADA PARA EL USO DE LA PLANTILLA LaTeX

Esta guía describe paso a paso cómo utilizar la plantilla basada en dos archivos principales: `main.tex` y `configuracion.tex`. Además,y ademas las funciones esenciales (portadas, índices, tablas, figuras, etc.)

---

## 1. ¿Qué es LaTeX y por qué usarlo?

**LaTeX** es un sistema de composición de documentos muy popular en ámbitos académicos y científicos. Sus ventajas incluyen:

- Manejo robusto de referencias, bibliografía, figuras y tablas.  
- Separación clara entre contenido (texto) y formato (estilos, márgenes, tipografías).  
- Presentación profesional y alta calidad tipográfica.  
- Posibilidad de reutilizar fácilmente plantillas (como la que mostramos) para múltiples trabajos o capítulos.

Esta **plantilla** simplifica mucho la configuración inicial. para realizar más énfasis en el contenido

---

## 2. Estructura de la plantilla

El proyecto está dividido principalmente en **dos** archivos:

1. **`main.tex`**  
   - Es el “documento maestro”.  
   - Define la clase (`report`), carga paquetes adicionales y, sobre todo, **llama** a `configuracion.tex`.  
   - Contiene la portada (carátula), índices (Tabla de contenidos, Figuras, Tablas), y los capítulos o secciones de tu trabajo.  
   - Aquí es donde escribirás tus secciones: introducción, justificación, objetivos, conclusiones, etc.

2. **`configuracion.tex`**  
   - Contiene la **configuración global** de tu documento: márgenes, idioma, encabezados y pies de página, tipografías, interlineado, macros para generar la portada, etc.  
   - También define la apariencia de tablas, figuras e índices.

**NOTA:** se puede **modificar poco** `configuracion.tex` (solo si se quiere cambiar, por ejemplo, los márgenes, la tipografía, o añadir algún nuevo comando) y que el contenido principal se redacte en `main.tex`.

---

## 3. Archivo `configuracion.tex`: ¿qué hace?

Separado en:

1. **Márgenes, idioma y tipografía**  
   ```latex
   \usepackage[left=3.5cm, right=3cm, top=3cm, bottom=3cm]{geometry}
   \usepackage[english,main=spanish]{babel}
   \usepackage[T1]{fontenc}
   \usepackage{times}
   \usepackage{fontsize}
   \usepackage{xcolor}
   \usepackage{graphicx}
   \graphicspath{{./img/}}
   ```
   * geometry: define el tamaño de márgenes de cada lado.
   * babel: maneja la configuración lingüística (en este caso, el idioma principal es español y el secundario es inglés).
   * fontenc, times: tipografía Times New Roman (requerida en muchos trabajos formales).
   * graphicx y \graphicspath: permiten incluir imágenes y definen la carpeta de imágenes (`./img/`).
2. **Paquetes adicionales**  
   ```latex
   \usepackage{tocloft}
   \usepackage{fancyhdr}
   \pagestyle{fancy}
   \fancyhf{}
   \rfoot{\thepage}
   \renewcommand{\headrulewidth}{0pt}
   ```
   * fancyhdr: personaliza los encabezados y pies de página.
   * tocloft: permite personalizar cómo se muestran las listas de figuras y tablas.

3. **Interlineado**
   ```latex
   \renewcommand{\baselinestretch}{1.5}
   ```
   Esto ajusta el espaciado entre líneas a 1.5 (otro valor, como 1.2, 2, etc., también se puede usar).

4. **Macros para datos del documento**
   ```latex
   \newcommand{\titulo}[1]{\def\Titulo{#1}}
   \newcommand{\autor}[1]{\def\Autor{#1}}
   \newcommand{\tutor}[1]{\def\Tutor{#1}}
   \newcommand{\fecha}[1]{\def\Fecha{#1}}
   \newcommand{\departamento}[1]{\def\Departamento{#1}}
   \newcommand{\carrera}[1]{\def\Carrera{#1}}
   \newcommand{\fechaActual}{\number\year}
   ```
   Sirven para incrustar datos (título, autor, tutor, año) que luego usa la plantilla de portada.

5. **Comandos para carátulas**
    * `\caratulaTapa` y `\caratulaContenido`: generan páginas de título (titlepage) con el logo y la información de la universidad, departamento, carrera, etc.
    * Cada uno se imprime con `\caratulaTapa` o `\caratulaContenido` dentro de main.tex.

6. **Numeración: `\iniciarNumeracion`**
   ```latex
   \newcommand{\iniciarNumeracion}{
      \setcounter{page}{1}
      \pagestyle{fancy}
      \fancyhf{}
      \fancyfoot[R]{\thepage}
      ...
   }
   ```
   Se usa cuando se quiere que, después de las portadas y del índice, la numeración de páginas empiece en la introducción (página 1).

7. **Configurar índices: `\configurarIndices`**
   ```latex
   \newcommand{\configurarIndices}{
      \setcounter{tocdepth}{3}
      \setcounter{secnumdepth}{3}
      ...
   }
   ```
   Ajusta hasta qué nivel de secciones deseas que aparezcan en la tabla de contenidos (\tableofcontents). Por ejemplo, \subsubsection es nivel 3.
   
---

## 4. Archivo `main.tex`: ¿cómo usarlo?
Este archivo define la clase report y carga configuracion.tex:
```latex
\documentclass[12pt,letterpaper]{report}

% Paquetes adicionales de uso puntual:
\usepackage[justification=centering]{caption}
\usepackage{multicol}
\usepackage{pdfpages}

% Cargar la configuración general
\input{configuracion}

% -- Datos del documento --
\departamento{ciencias de la tecnología e innovación}
\titulo{TITULO DE TRABAJO}
\autor{Nombre del Autor}
\tutor{Nombre del Tutor}
\fecha{\number\year}
\carrera{ingeniería mecatrónica}

\begin{document}

  % 1) Portadas
  \caratulaTapa
  \caratulaContenido
  \newpage
  \clearpage
  \pagestyle{empty}

  % 2) Insertar PDF externo (opcional)
  \includepdf[pages=-,scale=1]{IEEE/IEEE-conference-template-062824.pdf}

  % 3) Resumen Ejecutivo / Abstract
  \newpage
  \section*{Resumen Ejecutivo}
  % Texto...

  \newpage
  \section*{Abstract}
  % Texto...

  % 4) Índices
  \newpage
  \configurarIndices
  \tableofcontents
  \thispagestyle{empty}
  \newpage
  \listoffigures
  \thispagestyle{empty}
  \newpage
  \listoftables
  \thispagestyle{empty}
  \newpage

  % 5) Iniciar numeración
  \iniciarNumeracion

  % 6) Secciones del documento
  \renewcommand{\thesection}{\arabic{section}}
  \section{Análisis del problema}
  % Texto...

  \section{Marco Teórico}
  % Texto...

  \section{Marco Metodológico}
  % Texto...

  % ... etc ...

  % Bibliografía
  \newpage
  \section*{Bibliografía}
  % Aquí van tus referencias (APA 7, etc.)

  % Anexos
  \newpage
  \section*{Anexos}
  % Anexos o contenido extra

  % Ejemplo de figura
  \begin{figure}[ht]
    \refstepcounter{figure}
    \textbf{Figura \thefigure}\\[0.5em]
    \textit{Título breve de la figura}\\[1em]
    \centering
    \includegraphics[width=0.8\textwidth]{mi_imagen.png}
    \normalsize
    Nota: Descripción adicional, si fuera necesaria.
    \addcontentsline{lof}{figure}{Figura \thefigure. Título breve de la figura}
  \end{figure}

  % Ejemplo de tabla en estilo APA
  \begin{table}[ht]
    \captionsetup{justification=raggedright,singlelinecheck=false}
    \caption{\textit{Ejemplo de tabla}}
    \label{tab:variables}
    \centering
    \begin{tabular}{l c}
      \hline
      \textbf{Variable} & \textbf{Valor} \\
      \hline
      Variable A & 10 \\
      Variable B & 20 \\
      \hline
    \end{tabular}
    \begin{flushleft}
      \textit{Nota}. Texto de aclaración.
    \end{flushleft}
  \end{table}

\end{document}
```
1. Datos del documento se definen con las macros \departamento, \titulo, etc.
2. Portadas se crean con \caratulaTapa y \caratulaContenido.
3. Secciones e índices se ordenan según la preferencia.
4. Figuras y tablas se incluyen donde necesites.
---
## 5. Portadas y datos
En main.tex, cuando se usa:
```latex
\caratulaTapa
\caratulaContenido
```
LaTeX generará dos portadas (si así lo deseas). Estas se basan en los datos indicados con:
```latex
\departamento{}
\titulo{}
\autor{}
\tutor{}
\fecha{}
\carrera{}
```
Si solo quieres una portada, elimina uno de los comandos.

---
## 6. Índice de Tablas y Figuras
* Lista de Tablas se genera con \listoftables.
* Lista de Figuras se genera con \listoffigures.
* Para que aparezca “Tabla 1: Título” (y no solo “1 Título”), hay que configurar tocloft, por ejemplo:
```latex
\renewcommand{\cfttabpresnum}{Tabla~}
\renewcommand{\cfttabaftersnum}{: }
\setlength{\cfttabnumwidth}{4em}
```
Esto define un prefijo (“Tabla”) y un separador (”: ”) para la numeración en la lista.

---
## 7. Insertar un PDF externo
Si tienes un documento PDF (por ejemplo en este caso, un artículo IEEE) y quieres que aparezca incrustado en tu trabajo final:
```latex
\usepackage{pdfpages} % (si no está en configuracion.tex)

\includepdf[pages=-,scale=1]{ruta/archivo.pdf}
```
* `pages=-` inserta todas las páginas del PDF.
* `scale=1` mantiene el tamaño original.

---
## 8. Tablas en estilo APA 7

1. **Número y título**
   ```latex
   \begin{table}[ht]
   \captionsetup{justification=raggedright,singlelinecheck=false}
   \caption{\textit{Título de la tabla}}
   \label{tab:ejemplo}
   \centering
   ...
   \end{table}
   ```
   * LaTeX genera el “Tabla 1, 2…” según el orden.
   * El título en cursiva, la palabra “Tabla” y su número en negrita (definido en configuracion.tex con `\captionsetup[table]{...}`).
2. **Nota al pie (convención APA 7)**
   ```latex
   \begin{flushleft}
   \textit{Nota}. Texto de aclaración, fuente de datos, etc.
   \end{flushleft}
   ```
   Esto aparece debajo de la tabla, alineado a la izquierda.
3. **Referencia en el texto**
   “En la Tabla~\ref{tab:ejemplo} se muestra la comparativa…”.

---
## 9. Figuras y gráficos
Para insertar imágenes:
```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.8\textwidth]{nombre_imagen.png}
  \caption{Título descriptivo de la figura}
  \label{fig:mi_imagen}
\end{figure}
```
* Con \caption{} , LaTeX generará la entrada en la lista de figuras.
* Referenciar: “Ver Figura~\ref{fig:mi_imagen}”.

---
## 10. Bibliografía y citas APA 7
La plantilla muestra un lugar donde escribir referencias manualmente:
```latex
\section*{Bibliografía}
- Autor, A. (2020). Título del artículo. Revista, volumen, páginas...
```
---
## 11. Consejos de compilación y edición
* **Compilador**: Usa pdflatex, xelatex o lualatex. Asegúrate de tener el archivo en codificación UTF-8 para que los acentos funcionen correctamente.
* **Editor:** Overleaf, TeXstudio, VSCode con extensión LaTeX, etc. Todos pueden mostrar corrector ortográfico.
* **Limpieza:** Borrar archivos temporales (.aux, .log, .toc, etc.) si encuentras errores que no se solucionan recompilando.
* **Rutas de imágenes:** Al tener \graphicspath{{./img/}}, coloca tus imágenes en la carpeta img.


