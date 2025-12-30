import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, io

# Configuración de CustomTkinter
ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Color theme

# Formatos para exportación
VALID_FORMATS = {"JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP"}

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CCImage - Conversor & Compresor de Imágenes")
        self.root.resizable(False, False)

        self.image_path = None
        self.original_format = None
        self.original_size = 0
        self.preview_img_orig = None
        self.preview_img_comp = None

        self.resize_enabled = ctk.BooleanVar(value=False)
        self.keep_ratio = ctk.BooleanVar(value=True)
        self.width_var = ctk.StringVar()
        self.height_var = ctk.StringVar()

        self.batch_output_dir = None

        # --- Título ---
        frame_title = ctk.CTkFrame(root, fg_color="transparent")
        frame_title.pack(side="top", pady=(35, 0))
        lbl_text = ctk.CTkLabel(frame_title, text="CCImage", font=("Arial", 96))
        lbl_text.pack(side="left")
        frame_subtitle = ctk.CTkFrame(root, fg_color="transparent")
        frame_subtitle.pack(side="top", pady=(15, 0))
        lbl_text = ctk.CTkLabel(frame_subtitle, text="Conversor & Compresor de Imágenes", font=("Arial", 24))
        lbl_text.pack(side="left")

        # --- Label Procesamiento individual ---
        self.lbl_format = ctk.CTkLabel(root, text="Procesamiento individual", font=("Arial", 16))
        self.lbl_format.pack(pady=(20, 2))

        # --- Botón seleccionar imagen ---
        self.btn_select = ctk.CTkButton(
            root,
            text="Seleccionar imagen",
            fg_color="#1865B3",
            corner_radius=10,
            command=self.select_image
        )
        self.btn_select.pack(pady=5)

        # --- Label Procesamiento por lote ---
        self.lbl_format = ctk.CTkLabel(root, text="Procesamiento por lote", font=("Arial", 16))
        self.lbl_format.pack(pady=(10, 2))

        # --- Procesar por lotes
        self.btn_batch = ctk.CTkButton(
            root,
            text="Procesar por lote",
            fg_color="#009650",
            corner_radius=10,
            command=self.select_images_batch
        )
        self.btn_batch.pack(pady=(5, 10))

        # --- Seleccionar directorio de salida
        self.btn_select_output_dir = ctk.CTkButton(
            root,
            text="Seleccionar directorio de salida",
            fg_color="#009650",
            corner_radius=10,
            command=self.select_batch_output_dir
        )
        self.btn_select_output_dir.pack(pady=(5, 5))

        # --- Label para mostrar directorio de salida
        self.lbl_output_dir = ctk.CTkLabel(
            root,
            text="Directorio de salida: no seleccionado",
            wraplength=700,
            justify="left"
        )
        self.lbl_output_dir.pack(pady=(0, 10))

        # --- Formato original ---
        self.lbl_format = ctk.CTkLabel(root, text="Formato original: -")
        self.lbl_format.pack(pady=5)

        # --- Condiciones switchers ---
        self.compress_enabled = ctk.BooleanVar(value=True)
        self.keep_format_no_compress = ctk.BooleanVar(value=False)

        # --- Frame para los switches ---
        self.frame_switches = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )
        self.frame_switches.pack(pady=10)

        # --- Switch comprimir ---
        self.compress_switch = ctk.CTkSwitch(
            self.frame_switches,
            text="Activar compresión",
            variable=self.compress_enabled,
            command=self.toggle_compression_mode
        )
        self.compress_switch.pack(pady=5)

        # --- Switch mantener formato sin comprimir ---
        self.keep_format_switch = ctk.CTkSwitch(
            self.frame_switches,
            text="Mantener formato (procesado mínimo)",
            variable=self.keep_format_no_compress,
            command=self.update_preview
        )

        # --- Switch comprimir sin cambiar formato ---
        self.compress_only = ctk.CTkSwitch(
            self.frame_switches,
            text="Comprimir sin cambiar formato",
            command=self.toggle_compress_only
        )

        # --- Menu de selección de formato ---
        self.format_var = ctk.StringVar(value="Seleccione una imagen primero...")
        self.option_menu = ctk.CTkOptionMenu(
            root,
            values=[],
            variable=self.format_var,
            command=self.set_format
        )
        self.option_menu.pack(pady=10)

        # --- Slider calidad ---
        self.quality_label = ctk.CTkLabel(root, text="Calidad (JPEG/WEBP):")
        self.quality_slider = ctk.CTkSlider(
            root,
            from_=1,
            to=100,
            number_of_steps=100,
            command=lambda x: self.update_preview()
        )
        self.quality_label.pack_forget()
        self.quality_slider.pack_forget()

        # --- Ajuste de resolución ---
        self.resize_switch = ctk.CTkSwitch(
            root,
            text="Ajustar resolución",
            variable=self.resize_enabled,
            command=lambda: (self.toggle_resize_fields(), self.update_preview())
        )
        self.resize_switch.pack(pady=(15, 5))

        frame_resize = ctk.CTkFrame(root)
        frame_resize.pack(pady=5)

        ctk.CTkLabel(frame_resize, text="Ancho:").grid(row=0, column=0, padx=5)
        self.entry_width = ctk.CTkEntry(frame_resize, width=80, textvariable=self.width_var)
        self.entry_width.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(frame_resize, text="Alto:").grid(row=0, column=2, padx=5)
        self.entry_height = ctk.CTkEntry(frame_resize, width=80, textvariable=self.height_var)
        self.entry_height.grid(row=0, column=3, padx=5)

        self.keep_ratio_check = ctk.CTkCheckBox(
            root,
            text="Mantener proporción",
            variable=self.keep_ratio,
            command=self.update_preview
        )

        self.keep_ratio_check.pack(pady=5)

        # --- Labels imágenes ---
        self.size_label = ctk.CTkLabel(root, text="")
        self.size_label.pack(pady=5)

        # --- Vista previa antes/después ---
        self.frame_preview = ctk.CTkFrame(root)
        self.frame_preview.pack(pady=10, fill="both", expand=False)

        self.lbl_img_before = ctk.CTkLabel(self.frame_preview, text="")
        self.lbl_img_before.pack(side="left", padx=10)

        self.lbl_img_after = ctk.CTkLabel(self.frame_preview, text="")
        self.lbl_img_after.pack(side="right", padx=10)

        # --- Botón procesar ---
        self.btn_convert = ctk.CTkButton(root, text="Procesar", fg_color="#1865B3", corner_radius=10, command=self.convert_image, state="disabled")
        self.btn_convert.pack(pady=10)

        # --- Sección resize ---
        self.toggle_resize_fields()
        self.width_var.trace_add("write", lambda *args: self.update_preview())
        self.height_var.trace_add("write", lambda *args: self.update_preview())

        # --- Inicializar estado de switches ---
        self.toggle_compression_mode()

        # --- Créditos ---
        frame_credits = ctk.CTkFrame(root, fg_color="transparent")
        frame_credits.pack(side="bottom", pady=10)

        lbl_text = ctk.CTkLabel(frame_credits, text="Desarrollado por ", font=("Arial", 12))
        lbl_text.pack(side="left")

        lbl_link = ctk.CTkLabel(
            frame_credits,
            text="JotaQC",
            font=("Arial", 12),
            text_color="white",
            cursor="hand2"
        )
        lbl_link.pack(side="left")

        lbl_year = ctk.CTkLabel(frame_credits, text=" © 2025", font=("Arial", 12))
        lbl_year.pack(side="left")

        # --- Función para abrir enlace ---
        def open_web(event=None):
            import webbrowser
            webbrowser.open("https://github.com/JotaQC")

        lbl_link.bind("<Button-1>", open_web)

        def on_enter(event):
            lbl_link.configure(text_color="#01417E")
        
        def on_leave(event):
            lbl_link.configure(text_color="white")

        lbl_link.bind("<Enter>", on_enter)
        lbl_link.bind("<Leave>", on_leave)

    # --- Funciones ---
    def select_images_batch(self):
        if not self.batch_output_dir:
            messagebox.showwarning(
                "Directorio no seleccionado",
                "Selecciona primero un directorio de salida para las imágenes."
            )
            return

        filetypes = [
            ('Imágenes', '*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp'),
            ('Todos los archivos', '*.*')
        ]

        paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=filetypes
        )
        if not paths:
            return

        self.process_batch(list(paths))

    def process_batch(self, image_paths):
        errors = []
        processed = 0

        for path in image_paths:
            try:
                img = Image.open(path)
                image_format = img.format.upper()

                output_format = self.get_batch_output_format(image_format)

                if output_format == "JPEG" and img.mode == "RGBA":
                    img = img.convert("RGB")

                params = {}
                if self.is_compression_active():
                    params["optimize"] = True
                    if output_format in ("JPEG", "WEBP"):
                        params["quality"] = int(self.quality_slider.get())

                filename = os.path.basename(path)
                name, _ = os.path.splitext(filename)

                output_path = os.path.join(
                    self.batch_output_dir,
                    f"{name}_edited.{output_format.lower()}"
                )

                img.save(output_path, output_format, **params)
                processed += 1

            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        if errors:
            messagebox.showwarning(
                "Proceso terminado",
                f"Procesadas: {processed}\nErrores: {len(errors)}"
            )
        else:
            messagebox.showinfo(
                "Éxito",
                f"Se procesaron {processed} imágenes correctamente."
            )

    def select_batch_output_dir(self):
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if not directory:
            return

        self.batch_output_dir = directory
        self.lbl_output_dir.configure(
            text=f"Directorio de salida: {directory}"
        )
    
    def get_batch_output_format(self, image_format):
        image_format = image_format.upper()
        selected = self.format_var.get().upper()

        if selected not in VALID_FORMATS:
            selected = image_format

        if self.compress_enabled.get():
            if self.compress_only.get():
                return image_format
            return selected
        else:
            if self.keep_format_no_compress.get():
                return image_format
            return selected

    def get_final_format(self):
        # Devuelve el formato que se usará
        if not self.image_path:
            return None

        if self.compress_enabled.get():
            if self.compress_only.get():
                return self.original_format
            return self.format_var.get()
        else:
            if self.keep_format_no_compress.get():
                return self.original_format
            return self.format_var.get()


    def is_compression_active(self):
        # Indica compresión intencional
        return self.compress_enabled.get()


    def should_show_quality_slider(self):
        # Determinar si debe mostrar slider de calidad
        final_format = self.get_final_format()
        if not final_format:
            return False

        return self.is_compression_active() and final_format in ("JPEG", "WEBP")


    def toggle_compression_mode(self):
        if self.compress_enabled.get():
            # Modo compresión
            self.keep_format_switch.pack_forget()
            self.compress_only.pack(pady=5)
            self.compress_switch.pack(pady=5)
            self.option_menu.configure(state="normal")
        else:
            # Modo sin compresión
            self.compress_only.pack_forget()
            self.keep_format_switch.pack(pady=5)
            self.compress_switch.pack(pady=5)
            if self.keep_format_no_compress.get():
                self.option_menu.configure(state="disabled")
            else:
                self.option_menu.configure(state="normal")
        
        self.update_option_menu_state()
        self.update_quality_slider_visibility()
        self.update_preview()

    def toggle_compress_only(self):
        self.update_option_menu_state()
        self.update_quality_slider_visibility()
        self.update_preview()

    def update_option_menu_state(self):
        if (self.compress_only.get() and self.compress_enabled.get()) or \
        (self.keep_format_no_compress.get() and not self.compress_enabled.get()):
            self.option_menu.configure(state="disabled")
        else:
            self.option_menu.configure(state="normal")


    def select_image(self):
        filetype = [
            ('Imágenes', '*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp'),
            ('Todos los archivos', '*.*')
        ]
        path = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=filetype)
        if not path:
            return

        self.image_path = path
        try:
            img = Image.open(path)
            self.original_format = img.format.upper()
            self.original_size = os.path.getsize(path)

            width, height = img.size
            self.width_var.set(str(width))
            self.height_var.set(str(height))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen: {e}")
            return

        self.lbl_format.configure(text=f"Formato original: {self.original_format}")

        all_formats = ["JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP"]
        available_formats = [f for f in all_formats if f != self.original_format]

        self.option_menu.configure(values=available_formats if available_formats else [self.original_format])
        self.format_var.set(available_formats[0] if available_formats else self.original_format)

        self.show_original_thumbnail()
        self.update_quality_slider_visibility()
        self.update_preview()
        self.btn_convert.configure(state="normal")

    def set_format(self, fmt):
        self.format_var.set(fmt)
        self.update_quality_slider_visibility()
        self.update_preview()

    def update_quality_slider_visibility(self):
        if self.should_show_quality_slider():
            self.quality_label.pack(pady=5)
            self.quality_slider.pack(pady=5)
        else:
            self.quality_label.pack_forget()
            self.quality_slider.pack_forget()

    def show_original_thumbnail(self):
        img = Image.open(self.image_path)
        img.thumbnail((300, 300))
        self.preview_img_orig = ImageTk.PhotoImage(img)
        self.lbl_img_before.configure(image=self.preview_img_orig, text="Antes")

    def update_preview(self):
        if not self.image_path:
            return

        img = Image.open(self.image_path)
        img = self.apply_resize(img)

        final_format = self.get_final_format()

        if final_format == "JPEG" and img.mode == "RGBA":
            img = img.convert("RGB")

        params = {}
        if self.is_compression_active():
            params["optimize"] = True
            if final_format in ("JPEG", "WEBP"):
                params["quality"] = int(self.quality_slider.get())

        buffer = io.BytesIO()
        try:
            img.save(buffer, format=final_format, **params)
        except Exception:
            return

        new_size = len(buffer.getvalue())
        self.size_label.configure(
            text=f"Tamaño original: {self.original_size/1024:.2f} KB | Tamaño actual: {new_size/1024:.2f} KB"
        )

        buffer.seek(0)
        preview = Image.open(buffer)
        preview.thumbnail((300, 300))
        self.preview_img_comp = ImageTk.PhotoImage(preview)
        self.lbl_img_after.configure(image=self.preview_img_comp, text="Después")

        self.update_option_menu_state()
        self.update_quality_slider_visibility()

    def convert_image(self):
        if not self.image_path:
            return

        output_format = self.get_final_format()
        output_path = os.path.splitext(self.image_path)[0] + "_edited." + output_format.lower()

        try:
            img = Image.open(self.image_path)
            img = self.apply_resize(img)

            if output_format == "JPEG" and img.mode == "RGBA":
                img = img.convert("RGB")

            params = {}
            if self.is_compression_active():
                params["optimize"] = True
                if output_format in ("JPEG", "WEBP"):
                    params["quality"] = int(self.quality_slider.get())

            img.save(output_path, output_format, **params)
            messagebox.showinfo("Éxito", f"Imagen procesada\nGuardada en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def apply_resize(self, img):
        if not self.resize_enabled.get():
            return img
        
        try:
            target_w = int(self.width_var.get())
            target_h = int(self.height_var.get())
        except ValueError:
            return img
        
        if target_w <= 0 or target_h <= 0:
            return img

        orig_w, orig_h = img.size

        if self.keep_ratio.get():
            scale_w = target_w / orig_w
            scale_h = target_h / orig_h
            scale = min(scale_w, scale_h)

            target_w = int(orig_w * scale)
            target_h = int(orig_h * scale)

        return img.resize((target_w, target_h), Image.LANCZOS)
    
    def toggle_resize_fields(self):
        state = "normal" if self.resize_enabled.get() else "disabled"
        self.entry_width.configure(state=state)
        self.entry_height.configure(state=state)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ImageConverterApp(root)

    root.update()
    content_width = root.winfo_width()
    content_height = root.winfo_height()

    min_width = 800
    min_height = 800

    root.minsize(max(content_width, min_width), max(content_height, min_height))

    root.mainloop()

