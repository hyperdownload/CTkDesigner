import customtkinter as ctk
global_properties = {
    "VirtualWindow": ["fg_color", "bg_color", "border_width", "border_color"],
    "CTkButton": ["text", "command", "fg_color", "width", "height", "border_width", "border_color", "hover_color", "text_color",
        "border_spacing", "corner_radius"],
    "CTkLabel": ["text", "textvariable", "fg_color", "corner_radius", "text_color", "width", "height", "font", "anchor", "compound",
                 "justify"],
    "CTkEntry": ["placeholder_text"],
    "CTkFrame": ["fg_color", "bg_color", "height", "width", "border_width", "border_color"]}

button_style = {
        "fg_color": "#2E2E2E",  # Color de fondo del botón
        "hover_color": "#3A3A3A",  # Color al pasar el ratón por encima
        "text_color": "#FFFFFF",  # Color del texto
        "corner_radius": 8,       # Radio de las esquinas
        "border_color": "#5A5A5A",  # Color del borde
        "border_width": 2,        # Ancho del borde
}

widgets = [
            "CTkButton", "CTkLabel", "CTkEntry", "CTkCheckBox",
            "CTkRadioButton", "CTkComboBox", "CTkSlider", "CTkProgressBar",
            "CTkTextbox", "CTkSwitch", "CTkFrame"
        ]

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
            "CTkFrame": ctk.CTkFrame,
        }