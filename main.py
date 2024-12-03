import logging
import customtkinter as ctk
import tkinter as tk
from objects.virtualWindow import VirtualWindow
from tkinter import filedialog
from data.variable import *
import tkinter.ttk as ttk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler("app.log")
    ]
)

class LeftSidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, width=200)
        self.grid_columnconfigure(0, weight=1)

        self.widget_config = ctk.CTkFrame(self)
        self.widget_config.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.widget_config_label = ctk.CTkLabel(self.widget_config, text="Configuración de widget")
        self.widget_config_label.pack(pady=5)

        self.config_space = ctk.CTkFrame(self.widget_config)
        self.config_space.pack(fill="both", expand=True, padx=5, pady=5)

    def show_widget_config(self, widget):
        """Mostrar las configuraciones del widget seleccionado."""
        for child in self.config_space.winfo_children():
            child.destroy()
        widget.focus_set()
        widget_properties = global_properties

        widget_type = widget.__class__.__name__
        logging.info(f"Mostrando configuración para widget: {widget_type}")
        ctk.CTkLabel(self.config_space, text=f"Tipo: {widget_type}").pack(pady=5)

        def create_property_entry(prop):
            ctk.CTkLabel(self.config_space, text=f"{prop.capitalize()}:").pack()
            entry = ctk.CTkEntry(self.config_space)
            value = widget.cget(prop)
            entry.insert(0, str(value))
            entry.pack()

            def update_property(event):
                try:
                    if prop == "font":
                        font_value = entry.get()
                        font_parts = font_value.rsplit(" ", 1)  
                        if len(font_parts) == 2 and font_parts[1].isdigit():
                            font_name = font_parts[0]
                            font_size = int(font_parts[1])
                            widget.configure(**{prop: (font_name, font_size)})
                            logging.info(f"Propiedad '{prop}' actualizada a: ({font_name}, {font_size})")
                        else:
                            raise ValueError(f"El valor '{font_value}' no es válido para 'font'. Formato esperado: 'Arial 20'")
                    else:
                        widget.configure(**{prop: entry.get()})
                        logging.info(f"Propiedad '{prop}' actualizada a: {entry.get()}")
                except Exception as e1:
                    try:
                        widget.configure(**{prop: int(entry.get())})
                        logging.info(f"Propiedad '{prop}' actualizada a: {int(entry.get())}")
                    except ValueError as e2:
                        logging.error(f"Error al actualizar '{prop}': {e2}. Valor ingresado: {entry.get()}")

            entry.bind("<KeyRelease>", update_property)

        for prop in widget_properties.get(widget_type, []):
            create_property_entry(prop)

        # Manejo de posición (x, y)
        ctk.CTkLabel(self.config_space, text="Posición (x, y):").pack(pady=5)
        position_frame = ctk.CTkFrame(self.config_space)
        position_frame.pack(pady=5)

        x_entry = ctk.CTkEntry(position_frame, width=50)
        x_entry.insert(0, widget.winfo_x())
        x_entry.pack(side="left", padx=2)

        y_entry = ctk.CTkEntry(position_frame, width=50)
        y_entry.insert(0, widget.winfo_y())
        y_entry.pack(side="left", padx=2)

        def update_position(event):
            try:
                new_x = int(x_entry.get())
                new_y = int(y_entry.get())
                widget.place(x=new_x, y=new_y)
                logging.info(f"Posición actualizada a: ({new_x}, {new_y})")
            except ValueError:
                logging.warning("Posición inválida. Por favor, ingresa valores numéricos.")

        def update_positions(new_x, new_y):
            x_entry.delete(0, "end")
            x_entry.insert(0, new_x)
            y_entry.delete(0, "end")
            y_entry.insert(0, new_y)

        self.update_positions = update_positions

        x_entry.bind("<KeyRelease>", update_position)
        y_entry.bind("<KeyRelease>", update_position)

        ctk.CTkButton(
            self.config_space,
            text="Borrar widget",
            command=lambda: self.delete_widget(widget),
            **button_style
        ).pack(pady=15)

    def delete_widget(self, widget):
        if widget.__class__.__name__ != 'VirtualWindow':
            app.virtual_window.delete_widget(widget)
            for child in self.config_space.winfo_children():
                child.destroy()
            app.cross_update_treeview()
        else:
            logging.error("No se puede borrar la virtual window")

class RightSidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent, virtual_window):
        super().__init__(parent, width=200)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background= "#131313", foreground= "#fafafa", font=("Arial", 12, "bold"), relief = "flat")
        style.configure("Treeview", background=  "#131313", foreground= "#fafafa", fieldbackground="#131313", borderwidth=0, relief = "flat")
        style.map("Treeview.Heading", background=[("selected",  "#252525"), ("active",  "#252525")])
        self.grid_columnconfigure(0, weight=1)
        self.virtual_window = virtual_window

        # Diccionario para contar widgets por tipo
        self.widget_counters = {}

        ctk.CTkLabel(self, text="Widgets disponibles").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        for i, widget in enumerate(widgets):
            btn = ctk.CTkButton(
                self,
                text=widget,
                command=lambda w=widget: self.add_widget(w),
                **button_style
            )
            btn.grid(row=i + 1, column=0, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self, text="Esquema de widgets").grid(row=len(widgets) + 1, column=0, padx=5, pady=5, sticky="w")

        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=len(widgets) + 2, column=0, padx=5, pady=5, sticky="nsew")

        self.tree.column("#0", width=180, stretch=True)
        self.tree.heading("#0", text="Widgets")

        self.widget_tree = {}

    def add_widget(self, widget):
        """
        Añade un widget a la ventana virtual y actualiza el esquema del TreeView.
        """
        widget_type = widget

        self.virtual_window.add_widget(widget_type)
        self.update_treeview()

    def detect_hierarchy(self, parent_widget=None):
        """
        Detecta automáticamente la jerarquía de widgets dentro de la ventana virtual.
        :param parent_widget: El widget padre desde donde comenzar la detección (None para raíz).
        :return: Lista [(widget, parent_widget), ...] con la jerarquía detectada.
        """
        hierarchy = []
        container = parent_widget or self.virtual_window

        for child in container.winfo_children():
            hierarchy.append((child, parent_widget))
            hierarchy.extend(self.detect_hierarchy(child))

        return hierarchy

    def update_treeview(self):
        """
        Actualiza el esquema del TreeView basándose en la jerarquía detectada automáticamente.
        """
        widget_hierarchy = self.detect_hierarchy()

        self.tree.delete(*self.tree.get_children())
        self.widget_tree.clear()

        for widget, parent_widget in widget_hierarchy:
            widget_name = widget._name if hasattr(widget, "_name") else widget.__class__.__name__
            widget_id = id(widget)

            if parent_widget:
                parent_id = id(parent_widget)
                parent_tree_id = self.widget_tree.get(parent_id)
                tree_id = self.tree.insert(parent_tree_id, "end", text=f"{widget_name}")
            else:
                tree_id = self.tree.insert("", "end", text=widget_name)

            self.widget_tree[widget_id] = tree_id

class Toolbar(ctk.CTkFrame):
    def __init__(self, parent, virtual_window, rightbar):
        super().__init__(parent, height=40, fg_color="#333333")
        self.virtual_window = virtual_window
        self.right_bar = rightbar
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        export_button = ctk.CTkButton(self, text="Exportar a .py", command=self.export_to_file, **button_style)
        export_button.pack(pady=5, padx=5, side="right")

        import_button = ctk.CTkButton(self, text="Importar desde .py", command=self.import_from_file, **button_style)
        import_button.pack(pady=5, padx=5, side="right")
        
        self.info_label = ctk.CTkLabel(self, text="Ok")
        self.info_label.pack(pady=5, padx=5, side="left")
        
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=5, padx=5, side="left")
        self.progress.set(0)
        self.progress.pack_forget()

        log_handler = TkinterLogHandler(self.info_label)
        log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(log_handler)
        
    def progress_set_value(self, value):
        self.progress.set(value)
        
        if value < 1.0:
            self.progress.pack(pady=5, padx=5, side="left")
        else:
            self.after(3000, self.hide_progress_bar)

    def hide_progress_bar(self):
        if self.progress.get() == 1.0: 
            self.progress.pack_forget()  

    def export_to_file(self):
        if file_path := filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Guardar como",
        ):
            self.virtual_window.export_to_file(file_path)

    def import_from_file(self):
        if file_path := filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")], title="Abrir archivo"
        ):
            self.virtual_window.import_from_file(file_path)
            self.right_bar.update_treeview()

class TkinterLogHandler(logging.Handler):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.setLevel(logging.WARNING)

    def emit(self, record):
        if record.levelno >= self.level:
            log_entry = self.format(record)
            self.label.configure(text=log_entry)
            self.label.after(3000, lambda: self.label.configure(text="Ok"))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CTk Interface")
        self.geometry("1000x600")
        self._set_appearance_mode("dark")  

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.virtual_window = ctk.CTkFrame(self, fg_color='white', bg_color='lightgrey', width=800, height=500)
        self.virtual_window.place(x=50, y=50)

        entry_params = {
            'fg_color': ['#F9F9FA', '#343638'],
            'border_width': 2,
            'border_color': ['#979DA2', '#565B5E'],
            'text_color': ['gray10', '#DCE4EE'],
            'width': 140,
            'height': 28
        }

        self.h = ctk.CTkEntry(self.virtual_window, placeholder_text="500", **entry_params)
        self.h.place(x=100, y=129)

        self.w = ctk.CTkEntry(self.virtual_window, placeholder_text="800", **entry_params)
        self.w.place(x=100, y=166)

        label_params = {
            'textvariable': '',
            'fg_color': 'transparent',
            'corner_radius': 0,
            'text_color': 'black',
            'width': 0,
            'height': 28,
            'anchor': 'center',
            'compound': 'center',
            'justify': 'center'
        }

        ctk.CTkLabel(self.virtual_window, text='Altura:', **label_params).place(x=35, y=129)
        ctk.CTkLabel(self.virtual_window, text='Anchura:', **label_params).place(x=37, y=166)
        ctk.CTkLabel(self.virtual_window, text='Nuevo proyecto', font=('Arial', 35), **label_params).place(x=35, y=32)
        ctk.CTkLabel(self.virtual_window, text='Configuracion de ventana:', font=('Arial', 18), **label_params).place(x=35, y=89)

        self.is_resizable=ctk.CTkCheckBox(self.virtual_window, text='Resizable', textvariable=None, onvalue=1, 
                         offvalue=0, fg_color='#2E2E2E', text_color='#2E2E2E', width=100, 
                         height=24, hover_color='#3A3A3A', border_width=3, 
                         border_color='#5A5A5A', checkmark_color=['#DCE4EE', 'gray90'])
        self.is_resizable.place(x=35, y=216)

        ctk.CTkButton(self.virtual_window, text='Aceptar', 
                      command=lambda: self.clear_virtual_window(self.h.get(), self.w.get(), {"is_resizable":self.is_resizable.get()}), 
                      fg_color='#2E2E2E', width=140, height=28, border_width=2, 
                      border_color='#5A5A5A', hover_color='#3A3A3A', 
                      text_color=['#DCE4EE', '#DCE4EE'], border_spacing=2, 
                      corner_radius=8).place(x=645, y=459)

    def clear_virtual_window(self, h, w, bools):
        """Elimina todos los widgets dentro de self.virtual_window."""
        for widget in self.virtual_window.winfo_children():
            widget.destroy()
        self.virtual_window.destroy()
        self.create_ui(int(h), int(w), bools)
        
    def create_ui(self, vw_height, vw_width, bools):
        self.left_sidebar = LeftSidebar(self)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew")

        self.central_canvas = ctk.CTkCanvas(self, bg="black")
        self.central_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.virtual_window = VirtualWindow(self.central_canvas, self.left_sidebar, self, bools, width=vw_width, height=vw_height)
        self.central_canvas.create_window((50, 50), anchor="nw", window=self.virtual_window)

        self.right_sidebar = RightSidebar(self, self.virtual_window)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")

        self.toolbar = Toolbar(self, self.virtual_window, self.right_sidebar)
        self.toolbar.grid(row=1, column=0, columnspan=3, sticky="nsew")

    def cross_update_treeview(self):
        self.right_sidebar.update_treeview()

    def cross_update_progressbar(self, val:float):
        self.toolbar.progress_set_value(val)
        
    def cross_update_text_info(self, val:str):
        self.toolbar.info_label.configure(text=val)
        self.after(3000, lambda:self.toolbar.info_label.configure(text='Ok.'))
        
if __name__ == "__main__":
    app = App()
    app.mainloop()