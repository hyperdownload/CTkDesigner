import logging
import tkinter.ttk as ttk
import customtkinter as ctk
from data.variable import *
from objects.tooltip import *
from tkinter import filedialog
from functions.import_widget import *
from objects.codeBox import CTkCodeBox
from translations.translations import *
from translations.translator import Translator
from functions.create_widget_animation import *
from objects.virtualWindow import VirtualWindow

def validate_input(value):
    """Update the treeview in the right sidebar.

    This method triggers an update of the treeview widget within the right sidebar.
    It calls the `update_treeview` method of the `right_sidebar` object.

    Args:
        self: The current instance of the class.

    Returns:
        None
    """

    return bool(value == "" or (value.isdigit() and 0 <= int(value) <= 1000))

class LeftSidebar(ctk.CTkScrollableFrame):
    PADDING = 5
    ROW_SCENE = 0

    def __init__(self, parent):
        self.widget_dict = {}
        
        super().__init__(parent, width=200)
        self.grid_columnconfigure(0, weight=1)

        self.widget_config_scrollable = self.create_scrollable_frame()
        self.widget_config_label = self.create_label(self.widget_config_scrollable,
            app.translator.translate("CONFIG_LABEL_TEXT")
        )

        self.config_space = self.create_config_space()
        if app.use_scene_manager:
            self.scene_manager_frame = self.create_scene_manager_frame()

    def update_positions(self, x, y):
        self.x_entry.delete(0, "end")
        self.y_entry.delete(0, "end")
        self.x_entry.insert(0,str(x))
        self.y_entry.insert(0,str(y))

    def create_scrollable_frame(self):
        """
        Crea un Scrollable Frame para mostrar widgets.

        Parámetros:
        Ninguno

        Retorna:
        frame (ctk.CTkScrollableFrame o ctk.CTkFrame): Un marco desplazable o un marco regular, dependiendo del valor de app.use_scene_manager.
        """
        frame = ctk.CTkScrollableFrame(self, width=200, height=350, fg_color='#292929') if app.use_scene_manager else ctk.CTkFrame(self, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(frame)

    def create_label(self, parent, text):
        """
        Crea y configura un widget CTkLabel.

        Esta función crea un nuevo widget CTkLabel con el texto proporcionado,
        lo agrega al widget padre especificado y configura su posición en la cuadrícula.

        Parámetros:
        parent (ctk.CTk): El widget padre al que se agregará el Label.
        text (str): El texto que se mostrará en el Label.

        Retorna:
        ctk.CTkLabel: El Label creado y configurado.
        """
        label = ctk.CTkLabel(parent, text=text)
        label.grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING)
        return label

    def create_config_space(self):
        """Create the configuration space frame.

        Returns:
            ctk.CTkFrame: The config space frame.
        """
        config_space = ctk.CTkFrame(self.widget_config_scrollable, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(config_space)

    def create_scene_manager_frame(self):
        """Create the scene manager frame.

        Returns:
            ctk.CTkScrollableFrame: The scene manager frame.
        """

        frame = ctk.CTkScrollableFrame(self, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(frame)

    def add_to_scene_manager_frame(self, arg0):
        self._extracted_from_create_scene_manager_frame_3(arg0)

    def _extracted_from_create_scene_manager_frame_3(self, arg0):
        """Grid a widget and update row count.

        Args:
            arg0: The widget to grid.

        Returns:
            The gridded widget.
        """

        arg0.grid(
            row=self.ROW_SCENE, column=0, sticky="nsew", padx=self.PADDING, pady=self.PADDING
        )
        self.ROW_SCENE += 1
        arg0.grid_columnconfigure(0, weight=1)
        return arg0

    def add_widget_to_grid(self, widget, row, column, **grid_options):
        widget.grid(in_=self.grid_frame, row=row, column=column, **grid_options)

    def show_widget_config(self, widget):
        """Display configuration options for a widget.

        Clears the existing configuration space and populates it with the settings for the given widget.  This includes property entries, position entries, and action buttons.

        Args:
            widget: The widget to configure.
        """
        self.clear_config_space()
        widget.focus_set()
        widget_properties = global_properties
        widget_type = widget.__class__.__name__
        logging.info(f"Mostrando configuración para widget: {widget_type}")
        logging.debug(get_class_parameters(widget.__class__)[1:])
        if widget.__class__.__name__ not in widget_classes:
            self.create_property_entries(widget, get_class_parameters(widget.__class__)[1:])
        else:
            self.create_property_entries(widget, widget_properties[widget_type])
        self.create_position_entries(widget)
        self.create_action_buttons(widget)

    def clear_config_space(self):
        """Clear the configuration space.

        Removes all child widgets from the configuration space frame.
        """

        for child in self.config_space.winfo_children():
            child.destroy()

    def create_property_entries(self, widget, properties):
        """Create property entries for the widget.

        Creates and displays labeled entry widgets for each of the specified properties of the widget.  A label indicating the widget type is also displayed.

        Args:
            widget: The widget.
            properties: The properties to create entries for.
        """
        ctk.CTkLabel(self.config_space, text=f"{app.translator.translate("TYPE_TEXT_WIDGET_LABEL")} {widget.__class__.__name__}").pack(pady=self.PADDING)
        for prop in properties:
            self.create_property_entry(widget, prop)

    def create_property_entry(self, widget, prop):
        """Create a single property entry.

        Creates a labeled entry widget for the given property of the widget, initialized with the current value of the property.

        Args:
            widget: The widget.
            prop: The property name.
        """
        try:
            widget.cget(prop)
            ctk.CTkLabel(self.config_space, text=f"{prop.capitalize()}:").pack()
            entry = ctk.CTkEntry(self.config_space)
            entry.insert(0, str(widget.cget(prop)))
            entry.pack()
            tooltip = CTkToolTip(entry, "")
            tooltip.hide()
            entry.bind("<KeyRelease>", lambda event: self.update_property(widget, prop, entry, tooltip))
        except ValueError:
            logging.error(f"Error al obtener valor de '{prop}' del widget '{widget.__class__.__name__}'")

    def update_property(self, widget, prop, entry, tooltip):
        """Update a widget property based on entry value.

        Attempts to update the specified property of the widget with the value from the entry.  Handles special cases for font and VirtualWindow fg_color.  Displays an error tooltip if the update fails.

        Args:
            widget: The widget.
            prop: The property name.
            entry: The entry widget.
            tooltip: The tooltip for error messages.
        """

        tooltip.hide()
        type_of_property = str if prop == "text_color" else type(widget.cget(prop))
        logging.info(f"Type of property:{type_of_property}")
        try:
            if prop == "font":
                self.update_font_property(widget, entry)
            if widget.__class__.__name__ == "VirtualWindow" and prop == "fg_color":
                widget.configure(**{prop: type_of_property(entry.get())})
                widget.guide_canvas.config(bg=entry.get())
            else:
                widget.configure(**{prop: type_of_property(entry.get())})
            logging.info(f"Propiedad '{prop}' del widget '{widget.__class__.__name__}' actualizada a: {entry.get()}")
            entry.configure(border_color="#565B5E")
        except Exception as e:
            logging.error(f"Error al actualizar '{prop}': {e}. Valor ingresado: {entry.get()}")
            entry.configure(border_color="red")
            tooltip.show()
            tooltip.configure(message=e)

    def update_font_property(self, widget, entry):
        font_value = entry.get()
        font_parts = font_value.rsplit(" ", 1)
        if len(font_parts) != 2 or not font_parts[1].isdigit():
            raise ValueError(f"El valor '{font_value}' no es válido para 'font'. Formato esperado: 'Arial 20'")
        font_name, font_size = font_parts[0], int(font_parts[1])
        widget.configure(font=(font_name, font_size))
        logging.info(f"Propiedad 'font' actualizada a: ({font_name}, {font_size})")

    def create_position_entries(self, widget):
        """Create position entries for the widget.

        Creates entry widgets for the x and y coordinates of the widget, and an entry for a variable name.  Binds key release events to update functions.

        Args:
            widget: The widget.
        """

        position_frame = self._extracted_from_create_position_entries_2(
            "POSITION_LABEL_TEXT"
        )
        self.x_entry = self.create_position_entry(position_frame, widget.winfo_x())
        self.y_entry = self.create_position_entry(position_frame, widget.winfo_y())

        position_var_frame = self._extracted_from_create_position_entries_2(
            "RIGHTBAR_BUTTON_VARIABLE_NAME"
        )
        widget_var = self.create_position_entry(position_var_frame, '', width=110)

        self.x_entry.bind("<KeyRelease>", lambda event: self.update_position(widget, self.x_entry, self.y_entry))
        self.y_entry.bind("<KeyRelease>", lambda event: self.update_position(widget, self.x_entry, self.y_entry))
        widget_var.bind("<KeyRelease>", lambda event: self.variable_widget_change(widget._name, widget_var))

    # TODO Rename this here and in `create_position_entries`
    def _extracted_from_create_position_entries_2(self, arg0):
        """Create a labeled frame for position entries.

        Creates a CTkFrame and adds a CTkLabel above it with translated text.

        Args:
            arg0: Label text key.

        Returns:
            ctk.CTkFrame: The frame.
        """

        ctk.CTkLabel(self.config_space, text=app.translator.translate(arg0)).pack(
            pady=self.PADDING
        )
        result = ctk.CTkFrame(self.config_space)
        result.pack(pady=self.PADDING)

        return result

    def variable_widget_change(self, widget, widget_var):
        """Handle changes in the widget variable name.

        Attempts to update the widget's variable name; if the entered name is invalid, it logs a warning and corrects the name to contain only alphabetic characters.

        Args:
            widget: The widget name.
            widget_var: The variable name entry.
        """

        var_name = widget_var.get()
        if self.update_variable_name(widget, widget_var):
            logging.info("Variable de widget actualizada.")
        else:
            corrected_var_name = ''.join(filter(str.isalpha, var_name))
            widget_var.delete(0, 'end')
            widget_var.insert(0, corrected_var_name)
            logging.warning(f"El nombre de la variable '{var_name}' no es válido. Se ha corregido a '{corrected_var_name}'.")

    def update_variable_name(self, widget, widget_var):
        """Update the variable name associated with the widget.

        Stores the variable name in the widget dictionary if it's valid (alphabetic or empty).

        Args:
            widget: The widget name.
            widget_var: The variable name entry.

        Returns:
            bool: True if the variable name is valid, False otherwise.
        """

        var_name = widget_var.get()
        if var_name.isalpha() or var_name == '':
            self.widget_dict[widget] = var_name
            return True
        else:
            return False

    def create_position_entry(self, parent, initial_value, width=50):
        """Create an entry for position values.

        Creates a CTkEntry widget with a specified width and initial value, and packs it to the left.

        Args:
            parent: The parent widget.
            initial_value: The initial value.
            width: The entry width.

        Returns:
            ctk.CTkEntry: The created entry widget.
        """

        entry = ctk.CTkEntry(parent, width=width)
        entry.insert(0, initial_value)
        entry.pack(side="left", padx=2)
        return entry

    def update_position(self, widget, x_entry, y_entry):
        """Update the position of a widget.

        Tries to update the widget's position using values from x and y entry widgets. Logs a warning if the entry values are not valid integers.

        Args:
            widget: The widget to move.
            x_entry: The entry widget containing the x-coordinate.
            y_entry: The entry widget containing the y-coordinate.
        """

        try:
            new_x = int(x_entry.get())
            new_y = int(y_entry.get())
            widget.place(x=new_x, y=new_y)
            logging.info(f"Posición actualizada a: ({new_x}, {new_y})")
        except ValueError:
            logging.warning("Posición inválida. Por favor, ingresa valores numéricos.")

    def create_action_buttons(self, widget): 
        """Create action buttons for the widget.

        Creates buttons for raising, lowering, and deleting the given widget, adding them to the configuration space.  Button labels are translated using the app translator.

        Args:
            widget: The widget for which to create action buttons.
        """

        actions = [ 
            (app.translator.translate("RIGHTBAR_BUTTON_UPLOAD_LAYER"), lambda: widget.lift()), 
            (app.translator.translate("RIGHTBAR_BUTTON_LOWER_LAYER"), lambda: widget.lower()), 
            (app.translator.translate("RIGHTBAR_BUTTON_DELETE_WIDGET"), lambda: self.delete_widget(widget)),
        ]
        for text, command in actions:
            ctk.CTkButton(self.config_space, text=text, command=command, **BUTTON_STYLE).pack(pady=15)

    def delete_widget(self, widget):
        """Delete a widget.

        Deletes the given widget from the virtual window, clears the config space, and updates the treeview, unless the widget is the virtual window itself.  Logs an error if attempting to delete the virtual window.

        Args:
            widget: The widget to delete.
        """

        if widget.__class__.__name__ != 'VirtualWindow':
            app.virtual_window.delete_widget(widget)
            self.clear_config_space()
            app.cross_update_treeview()
        else:
            logging.error("No se puede borrar la virtual window")

class RightSidebar(ctk.CTkScrollableFrame):
    TREEVIEW_WIDTH = 180
    PADDING = 5

    def __init__(self, parent, virtual_window):
        super().__init__(parent, width=200)
        self.configure_treeview_style()
        self.grid_columnconfigure(0, weight=1)
        self.virtual_window = virtual_window
        self.widget_tree = {}
        self.buttons = {}

        self.create_widgets_section()
        self.create_treeview_section()

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#131313", foreground="#fafafa", font=("Arial", 12, "bold"), relief="flat")
        style.configure("Treeview", background="#131313", foreground="#fafafa", fieldbackground="#131313", borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("selected", "#252525"), ("active", "#252525")])

    def create_widgets_section(self):
        ctk.CTkLabel(self, text=app.translator.translate("LABEL_WIDGETS_TEXT")).grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
        for i, widget in enumerate(widgets):
            self.create_widget_button(widget, i + 1)
        self.create_widget_button("Importar", i + 1)

    def import_custom_widget(self):
        widget=load_classes_from_file(filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")]
        ))
        logging.info(f"Detalles de widget a importar: {widget}")
        app.virtual_window._extracted_from_create_and_place_widget_5(widget[0](self.virtual_window), 100, 100)

    def check_widget(self, widget):
        if widget == "Importar": return self.import_custom_widget
        else: return lambda w=widget: self.add_widget(w)

    def create_widget_button(self, widget, row):
        """Crea un botón para cada widget y lo agrega a la sección de widgets."""
        btn = ctk.CTkButton(
            self,
            text=widget,
            command=self.check_widget(widget),
            **BUTTON_STYLE
        )
        btn.grid(row=row, column=0, padx=self.PADDING, pady=2, sticky="ew")
        self.buttons[widget] = btn

    def disable_buttons(self):
        """Desactiva todos los botones creados."""
        for btn in self.buttons.values():
            btn.configure(state="disabled")
            
    def enable_buttons(self):
        """Activa todos los botones creados."""
        for btn in self.buttons.values():
            btn.configure(state="normal")

    def create_treeview_section(self):
        ctk.CTkLabel(self, text=app.translator.translate("LABEL_SCHEME_TEXT")).grid(row=len(widgets) + 1, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=len(widgets) + 2, column=0, padx=self.PADDING, pady=self.PADDING, sticky="nsew")
        self.tree.column("#0", width=self.TREEVIEW_WIDTH, stretch=True)
        self.tree.heading("#0", text="Widgets")

    def add_widget(self, widget):
        """Añade un widget a la ventana virtual y actualiza el esquema del TreeView."""
        self.virtual_window.add_widget(widget)
        self.update_treeview()

    def detect_hierarchy(self, parent_widget=None):
        """Detecta automáticamente la jerarquía de widgets dentro de la ventana virtual."""
        hierarchy = []
        container = parent_widget or self.virtual_window

        for child in container.winfo_children():
            hierarchy.append((child, parent_widget))
            hierarchy.extend(self.detect_hierarchy(child))

        return hierarchy

    def update_treeview(self):
        """Actualiza el esquema del TreeView basándose en la jerarquía detectada automáticamente."""
        widget_hierarchy = self.detect_hierarchy()
        self.tree.delete(*self.tree.get_children())
        self.widget_tree.clear()

        for widget, parent_widget in widget_hierarchy:
            self.insert_widget_into_tree(widget, parent_widget)

    def insert_widget_into_tree(self, widget, parent_widget):
        widget_name = widget._name if hasattr(widget, "_name") else widget.__class__.__name__
        widget_id = id(widget)

        if parent_widget:
            parent_id = id(parent_widget)
            parent_tree_id = self.widget_tree.get(parent_id)
            tree_id = self.tree.insert(parent_tree_id, "end", text=widget_name)
        else:
            tree_id = self.tree.insert("", "end", text=widget_name)

        self.widget_tree[widget_id] = tree_id

class Toolbar(ctk.CTkFrame):
    PROGRESS_BAR_HIDE_DELAY = 3000

    def __init__(self, parent, virtual_window, rightbar, initialize_on_import=False):
        super().__init__(parent, height=40, fg_color="#333333")
        self.virtual_window = virtual_window
        self.right_bar = rightbar
        
        self.config_window = None
        
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.create_buttons()
        self.create_info_label()
        self.create_progress_bar()

        self.initialize_on_import = initialize_on_import
        self.setup_logging()

    def apply_configs(self, language):
        app.switch_language(language)

    def create_config_widgets(self, config_window):
        """Crea los widgets de configuración en la ventana de configuración."""
        language = ctk.CTkComboBox(config_window, values=['es', 'en'], command=None, state='readonly', fg_color=['#F9F9FA', '#343638'], button_color=['#979DA2', '#565B5E'], button_hover_color=['#6E7174', '#7A848D'], dropdown_fg_color=['gray90', 'gray20'], dropdown_hover_color=['gray75', 'gray28'], width=140, height=28)
        language.place(x=99, y=44)
        language.set(app.translator.current_language)
        ctk.CTkLabel(config_window, text='Idioma:', textvariable='', fg_color='transparent', corner_radius=0, text_color=['gray14', 'gray84'], width=0, height=28, font=('Arial', 19), anchor='center', compound='center', justify='center').place(x=20, y=44)
        ctk.CTkButton(config_window, text='Aplicar cambios', command=lambda:self.apply_configs(language.get()), fg_color=['#3a7ebf', '#1f538d'], width=140, height=28, border_width=0, border_color=['#3E454A', '#949A9F'], hover_color=['#325882', '#14375e'], text_color=['#DCE4EE', '#DCE4EE'], border_spacing=2, corner_radius=6).place(x=251, y=262)
        # entry = ctk.CTkEntry(config_window)
        # entry.pack(pady=10)

    def open_config_window(self):
        """Abre la ventana de configuraciones si no está ya abierta."""
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = ctk.CTkToplevel(self)
            self.config_window.title("Configuraciones")
            self.config_window.geometry("400x300")
            
            self.create_config_widgets(self.config_window)
            
            label = ctk.CTkLabel(self.config_window, text="Configuraciones")
            label.pack(pady=10)
        else:
            self.config_window.lift()
    
    def create_buttons(self):
        """Crea y empaqueta los botones de la barra de herramientas."""
        self.create_button(app.translator.translate("TOOLBAR_BUTTON_EXPORT"), self.export_to_file, side="right")
        self.create_button("Code preview", self.change_view, side="right")
        self.create_button(app.translator.translate("TOOLBAR_BUTTON_CONFIG"),self.open_config_window, side="right")
        #self.create_button("Importar desde .py", self.import_from_file, side="right")
    
    def change_view(self):
        """Cambia el modo de visualización del código."""
        
        app.view_code()
    
    def create_button(self, text, command, side):
        """Método auxiliar para crear un botón."""
        button = ctk.CTkButton(self, text=text, command=command, **BUTTON_STYLE)
        button.pack(pady=5, padx=5, side=side)

    def create_info_label(self):
        """Crea y empaqueta la etiqueta de información."""
        self.info_label = ctk.CTkLabel(self, text="Ok")
        self.info_label.pack(pady=5, padx=5, side="left")

    def create_progress_bar(self):
        """Crea y empaqueta la barra de progreso."""
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=5, padx=5, side="left")
        self.progress.set(0)
        self.progress.pack_forget()

    def setup_logging(self):
        """Configure el registro para mostrar mensajes en la etiqueta de información."""
        log_handler = TkinterLogHandler(self.info_label)
        log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(log_handler)

    def progress_set_value(self, value):
        """Establezca el valor de la barra de progreso y administre su visibilidad."""
        self.progress.set(value)
        if value < 1.0:
            self.progress.pack(pady=5, padx=5, side="left")
        else:
            self.after(self.PROGRESS_BAR_HIDE_DELAY, self.hide_progress_bar)

    def hide_progress_bar(self):
        """Oculta la barra de progreso si está completa."""
        if self.progress.get() == 1.0:
            self.progress.pack_forget()

    def export_to_file(self):
        """Exporte el contenido de la ventana virtual a un archivo Python."""
        if file_path := filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Guardar como",
        ):
            self.virtual_window.export_to_file(file_path)

    def import_from_file(self):
        """Importe contenido desde un archivo Python a la ventana virtual."""
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
    DEFAULT_HEIGHT = 500
    DEFAULT_WIDTH = 800

    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.translator.load_translations(translations)
        self.title("CustomDesigner")
        self.geometry("1000x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.import_proyect = False
        self.use_scene_manager = False

        self.TITLE_FONT = ctk.CTkFont(family="Helvetica", size=36, weight="bold")
        self.SUBTITLE_FONT = ctk.CTkFont(family="Helvetica", size=18)
        self.LABEL_FONT = ctk.CTkFont(family="Helvetica", size=14)

        self.ENTRY_STYLE = {
            'fg_color': 'transparent',
            'border_width': 2,
            'border_color': '#1F6AA5',
            'text_color': ('gray10', 'gray90'),
            'width': 140,
            'height': 35,
            'corner_radius': 8,
            'font': self.LABEL_FONT
        }
        self.CHECKBOX_STYLE = {
            'fg_color': '#1F6AA5',
            'text_color': ('gray10', 'gray90'),
            'hover_color': '#2980B9',
            'border_width': 2,
            'border_color': '#1F6AA5',
            'checkmark_color': ('gray90', 'gray10'),
            'corner_radius': 5,
            'font': self.LABEL_FONT
        }
        
        self.setup_grid()
        self.create_virtual_window()
        self.create_ui_elements()

    def setup_grid(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_virtual_window(self):
        self.virtual_window = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.virtual_window.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.virtual_window.grid_columnconfigure((0, 1), weight=1)
        self.virtual_window.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

    def create_ui_elements(self):
        self.create_title_label()
        self.create_window_configuration_labels()
        self.create_entry_fields()
        self.create_checkboxes()
        self.create_action_buttons()

    def create_title_label(self):
        ctk.CTkLabel(self.virtual_window, text=self.translator.translate("NEW_PROYECT"), font=self.TITLE_FONT, text_color=('gray10', 'gray90')).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(30, 10))

    def create_window_configuration_labels(self):
        ctk.CTkLabel(self.virtual_window, text=self.translator.translate("WINDOW_CONFIG"), font=self.SUBTITLE_FONT, text_color=('gray20', 'gray80')).grid(row=1, column=0, columnspan=2, sticky="w", padx=30, pady=(10, 20))

    def create_entry_fields(self):
        validate_command = self.register(validate_input)

        self.hvar = ctk.StringVar(value=str(self.DEFAULT_HEIGHT))
        self.create_label_and_entry(self.translator.translate("HEIGHT"), self.hvar, 2, validate_command)

        self.wvar = ctk.StringVar(value=str(self.DEFAULT_WIDTH))
        self.create_label_and_entry(self.translator.translate("WIDTH"), self.wvar, 3, validate_command)

    def create_label_and_entry(self, label_text, text_var, row, validate_command):
        ctk.CTkLabel(self.virtual_window, text=label_text, font=self.LABEL_FONT, text_color=('gray10', 'gray90')).grid(row=row, column=0, sticky="e", padx=(20, 10), pady=10)
        entry = ctk.CTkEntry(self.virtual_window, textvariable=text_var, validate="key", validatecommand=(validate_command, "%P"), placeholder_text=text_var.get(), **self.ENTRY_STYLE)
        entry.grid(row=row, column=1, sticky="w", padx=(10, 30), pady=10)

    def create_checkboxes(self):
        self.is_resizable = ctk.CTkCheckBox(self.virtual_window, text=self.translator.translate("RESIZABLE"), **self.CHECKBOX_STYLE)
        self.is_resizable.grid(row=4, column=0, columnspan=2, sticky="w", padx=30, pady=10)

    def create_action_buttons(self):
        ctk.CTkButton(self.virtual_window, text=self.translator.translate("CREATE_PROJECT"), command=self.create_project, font=self.LABEL_FONT, **BUTTON_STYLE).grid(row=8, column=0, columnspan=2, sticky="se", padx=30, pady=30)
        ctk.CTkButton(self.virtual_window, text=self.translator.translate("IMPORT_PROJECT"), command=lambda: self.create_project(True), font=self.LABEL_FONT, **BUTTON_STYLE).grid(row=8, column=4, columnspan=2, sticky="se", padx=30, pady=30)

    def create_project(self, import_proyect=False):
        self.import_proyect = import_proyect
        height = self.hvar.get()
        width = self.wvar.get()
        options = {
            "is_resizable": self.is_resizable.get(),
        }
        logging.info(f"Creando proyecto - Altura: {height}, Anchura: {width}, Opciones: {options}")
        self.clear_virtual_window(height, width, options)

    def clear_virtual_window(self, h, w, bools):
        """Elimina todos los widgets dentro de self.virtual_window en el contexto del Menu."""
        if h.isdigit() and w.isdigit():
            for widget in self.virtual_window.winfo_children():
                widget.destroy()
            self.virtual_window.destroy()
            self.create_ui(int(h), int(w), bools)
        else:
            logging.warning("Altura o anchura no válidas.")

    def create_ui(self, vw_height, vw_width, bools):
        self.resizable(True, True)
        self.left_sidebar = LeftSidebar(self)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew")

        self.central_canvas = ctk.CTkCanvas(self, bg="black")
        self.central_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.virtual_window = VirtualWindow(self.central_canvas, self.left_sidebar, self, bools, width=vw_width, height=vw_height)
        self.virtual_window_id = self.central_canvas.create_window((50, 50), anchor="nw", window=self.virtual_window)

        self.central_canvas.configure(scrollregion=self.central_canvas.bbox("all"))

        self.right_sidebar = RightSidebar(self, self.virtual_window)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")

        self.toolbar = Toolbar(self, self.virtual_window, self.right_sidebar, self.import_proyect)
        self.toolbar.grid(row=1, column=0, columnspan=3, sticky="nsew")

        if self.toolbar.initialize_on_import:
            self.toolbar.import_from_file()

        #self.central_canvas.bind("<MouseWheel>", self.zoom_canvas)
        self.central_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.central_canvas.bind("<B1-Motion>", self.pan_canvas)

        self.scale_factor = 1.1
        self.current_scale = 1.0
        self.last_x = 0
        self.last_y = 0

    def zoom_canvas(self, event):
        x = self.central_canvas.canvasx(event.x)
        y = self.central_canvas.canvasy(event.y)

        scale = self.scale_factor if event.delta > 0 else 1 / self.scale_factor
        self.central_canvas.scale("all", x, y, scale, scale)

        self.central_canvas.configure(scrollregion=self.central_canvas.bbox("all"))

        self.current_scale *= scale

    def start_pan(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def pan_canvas(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y

        self.central_canvas.move("all", dx, dy)

        self.last_x = event.x
        self.last_y = event.y

    def view_code(self):
        if self.virtual_window.toggle_visibility():
            self.virtual_window.replace()
            self.code = CTkCodeBox(self.central_canvas, height=500, width=800, language='python')
            self.code.place(x=50, y=50)
            self.code.insert('1.0', "\n".join(self.virtual_window.previsualize_code()))
            self.right_sidebar.disable_buttons()
            self.code.bind("<KeyRelease>", self.update_virtual_window)
        else:
            self.right_sidebar.enable_buttons()
            self.code.destroy()

    def update_virtual_window(self, event):
        """
        Actualiza el contenido de VirtualWindow con el código actual de CTkCodeBox.

        :param event: El evento de tecla liberada.
        """
        new_code = self.code.get('1.0', 'end-1c')
        self.virtual_window.import_from_codebox(new_code)
        logging.debug(self.virtual_window.widgets)

    def cross_update_treeview(self):
        self.right_sidebar.update_treeview()

    def cross_update_progressbar(self, val: float):
        self.toolbar.progress_set_value(val)

    def cross_update_text_info(self, val: str):
        self.toolbar.info_label.configure(text=val)
        self.after(3000, lambda: self.toolbar.info_label.configure(text='Ok.'))
    
    def switch_language(self, language):
        try:
            self.translator.set_language(language)
            self.refresh_ui()
        except ValueError as e:
            logging.error(str(e))
    
    def refresh_ui(self):
        for w in [self.toolbar, self.left_sidebar, self.right_sidebar]:
            for widget in w.winfo_children():
                if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                    try:
                        widget.configure(text=self.translator.translate(self.translator.find_key_by_value(widget.cget('text'))))
                        logging.debug(f"Actualizando widget: {widget.__class__.__name__} - Texto: {widget.cget('text')}")
                    except Exception:
                        continue

if __name__ == "__main__":
    app = App()
    app.mainloop()