import json
from pathlib import Path


class Translator:
    def __init__(self, default_language="pt"):
        self.base_path = Path(__file__).resolve().parent / "locales"
        self.supported_languages = ("pt", "en")
        self._translations = {}
        self.language = default_language
        self.set_language(default_language)

    def _load(self, language):
        if language in self._translations:
            return self._translations[language]
        file_path = self.base_path / f"{language}.json"
        with file_path.open("r", encoding="utf-8") as f:
            self._translations[language] = json.load(f)
        return self._translations[language]

    def set_language(self, language):
        if language not in self.supported_languages:
            language = "en"
        self.language = language
        self._load(language)

    def get(self, key):
        current = self._translations[self.language]
        if key in current:
            return current[key]
        fallback = self._load("en")
        return fallback.get(key, key)

