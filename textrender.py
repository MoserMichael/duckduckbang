import re
import globs
import uitextbase

class TextRenderer:
    MODE_SHOW_ALL_LANGUAGES=1
    MODE_SHOW_TRANSLATION=2

    def __init__(self):
        self.text_set = {}
        self.check_for_regex = None
        self.out_file = None
        self.mode = TextRenderer.MODE_SHOW_ALL_LANGUAGES
        self.text_base = None
        self.translation_lang = None

    def set_translation_mode(self):
        self.mode = TextRenderer.MODE_SHOW_TRANSLATION
        self.text_base = uitextbase.UITextBase()
        self.text_base.read_json()

    def is_show_all_languages(self):
        return self.mode == TextRenderer.MODE_SHOW_ALL_LANGUAGES

    def show_text_str(self, text):
        if self.mode == TextRenderer.MODE_SHOW_ALL_LANGUAGES:
            # check if this is not a regular expression.
            if self.check_for_regex is None:
                self.check_for_regex = re.compile(r'^(http[s]?)://.*$')
            if self.check_for_regex.match(text) is None:
                print(text)
                self.text_set[text] = 1
            return text

        if self.mode == TextRenderer.MODE_SHOW_TRANSLATION:
            assert self.translation_lang is not None
            translation_text = self.text_base.get_item( text.strip(), self.translation_lang)
            if translation_text is not None:
                return translation_text
#            else:
#                print(f"can't find translation for: {self.translation_lang} |{text}|")
#                assert 0

            return text

        raise ValueError(f"Invalid mode value {self.mode}")

    def show_text(self, text):
        assert self.out_file is not None
        self.out_file.write( self.show_text_str(text) )

    def write_text(self):
        if self.mode == TextRenderer.MODE_SHOW_ALL_LANGUAGES:
            print("writing ui string...")
            with open(globs.Globals.ui_text_strings, "w") as out_file:
                for item, _ in self.text_set.items():
                    out_file.write(f"{item}\n")
