import customtkinter as ctk
from data.variable import *
class VirtualWindow(ctk.CTkFrame):
    def __init__(self, parent, left_sidebar):
        super().__init__(parent, width=800, height=500, bg_color="lightgrey", fg_color="white")
        self.left_sidebar = left_sidebar
        self.widgets = []
        
        self.pack_propagate(False)
        self.make_widget_selectable(self)

    def add_widget(self, widget_type):
        """Agregar un widget al VirtualWindow."""
        widget = self.create_widget(widget_type)
        if widget:
            widget.place(x=100, y=100)  # Posición inicial predeterminada
            self.make_widget_movable(widget)
            self.make_widget_selectable(widget)
            self.widgets.append(widget)

    def create_widget(self, widget_type):
        """Crear un widget basado en el tipo proporcionado."""
        widget_classes = {
            "CTkButton": ctk.CTkButton,
            "CTkLabel": ctk.CTkLabel,
            "CTkEntry": ctk.CTkEntry,
            "CTkCheckBox": ctk.CTkCheckBox,
            "CTkRadioButton": ctk.CTkRadioButton,
            "CTkComboBox": ctk.CTkComboBox,
            "CTkSlider": ctk.CTkSlider,
            "CTkProgressBar": ctk.CTkProgressBar,
            "CTkTextbox": ctk.CTkTextbox,
            "CTkTabview": ctk.CTkTabview,
            "CTkSegmentedButton": ctk.CTkSegmentedButton,
            "CTkSwitch": ctk.CTkSwitch,
        }
        return widget_classes.get(widget_type, lambda: None)(self)
    
    def export_to_file(self, file_path):
        window_params = {
            "fg_color": self.cget("fg_color"),
            "bg_color": self.cget("bg_color"),
            "width": self.cget("width"),
            "height": self.cget("height"),
        }

        window_params_string = ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())

        lines = [
            "import customtkinter as ctk",
            "",
            "class App(ctk.CTk):",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.geometry('{self.winfo_width()}x{self.winfo_height()}')",
            "        self.title('Exported Virtual Window')",
            "",
            f"        self.virtual_window = ctk.CTkFrame(self, {window_params_string})",
            "        self.virtual_window.pack(expand=True, fill='both')",
            ""
        ]

        for widget in self.widgets:
            widget_type = widget.__class__.__name__
            widget_params = global_properties.get(widget.__class__.__name__)

            x = widget.winfo_x()
            y = widget.winfo_y()

            params = []
            if widget_params is not None:
                for value in widget_params:
                    if value not in (None, "", "default"):  
                        params.append(f"{value}={repr(widget.cget(value))}")
            else:
                print(f"Error: Los parámetros del widget son 'None' para {widget}")
            params_string = ", ".join(params)
            lines.append(f"        ctk.{widget_type}(self.virtual_window, {params_string}).place(x={x}, y={y})")

        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    app = App()")
        lines.append("    app.mainloop()")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

    def make_widget_movable(self, widget):
        """Hacer que un widget sea movible dentro del VirtualWindow."""
        def start_move(event):
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y

        def do_move(event):
            new_x = widget.winfo_x() + event.x - widget._drag_start_x
            new_y = widget.winfo_y() + event.y - widget._drag_start_y
            widget.place(x=new_x, y=new_y)

        widget.bind("<Button-1>", start_move)
        widget.bind("<B1-Motion>", do_move)

    def make_widget_selectable(self, widget):
        """Hacer que un widget sea seleccionable con clic derecho."""
        def select_widget(event):
            self.left_sidebar.show_widget_config(widget)

        widget.bind("<Button-3>", select_widget)
        widget.bind("<Control-Delete>", select_widget)

    def delete_widget(self, widget):
        """Borrar un widget del VirtualWindow."""
        widget.destroy()
        self.widgets.remove(widget)
        
    def export(self):
        pass