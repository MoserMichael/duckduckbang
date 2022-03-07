#!/usr/bin/env python3
import argparse
import sys
import translators as ts
import globs
import dcachebase
import uitextbase



class LanguageTranslation:

    translators_prec = [
            ts.deepl, # doesn't work - seems 0they changed the api, and the package didn't
            #ts.yandex,
            ts.google,
#            ts.bing,
#            ts.sogou,
#            ts.baidu,
            ]

    def __init__(self):
        pass

    def process(self, from_lang_name, to_lang_name, text):

        for provider in LanguageTranslation.translators_prec:
            try:
                result = ts.translate_html(text, translator=provider, from_language=from_lang_name, to_language=to_lang_name)

                print(f"From_lang: {from_lang_name}\nTo_lang: {to_lang_name}\nprovider: {repr(provider)}\nText: {text}\nResult: {result}")

                return result
            except Exception as ex:
                print(f"failed from: {from_lang_name} to: {to_lang_name} for: {provider} with exception: {ex}")

        return None

class TranslateHelpText:
    def __init__(self, list_of_target_langs):
        self.list_of_target_langs = list_of_target_langs
        self.num_set = 0
        self.num_failed = 0

    def run(self):
        for target_lang in self.list_of_target_langs:
            print(f"Translating to {target_lang}")
            self.run_translation(target_lang)

    @staticmethod
    def get_src_lang(entry_obj):
        if entry_obj.html_document_language is not None and entry_obj.html_document_language != "":
            lan = entry_obj.html_document_language
            pos = lan.find("-")
            if pos == -1:
                return lan
            return lan[0 : pos]
        if entry_obj.language_description.startswith("__label__"):
            return entry_obj.language_description[ len("__label__") : ]
        return None

    def run_translation(self, to_lang):
        cache = dcachebase.DescriptionCacheBase()
        transl = LanguageTranslation()

        cache.read_description_cache()

        for base_url in cache.map_url_to_descr.keys():
            entry_obj = cache.cache_get(base_url)
            if entry_obj is not None and entry_obj.description != '':

                src_lang = TranslateHelpText.get_src_lang(entry_obj)

                if entry_obj.translations.get( to_lang ) is not None:
                    continue

                if src_lang != to_lang:
                    out_text = transl.process(src_lang, to_lang, entry_obj.description)
                    if out_text is None:
                        out_text = transl.process("auto", to_lang, entry_obj.description)

                else:
                    out_text = entry_obj.description

                if out_text is not None:
                    entry_obj.translations[ to_lang ] = out_text
                    cache.cache_set(base_url, entry_obj)
                    self.num_set += 1
                else:
                    self.num_failed += 1

            cache.write_description_cache()

        print(f"*** description cache changed, number of items set: {self.num_set} failed: {self.num_failed}")

def translate_ui_text():
    print(f"Translating ui texts from file {globs.Globals.ui_text_strings}")

    transl = LanguageTranslation()
    text_base = uitextbase.UITextBase()

    text_base.read_json()

    num = 0

    with open(globs.Globals.ui_text_strings, 'r') as ui_file:
        lines = ui_file.readlines()

        for lang in globs.Globals.supported_languages:
            for line in lines:
                line = line.strip()

                descr = text_base.get_item(line, lang)
                if descr is not None:
                    print(f"skipping {line} {lang}")
                    continue

                if lang != "en":
                    descr = transl.process("en", lang, line)
                else:
                    descr = line

                if descr is not None and descr != "":
                    text_base.set_item( line, lang, descr )
                num += 1

                # from time to time: update the json, might crash and loose all your work...
                if num % 100 == 0:
                    text_base.write_json()

    text_base.write_json()

def translate_help_text():
    print("translating descriptions of search engines...")
    transl = TranslateHelpText(globs.Globals.supported_languages)
    transl.run()

def run_all():
    usage = """
Build the translation of the text.
"""

    parse = argparse.ArgumentParser(
        description=usage, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    group = parse.add_argument_group("translate the text")

    group.add_argument(
        "--uitext",
        "-u",
        default=False,
        action="store_true",
        dest="translate_ui_text",
        help="tranlate user interface text, input file: " + globs.Globals.ui_text_strings,
    )

    group.add_argument(
        "--descr",
        "-d",
        default=False,
        action="store_true",
        dest="translate_descr",
        help="translate description of search engines. Input file: " + globs.Globals.description_cache_file,
    )
    cmd = parse.parse_args()

    if cmd.translate_ui_text:
        translate_ui_text()
    elif cmd.translate_descr:
        translate_help_text()
    else:
        print("no option has been set, see help")
        sys.exit(1)


if __name__ == '__main__':
    run_all()
