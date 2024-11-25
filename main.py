import customtkinter as ctk
import tkinter as tk
from objects.virtualWindow import VirtualWindow
from tkinter import filedialog
from data.variable import *
import tkinter.ttk as ttk

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

        widget_properties = global_properties

        widget_type = widget.__class__.__name__
        ctk.CTkLabel(self.config_space, text=f"Tipo: {widget_type}").pack(pady=5)

        def create_property_entry(prop):
            ctk.CTkLabel(self.config_space, text=f"{prop.capitalize()}:").pack()
            entry = ctk.CTkEntry(self.config_space)
            value = widget.cget(prop)
            entry.insert(0, str(value))
            entry.pack()

            def update_property(event):
                try:
                    widget.configure(**{prop: entry.get()})
                except:
                    try:
                        widget.configure(**{prop: int(entry.get())})
                    except ValueError:
                        print(f"Error: el valor para '{prop}' no es válido.")
            
            entry.bind("<KeyRelease>", update_property)

        for prop in widget_properties.get(widget_type, []):
            create_property_entry(prop)

        ctk.CTkLabel(self.config_space, text="Posición (x, y):").pack(pady=5)
        position_frame = ctk.CTkFrame(self.config_space)
        position_frame.pack(pady=5)

        x_entry = ctk.CTkEntry(position_frame, width=50)
        x_entry.insert(0, widget.winfo_x())
        x_entry.pack(side="left", padx=2)

        y_entry = ctk.CTkEntry(position_frame, width=50)
        y_entry.insert(0, widget.winfo_y())
        y_entry.pack(side="left", padx=2)

        # Actualizar posición dinámicamente
        def update_position(event):
            try:
                new_x = int(x_entry.get())
                new_y = int(y_entry.get())
                widget.place(x=new_x, y=new_y)
            except ValueError:
                print("Las coordenadas no son válidas.")

        def update_positions(new_x, new_y):
            x_entry.delete(0, "end")
            x_entry.insert(0, new_x)
            y_entry.delete(0, "end")
            y_entry.insert(0, new_y)

        self.update_positions = update_positions

        x_entry.bind("<KeyRelease>", update_position)
        y_entry.bind("<KeyRelease>", update_position)

        ctk.CTkButton(self.config_space, text="Borrar widget", command=lambda: self.delete_widget(widget), **button_style).pack(pady=15)

    def delete_widget(self, widget):
        if widget.__class__.__name__ != 'VirtualWindow':
            app.virtual_window.delete_widget(widget)
            for child in self.config_space.winfo_children():
                child.destroy()
            app.cross_update_treeview()
        else:
            print("No se puede borrar la virtual window")

class RightSidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent, virtual_window):
        super().__init__(parent, width=200)
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

    def get_unique_name(self, widget_type):
        """
        Genera un nombre único para un widget basado en su tipo.
        """
        # Inicializa el contador si no existe
        if widget_type not in self.widget_counters:
            self.widget_counters[widget_type] = 0

        # Incrementa el contador y genera el nombre
        count = self.widget_counters[widget_type]
        unique_name = f"{widget_type}{count}" if count > 0 else widget_type
        self.widget_counters[widget_type] += 1

        return unique_name

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
        container = parent_widget if parent_widget else self.virtual_window 

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
        super().__init__(parent, height=40, fg_color="gray")
        self.virtual_window = virtual_window
        self.right_bar = rightbar
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        export_button = ctk.CTkButton(self, text="Exportar a .py", command=self.export_to_file, **button_style)
        export_button.pack(pady=5, padx=5, side="right")

        import_button = ctk.CTkButton(self, text="Importar desde .py", command=self.import_from_file, **button_style)
        import_button.pack(pady=5, padx=5, side="right")

    def export_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Guardar como"
        )
        if file_path:
            self.virtual_window.export_to_file(file_path)

    def import_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")],
            title="Abrir archivo"
        )
        if file_path:
            self.virtual_window.import_from_file(file_path)
            self.right_bar.update_treeview()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CTk Interface")
        self.geometry("1000x600")
        self._set_appearance_mode("dark")  

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_sidebar = LeftSidebar(self)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew")

        self.central_canvas = ctk.CTkCanvas(self, bg="black")
        self.central_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.virtual_window = VirtualWindow(self.central_canvas, self.left_sidebar)
        self.central_canvas.create_window((50, 50), anchor="nw", window=self.virtual_window)

        self.right_sidebar = RightSidebar(self, self.virtual_window)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")

        self.toolbar = Toolbar(self, self.virtual_window, self.right_sidebar)
        self.toolbar.grid(row=1, column=0, columnspan=3, sticky="nsew")

    def cross_update_treeview(self):
        self.right_sidebar.update_treeview()

if __name__ == "__main__":
    app = App()
    app.mainloop()