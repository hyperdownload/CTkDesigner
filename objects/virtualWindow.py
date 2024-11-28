import customtkinter as ctk
from data.variable import *
import tkinter as tk
import logging
import ast

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

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
        logging.info(f"VirtualWindow inicializada con dimensiones {self.cget("width")}x{self.cget("height")} y canvas configurado.")
        
    def add_widget(self, widget_type):
        """Agrega un widget al VirtualWindow."""
        logging.debug(f"Intentando agregar widget de tipo '{widget_type}'.")
        if widget := self.create_widget(widget_type):
            self._extracted_from_create_and_place_widget_5(widget, 100, 100)
            logging.info(f"Widget de tipo '{widget_type}' agregado en posición inicial (100, 100).")
        else:
            logging.warning(f"Fallo al agregar widget de tipo '{widget_type}'.")

    def create_widget(self, widget_type, **kwargs):
        """Crea un widget basado en el tipo proporcionado."""
        logging.debug(f"Creando widget de tipo '{widget_type}' con argumentos: {kwargs}.")
        if widget_class := widget_classes.get(widget_type):
            widget = widget_class(self, **kwargs)
            logging.info(f"Widget '{widget_type}' creado con éxito.")
            return widget
        logging.error(f"'{widget_type}' no es un tipo de widget válido.")
        return None
    
    def export_to_file(self, file_path):
        logging.debug(f"Intentando exportar archivo a {file_path}.")
        window_params = {
            "fg_color": self.cget("fg_color"),
            "bg_color": self.cget("bg_color"),
            "width": self.cget("width"),
            "height": self.cget("height"),
        }
        logging.debug("Cargando parametros de la ventana...")
        window_params_string = ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())

        logging.debug("Procediendo a crear las lineas...")
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
                        logging.info(f"{widget.cget(value)}")
            else:
                logging.warning(f"Error: Los parámetros del widget son 'None' para {widget}")
            params_string = ", ".join(params)
            lines.append(f"        ctk.{widget_type}(self.virtual_window, {params_string}).place(x={x}, y={y})")

        lines.extend(
            (
                "",
                "if __name__ == '__main__':",
                "    app = App()",
                "    app.mainloop()",
            )
        )
        logging.info("Lineas creadas exitosamente.\n Escribiendo archivo...")
        with open(file_path, "w", encoding="utf-8") as file:
            logging.info("\n".join(lines))
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

            #Centrado vertical
            if widget_center_x == child_center_x:
                self.create_guide_line(child_center_x, 0, child_center_x, self.winfo_height(), "green")
            elif abs(widget_center_x - child_center_x) <= 5:
                self.create_guide_line(child_center_x, 0, child_center_x, self.winfo_height(), "red")

            #Centrado horizontal
            if widget_center_y == child_center_y:
                self.create_guide_line(0, child_center_y, self.winfo_width(), child_center_y, "green")
            elif abs(widget_center_y - child_center_y) <= 5:
                self.create_guide_line(0, child_center_y, self.winfo_width(), child_center_y, "red")

            #Bordes izquierdo y derecho
            if new_x == child_x:
                self.create_guide_line(child_x, 0, child_x, self.winfo_height(), "green")
            elif abs(new_x - child_x) <= 5:
                self.create_guide_line(child_x, 0, child_x, self.winfo_height(), "red")

            if new_x + widget_width == child_x + child_width:
                self.create_guide_line(child_x + child_width, 0, child_x + child_width, self.winfo_height(), "green")
            elif abs(new_x + widget_width - (child_x + child_width)) <= 5:
                self.create_guide_line(child_x + child_width, 0, child_x + child_width, self.winfo_height(), "red")

            #Bordes superior e inferior
            if new_y == child_y:
                self.create_guide_line(0, child_y, self.winfo_width(), child_y, "green")
            elif abs(new_y - child_y) <= 5:
                self.create_guide_line(0, child_y, self.winfo_width(), child_y, "red")

            if new_y + widget_height == child_y + child_height:
                self.create_guide_line(0, child_y + child_height, self.winfo_width(), child_y + child_height, "green")
            elif abs(new_y + widget_height - (child_y + child_height)) <= 5:
                self.create_guide_line(0, child_y + child_height, self.winfo_width(), child_y + child_height, "red")

    def create_guide_line(self, x1, y1, x2, y2, color):
        """Crea una línea guía en el canvas."""
        self.guide_canvas.create_line(x1, y1, x2, y2, fill=color, dash=(4, 2), width=1)

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
        self.clean_virtual_window()
        logging.info(f"Iniciando la importación de widgets desde el archivo: {file_path}")
        try:
            code = self.read_file(file_path)
            if code is None:
                logging.error("No se pudo leer el archivo, abortando la importación.")
                return

            tree = ast.parse(code)
            app_class = self.find_app_class(tree)
            if not app_class:
                logging.error("No se encontró la clase 'App', abortando la importación.")
                return

            if generic_widget_creator := self.find_generic_widget_creator(app_class):
                logging.info("Se encontró la función 'generic_widget_creator', procesando llamadas de widgets.")
                self.process_widget_calls(generic_widget_creator)
            else:
                logging.error("No se encontró la función 'generic_widget_creator', abortando la importación.")
            logging.info("Importación completada exitosamente.")
        except Exception as e:
            logging.error(f"Error durante la importación: {e}")

    def clean_virtual_window(self):
        """Limpia el contenido del VirtualWindow."""
        logging.info("Limpiando el contenido del VirtualWindow.")
        try:
            self.clear_guides()
            for widget in self.widgets:
                self.left_sidebar.delete_widget(widget)
            logging.info("El contenido del VirtualWindow fue borrado correctamente.")
        except Exception as e:
            logging.error(f"Error al limpiar el contenido del VirtualWindow: {e}")

    def read_file(self, file_path):
        """Lee el contenido del archivo especificado."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                logging.debug(f"Archivo {file_path} leído correctamente.")
                return file.read()
        except Exception as e:
            logging.error(f"Error al leer el archivo {file_path}: {e}")
            return None

    def find_app_class(self, tree):
        """Encuentra la clase 'App' en el AST."""
        app_class = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App"), None)
        if not app_class:
            logging.warning("No se encontró ninguna clase llamada 'Aplicación'.")
        else:
            logging.debug("Clase 'App' encontrada en el AST.")
        return app_class

    def find_generic_widget_creator(self, app_class):
        """Encuentra la función 'generic_widget_creator' en la clase 'App'."""
        generic_widget_creator = next(
            (subnode for subnode in app_class.body if isinstance(subnode, ast.FunctionDef) and subnode.name == "generic_widget_creator"),
            None,
        )
        if not generic_widget_creator:
            logging.warning("No se encontró ninguna función denominada 'generic_widget_creator'.")
        else:
            logging.debug("Función 'generic_widget_creator' encontrada en la clase 'App'.")
        return generic_widget_creator

    def process_widget_calls(self, generic_widget_creator):
        """Procesa llamadas de widgets en la función 'generic_widget_creator'."""
        logging.info("Procesando llamadas de widgets en 'generic_widget_creator'.")
        for stmt in generic_widget_creator.body:
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
                logging.debug("Declaración ignorada, no es una llamada de widget.")
                continue

            widget_call = stmt.value
            if not (isinstance(widget_call.func, ast.Attribute) and isinstance(widget_call.func.value, ast.Call)):
                logging.debug("Llamada de widget ignorada, no es una llamada válida.")
                continue

            widget_type = widget_call.func.value.func.attr
            widget_method = widget_call.func.attr

            if widget_method != "place":
                logging.debug(f"Método '{widget_method}' ignorado, solo se procesan métodos 'place'.")
                continue

            widget_args, placement_args = self.extract_widget_args(widget_call)
            x = placement_args.get("x", 0)
            y = placement_args.get("y", 0)

            logging.debug(f"Creando y colocando widget de tipo '{widget_type}' en ({x}, {y}).")
            self.create_and_place_widget(widget_type, widget_args, x, y)

    def extract_widget_args(self, widget_call):
        """Extrae argumentos de widget y ubicación de la llamada del widget."""
        logging.debug("Extrayendo argumentos de widget y ubicación.")
        widget_args = {
            kw.arg: ast.literal_eval(kw.value)
            for kw in widget_call.func.value.keywords
            if kw.arg in global_properties.get(widget_call.func.value.func.attr, [])
        }

        placement_args = {
            kw.arg: ast.literal_eval(kw.value)
            for kw in widget_call.keywords
        }
        logging.debug(f"Argumentos de widget extraídos: {widget_args}, Argumentos de ubicación: {placement_args}.")
        return widget_args, placement_args

    def create_and_place_widget(self, widget_type, widget_args, x, y):
        """Crea y coloca el widget y actualiza la lista de widgets."""
        logging.debug(f"Intentando crear el widget del tipo '{widget_type}' con argumentos: {widget_args}.")
        if widget := self.create_widget(widget_type, **widget_args):
            self._extracted_from_create_and_place_widget_5(widget, x, y)
            logging.info(f"Widget del tipo '{widget_type}' ubicado en ({x}, {y}).")
        else:
            logging.error(f"No se pudo crear el widget del tipo '{widget_type}'.")

    def _extracted_from_create_and_place_widget_5(self, widget, x, y):
        widget.place(x=x, y=y)
        self.make_widget_movable(widget)
        self.make_widget_selectable(widget)
        self.widgets.append(widget)
