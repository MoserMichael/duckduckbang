import os
import json
import globs

class UITextBase:
    def __init__(self):
        self.map_string_to_translations = {}
        self.translation_changed = False

    def add_item(self, str_val ):
        self.map_string_to_translations[ str_val ] = {}
        self.translation_changed = True


    def get_item(self, str_val, lan):
        entry = self.map_string_to_translations.get(str_val)
        if entry is None:
            return None
        return entry.get(lan)

    def set_item(self, str_val, lan, text):
        entry = self.map_string_to_translations.get(str_val)
        if entry is None:
            self.map_string_to_translations[str_val] = { lan : text }
        else:
            entry[lan] = text
        self.translation_changed = True

    def read_json(self):
        if os.path.isfile(globs.Globals.ui_text_translated):
            with open(globs.Globals.ui_text_translated, 'r') as json_file:
                self.map_string_to_translations = json.load(json_file)

    def write_json(self):
        if self.translation_changed:
            with open(globs.Globals.ui_text_translated, 'w') as json_file:
                json.dump( self.map_string_to_translations, json_file, indent=2 )
            self.translation_changed = False
            return True
        return False
