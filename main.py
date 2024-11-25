import customtkinter as ctk
import tkinter as tk
from objects.virtualWindow import VirtualWindow
import time
import threading
from tkinter import filedialog
from data.variable import *
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
        # Limpiar configuraciones previas
        for child in self.config_space.winfo_children():
            child.destroy()

        widget_properties = global_properties

        widget_type = widget.__class__.__name__
        ctk.CTkLabel(self.config_space, text=f"Tipo: {widget_type}").pack(pady=5)

        # Crear entradas para las propiedades
        def create_property_entry(prop):
            ctk.CTkLabel(self.config_space, text=f"{prop.capitalize()}:").pack()
            entry = ctk.CTkEntry(self.config_space)
            value = widget.cget(prop)
            entry.insert(0, str(value))
            entry.pack()

            def update_property():
                try:
                    widget.configure(**{prop: entry.get()})
                except:
                    widget.configure(**{prop: int(entry.get())})
                finally:
                    print("Hubo un error en el tipo de dato, cambiando a int.")

            ctk.CTkButton(self.config_space, text=f"Actualizar {prop}", command=update_property).pack(pady=5)

        for prop in widget_properties.get(widget_type, []):
            create_property_entry(prop)

        # Configuración de posición
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
                
            except ValueError:
                print("Las coordenadas no son válidas.")
                
        def update_position_loop():
            while True:
                try:
                    x_entry.delete(0, tk.END)
                    y_entry.delete(0, tk.END)
                    
                    x_entry.insert(0, widget.winfo_x())
                    y_entry.insert(0, widget.winfo_y())
                except ValueError:
                    pass  
                time.sleep(0.1) 

        update_thread = threading.Thread(target=update_position_loop, daemon=True)
        update_thread.start()
        
        x_entry.bind("<KeyRelease>", update_position)
        y_entry.bind("<KeyRelease>", update_position)

        ctk.CTkButton(self.config_space, text="Borrar widget", command=lambda: self.delete_widget(widget)).pack(pady=15)

    def delete_widget(self, widget):
        if widget.__class__.__name__ != 'VirtualWindow':
            app.virtual_window.delete_widget(widget)
            for child in self.config_space.winfo_children():
                child.destroy()
        else:
            print("No se puede borrar la virtual window")

class RightSidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent, virtual_window):
        super().__init__(parent, width=200)
        self.grid_columnconfigure(0, weight=1)
        self.virtual_window = virtual_window

        widgets = [
            "CTkButton", "CTkLabel", "CTkEntry", "CTkCheckBox",
            "CTkRadioButton", "CTkComboBox", "CTkSlider", "CTkProgressBar",
            "CTkTextbox", "CTkTabview", "CTkSegmentedButton", "CTkSwitch"
        ]

        for i, widget in enumerate(widgets):
            btn = ctk.CTkButton(
                self,
                text=widget,
                command=lambda w=widget: self.virtual_window.add_widget(w),
            )
            btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")

class Toolbar(ctk.CTkFrame):
    def __init__(self, parent, virtual_window):
        super().__init__(parent, height=40, fg_color="gray")
        self.virtual_window = virtual_window
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        export_button = ctk.CTkButton(self, text="Exportar a .py", command=self.export_to_file)
        export_button.pack(pady=5, padx=5, side="right")

    def export_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Guardar como"
        )
        if file_path:
            self.virtual_window.export_to_file(file_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CTk Interface")
        self.geometry("1000x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_sidebar = LeftSidebar(self)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew")

        self.central_canvas = ctk.CTkCanvas(self, bg="black")
        self.central_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.virtual_window = VirtualWindow(self.central_canvas, self.left_sidebar)
        self.central_canvas.create_window((0, 0), anchor="nw", window=self.virtual_window)

        self.right_sidebar = RightSidebar(self, self.virtual_window)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")

        self.toolbar = Toolbar(self, self.virtual_window)
        self.toolbar.grid(row=1, column=0, columnspan=3, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
