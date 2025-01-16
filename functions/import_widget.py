import importlib.util
import inspect
import os

def load_classes_from_file(file_path):
    """
    Carga todas las clases definidas en un archivo Python.

    Args:
        file_path (str): Ruta del archivo Python.

    Returns:
        list: Una lista de clases definidas en el archivo.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise ImportError(f"Error al importar el archivo: {e}")

    return [
        obj
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module_name
    ]

def get_class_parameters(cls):
    """
    Obtiene los parámetros del constructor de una clase.

    Args:
        cls (type): La clase.

    Returns:
        list: Una lista de nombres de parámetros (excluyendo 'self').
    """
    init_signature = inspect.signature(cls.__init__)
    return [
        param.name for param in init_signature.parameters.values()
        if param.name != "self"
    ]

if __name__ == "__main__":
    file_path = "b.py"

    try:
        if classes := load_classes_from_file(file_path):
            print("Clases encontradas:")
            for i, cls in enumerate(classes, start=1):
                print(f"{i}. {cls.__name__}")

            selected_class = classes[0]
            print(f"\nSeleccionando clase predeterminada: {selected_class.__name__}")

            parameters = get_class_parameters(selected_class)
            print(f"Clase seleccionada: {selected_class.__name__}")
            print(f"Parámetros del constructor: {parameters}")

            instance = selected_class(*[None] * len(parameters))
            print(f"Instancia creada: {instance}")
        else:
            print("No se encontraron clases en el archivo.")
    except Exception as e:
        print(f"Error: {e}")
