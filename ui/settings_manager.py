from PyQt6.QtCore import QSettings


class SettingsManager:
    ORG  = "MyCompany"
    APP  = "SpeechTranscriber"

    # ключи
    DEVICE_KEY   = "audio/device"
    FOLDER_KEY   = "audio/folder"
    LANGUAGE_KEY = "ui/default_language"
    RECORDS_KEY  = "records/list"

    def __init__(self):
        self._s = QSettings(SettingsManager.ORG, SettingsManager.APP)

    # --- геттеры ---
    def device(self, default="") -> str:
        return self._s.value(SettingsManager.DEVICE_KEY, default, str)

    def folder(self, default="") -> str:
        return self._s.value(SettingsManager.FOLDER_KEY, default, str)

    def language(self, default="") -> str:
        return self._s.value(SettingsManager.LANGUAGE_KEY, default, str)

    def records(self) -> list[str]:
        """Return list of previously recorded file paths."""
        data = self._s.value(SettingsManager.RECORDS_KEY, "[]", str)
        try:
            import json
            return json.loads(data)
        except Exception:
            return []

    # --- сеттеры ---
    def set_device(self, text: str):
        self._s.setValue(SettingsManager.DEVICE_KEY, text)

    def set_folder(self, path: str):
        self._s.setValue(SettingsManager.FOLDER_KEY, path)

    def set_language(self, code: str):
        self._s.setValue(SettingsManager.LANGUAGE_KEY, code)

    def set_records(self, paths: list[str]):
        """Persist list of recorded files."""
        import json
        self._s.setValue(SettingsManager.RECORDS_KEY, json.dumps(paths))
