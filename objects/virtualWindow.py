import customtkinter as ctk
from data.variable import *
import tkinter as tk
import ast
class VirtualWindow(ctk.CTkFrame):
    def __init__(self, parent, left_sidebar):
        super().__init__(parent, width=800, height=500, bg_color="lightgrey", fg_color="white")
        self.left_sidebar = left_sidebar
        self.widgets = []
        
        self.guide_canvas = tk.Canvas(self, width=800, height=500, highlightthickness=0)
        self.guide_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.pack_propagate(False)
        self.make_widget_selectable(self)
        self.make_widget_selectable(self.guide_canvas)
        
    def add_widget(self, widget_type):
        """Agrega un widget al VirtualWindow."""
        widget = self.create_widget(widget_type)
        if widget:
            widget.place(x=100, y=100)  
            self.make_widget_movable(widget)
            self.make_widget_selectable(widget)
            self.widgets.append(widget)

    def create_widget(self, widget_type, **kwargs):
        """Crea un widget basado en el tipo proporcionado."""
        widget_class = widget_classes.get(widget_type)
        if widget_class:
            return widget_class(self, **kwargs)  
        print(f"Advertencia: '{widget_type}' no es un tipo de widget válido.")
        return None
    
    def export_to_file(self, file_path):
        window_params = {
            "fg_color": self.cget("fg_color"),
            "bg_color": self.cget("bg_color"),
            "width": self.cget("width"),
            "height": self.cget("height"),
        }

        window_params_string = ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())

        lines = [
            "#Codigo generado automaticamente desde una VirtualWindow",
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
            "        self.generic_widget_creator()",
            ""
            "    def generic_widget_creator(self):",
            
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
        """Hace que un widget sea movible dentro del VirtualWindow con líneas guía."""
        def start_move(event):
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y
            self.clear_guides()

        def do_move(event):
            new_x = widget.winfo_x() + event.x - widget._drag_start_x
            new_y = widget.winfo_y() + event.y - widget._drag_start_y
            widget.place(x=new_x, y=new_y)

            self.clear_guides()
            self.draw_guides(widget, new_x, new_y)

            if hasattr(self.left_sidebar, 'update_positions'):
                self.left_sidebar.update_positions(new_x, new_y)

        def stop_move(event):
            self.clear_guides()

        widget.bind("<Button-1>", start_move)
        widget.bind("<B1-Motion>", do_move)
        widget.bind("<ButtonRelease-1>", stop_move)

    def draw_guides(self, widget, new_x, new_y):
        """Dibuja líneas guía en el canvas para ayudar con la alineación."""
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()

        widget_center_x = new_x + widget_width // 2
        widget_center_y = new_y + widget_height // 2

        for child in self.widgets:
            if child == widget:
                continue

            child_x = child.winfo_x()
            child_y = child.winfo_y()
            child_width = child.winfo_width()
            child_height = child.winfo_height()
            child_center_x = child_x + child_width // 2
            child_center_y = child_y + child_height // 2

            if abs(widget_center_x - child_center_x) <= 5:
                self.create_guide_line(child_center_x, 0, child_center_x, self.winfo_height())
            if abs(widget_center_y - child_center_y) <= 5:
                self.create_guide_line(0, child_center_y, self.winfo_width(), child_center_y)

            if abs(new_x - child_x) <= 5:
                self.create_guide_line(child_x, 0, child_x, self.winfo_height())
            if abs(new_x + widget_width - (child_x + child_width)) <= 5:
                self.create_guide_line(child_x + child_width, 0, child_x + child_width, self.winfo_height())
            if abs(new_y - child_y) <= 5:
                self.create_guide_line(0, child_y, self.winfo_width(), child_y)
            if abs(new_y + widget_height - (child_y + child_height)) <= 5:
                self.create_guide_line(0, child_y + child_height, self.winfo_width(), child_y + child_height)

    def create_guide_line(self, x1, y1, x2, y2):
        """Crea una línea guía en el canvas."""
        self.guide_canvas.create_line(x1, y1, x2, y2, fill="red", dash=(4, 2), width=1)

    def clear_guides(self):
        """Elimina las líneas guía del canvas."""
        self.guide_canvas.delete("all")

    def make_widget_selectable(self, widget):
        """Hace que un widget sea seleccionable con clic derecho."""
        def select_widget(event):
            if widget.__class__.__name__=="Canvas":
                widget.bind("<Button-3>", lambda:select_widget(self))
                self.left_sidebar.show_widget_config(self)
            else:
                self.left_sidebar.show_widget_config(widget)
        widget.bind("<Button-3>", select_widget)
        widget.bind("<Control-Delete>", select_widget)

    def delete_widget(self, widget):
        """Borra un widget del VirtualWindow."""
        widget.destroy()
        self.widgets.remove(widget)
        
    def import_from_file(self, file_path):
        """Importa widgets desde un archivo Python exportado, incluidos sus parámetros."""
        import ast

        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        try:
            tree = ast.parse(code)  
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == "App":
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef) and subnode.name == "generic_widget_creator":
                            for stmt in subnode.body:
                                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                    widget_call = stmt.value

                                    if isinstance(widget_call.func, ast.Attribute):
                                        if isinstance(widget_call.func.value, ast.Call):
                                            widget_type = widget_call.func.value.func.attr 
                                            widget_method = widget_call.func.attr 

                                            if widget_method == "place":  
                                                widget_args = {
                                                    kw.arg: ast.literal_eval(kw.value)
                                                    for kw in widget_call.func.value.keywords
                                                    if kw.arg in global_properties.get(widget_type, [])
                                                }

                                                placement_args = {
                                                    kw.arg: ast.literal_eval(kw.value)
                                                    for kw in widget_call.keywords
                                                }
                                                x = placement_args.get("x", 0)
                                                y = placement_args.get("y", 0)

                                                widget = self.create_widget(widget_type, **widget_args)
                                                if widget:
                                                    widget.place(x=x, y=y)
                                                    self.make_widget_movable(widget)
                                                    self.make_widget_selectable(widget)
                                                    self.widgets.append(widget)
            print("Importación completada exitosamente.")
        except Exception as e:
            print(f"Error al importar el archivo: {e}")
