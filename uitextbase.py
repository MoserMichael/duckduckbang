

class UITextBase:
    def __init__(self):
        self.map_string_to_translations = {}

    def add_item(self, str_val ):
        self.map_string_to_translations[ str_val ] = {}

    def get_item(self, str_val, lan):
        entry = self.map_string_to_translations.get(str_val)
        if entry is None:
            return None
        return entry.get(lan)

    def set_item(self, str_val, lan, text):
        entry = self.map_string_to_translations.get(str_val)
        if entry is None:
            self.map_string_to_translations[str_val] = { lan : text }
            return
        entry[lan] = text
