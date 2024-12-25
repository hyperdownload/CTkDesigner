class Translator:
    def __init__(self, default_language="en"):
        self.languages = {"es": {}, "en": {}}
        self.current_language = default_language

    def load_translations(self, translations):
        """
        Carga un diccionario de traducciones.
        Ejemplo: {"es": {"hello": "Hola"}, "en": {"hello": "Hello"}}
        """
        for lang, texts in translations.items():
            self.languages[lang] = texts

    def set_language(self, language):
        if language in self.languages:
            self.current_language = language
        else:
            raise ValueError(f"Idioma no soportado: {language}")

    def translate(self, key):
        return self.languages[self.current_language].get(key, key)
