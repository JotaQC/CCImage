import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, io

# Configuración de CustomTkinter
ctk.set_appearance_mode("Dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Color theme

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

        # --- Título ---
        frame_title = ctk.CTkFrame(root, fg_color="transparent")
        frame_title.pack(side="top", pady=(35, 0))
        lbl_text = ctk.CTkLabel(frame_title, text="CCImage", font=("Arial", 96))
        lbl_text.pack(side="left")
        frame_subtitle = ctk.CTkFrame(root, fg_color="transparent")
        frame_subtitle.pack(side="top", pady=(15, 0))
        lbl_text = ctk.CTkLabel(frame_subtitle, text="Conversor & Compresor de Imágenes", font=("Arial", 24))
        lbl_text.pack(side="left")

        # --- Botón seleccionar imagen ---
        self.btn_select = ctk.CTkButton(root, text="Seleccionar imagen", fg_color="#1865B3", corner_radius=10, command=self.select_image)
        self.btn_select.pack(pady=(40, 10))

        # --- Formato original ---
        self.lbl_format = ctk.CTkLabel(root, text="Formato original: -")
        self.lbl_format.pack(pady=5)

        # --- Switch On/Off ---
        self.compress_only = ctk.CTkSwitch(root, text="Comprimir sin cambiar formato", command=self.toggle_compress_only)
        self.compress_only.pack(pady=10)

        # --- Menu de selección de formato ---
        self.format_var = ctk.StringVar()
        self.option_menu = ctk.CTkOptionMenu(root, values=[], variable=self.format_var, command=self.set_format)
        self.option_menu.pack(pady=10)

        # --- Slider calidad ---
        self.quality_label = ctk.CTkLabel(root, text="Calidad (JPEG/WEBP):")
        self.quality_slider = ctk.CTkSlider(root, from_=1, to=100, number_of_steps=100, command=lambda x: self.update_preview())
        self.quality_label.pack_forget()
        self.quality_slider.pack_forget()

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

        # --- Botón convertir ---
        self.btn_convert = ctk.CTkButton(root, text="Convertir", fg_color="#1865B3", corner_radius=10, command=self.convert_image, state="disabled")
        self.btn_convert.pack(pady=10)

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
    def toggle_compress_only(self):
        if self.compress_only.get() == 1:
            self.option_menu.configure(state="disabled")
        else:
            self.option_menu.configure(state="normal")
        self.update_quality_slider_visibility()
        self.update_preview()

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
        final_format = self.format_var.get()
        if self.compress_only.get() == 1:
            final_format = self.original_format

        if final_format in ["JPEG", "WEBP"]:
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

        temp_img = Image.open(self.image_path)
        final_format = self.format_var.get()
        if self.compress_only.get() == 1:
            final_format = self.original_format

        if final_format == "JPEG" and temp_img.mode == "RGBA":
            temp_img = temp_img.convert("RGB")

        params = {"optimize": True}
        if final_format in ["JPEG", "WEBP"]:
            params["quality"] = int(self.quality_slider.get())
        elif final_format == "PNG":
            params["optimize"] = True

        buffer = io.BytesIO()
        try:
            temp_img.save(buffer, format=final_format, **params)
        except:
            return

        data = buffer.getvalue()
        new_size = len(data)
        self.size_label.configure(text=f"Tamaño original: {self.original_size/1024:.2f} KB | Comprimido: {new_size/1024:.2f} KB")

        buffer.seek(0)
        preview = Image.open(buffer)
        preview.thumbnail((300, 300))
        self.preview_img_comp = ImageTk.PhotoImage(preview)
        self.lbl_img_after.configure(image=self.preview_img_comp, text="Después")

    def convert_image(self):
        if not self.image_path:
            return

        output_format = self.format_var.get()
        if self.compress_only.get() == 1:
            output_format = self.original_format

        output_path = os.path.splitext(self.image_path)[0] + "_compressed." + output_format.lower()

        try:
            img = Image.open(self.image_path)
            if output_format == "JPEG" and img.mode == "RGBA":
                img = img.convert("RGB")

            params = {"optimize": True}
            if output_format in ["JPEG", "WEBP"]:
                params["quality"] = int(self.quality_slider.get())
            elif output_format == "PNG":
                params["optimize"] = True

            img.save(output_path, output_format, **params)
            messagebox.showinfo("Éxito", f"Imagen procesada\nGuardada en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo convertir la imagen:\n{e}")

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
