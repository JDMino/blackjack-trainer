# Plantillas de reconocimiento

Esta carpeta debe contener una imagen por rango de carta, usada por
`ReconocedorCartas` (ver `app/recognition/`) para identificar las
cartas detectadas en pantalla.

## ⚠️ Formato esperado: LA CARTA COMPLETA, no solo el índice

`ProcesadorImagen` (la capa de visión) recorta el **rectángulo
completo de la carta** desde la mesa — no solo el número/letra de la
esquina. Por lo tanto, cada plantilla debe ser también la carta
completa: borde superior a borde inferior, todo el ancho.

❌ Incorrecto: una imagen pequeña con solo el "7" de la esquina.
✅ Correcto: el rectángulo entero de la carta (borde, índice, dibujo
   central, todo), tal como se ve en la mesa.

Si las plantillas no coinciden en este formato con lo que
`ProcesadorImagen` recorta en tiempo real, `ReconocedorCartas` dará
resultados de baja confianza o incorrectos, incluso si la plantilla
"se ve bien" a simple vista.

## Nombres de archivo esperados

```
2.png   3.png   4.png   5.png   6.png   7.png   8.png   9.png
10.png  J.png   Q.png   K.png  A.png
```

## Cómo generarlas

1. Ejecuta `main.py`, selecciona con el mouse la región de tu mesa,
   y deja correr la app con cartas reales visibles (o simplemente
   toma un screenshot normal de esa zona con la herramienta de tu
   sistema operativo).
2. Para cada rango distinto que veas, recorta **la carta completa**
   (no solo el índice) con cualquier editor de imágenes.
3. Guarda cada recorte como `{rango}.png` en esta carpeta. No
   necesitas que tengan un tamaño exacto: `BancoPlantillas` las
   redimensiona automáticamente al cargarlas.

## Nota

No es necesario tener las 13 plantillas para empezar a probar. El
sistema funciona con un conjunto parcial (por ejemplo, si solo
generas plantillas para 2, 7, 10 y A para tus primeras pruebas), pero
`ReconocedorCartas` solo podrá reconocer los rangos que sí tengan
plantilla cargada.

