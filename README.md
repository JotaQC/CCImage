# 🖼 CCImage - Conversor &amp; Compresor de Imágenes 🖼

<b>CCImage</b> es una aplicación <b>portable</b> para convertir imágenes entre distintos formatos y comprimirlas para ahorrar espacio sin perder calidad.

Con CCImage puedes:
- Elegir la <b>calidad de salida</b> para `JPEG` y `WEBP` con un <b>slider interactivo</b> y ver los cambios en tiempo real.
- Comprimir imágenes <b>sin cambiar su formato</b>.
- Visualizar un <b>antes y después</b> de la imagen para comparar tamaños y calidad.
>[!NOTE]
>El slider de calidad solo funciona con los formatos `JPEG` y `WEBP`.

## 🤓 Características 🤓
- Conversión entre formatos: `JPEG`, `PNG`, `GIF`, `BMP`, `TIFF`, `WEBP`.
- Compresión sin cambiar formato.
- Vista previa en tiempo real del tamaño y calidad de la imagen.
- Interfaz gráfica moderna con <b>CustomTkinter</b>.
- Portable y fácil de usar.

## ⚙️ Instalación 🤔
1. Clona este repositorio:
```
git clone https://github.com/JotaQC/CCImage.git
cd CCImage
```
2. Instala las dependencias:
```
pip install -r requirements.txt
```
3. Ejecuta la aplicación:
```
python ccimage.py
```

## 🧑‍💻 Uso 🧑‍💻
1. Haz clic en <b>"Seleccionar imagen"</b> para abrir un archivo.
2. Si desear cambiar el formato, selecciona uno en el menú desplegable; de lo contrario, activa <b>"Comprimir sin cambiar formato"</b>.
3. Ajusta el <b>slider de calidad</b> si estás usando `JPEG` o `WEBP`.
4. Visualiza el antes y después de la imagen y su tamaño final.
5. Haz clic en <b>"Convertir"</b> para guardar la imagen procesada.
>[!NOTE]
>La imagen se guardará en el mismo directorio donde seleccionaste la original con el mismo nombre añadiendo `_compressed` al final de este.

## 💡 Mejoras futuras ☝️🤓
- [x] Ajuste de resolución.
- [x] Procesamiento por lotes (varias imágenes a la vez).
- [ ] Soporte para más formatos de imagen.
