#!/usr/bin/env python3
import typing
import translators as ts
import dcachebase



class LanguageTranslation:

    translators_prec = [
            ts.deepl,
            ts.yandex,
            ts.google,
            ts.bing,
            ts.sogou,
            ts.baidu,
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

class TranslateText:
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
        cache.set_file_name( dcachebase.DescriptionCacheBase.description_cache_file_with_translation )
        for base_url in cache.map_url_to_descr.keys():
            entry_obj = cache.cache_get(base_url)
            if entry_obj is not None and entry_obj.description != '':

                src_lang = TranslateText.get_src_lang(entry_obj)

                if entry_obj.translations.get( to_lang ) is not None:
                    continue

                if src_lang != to_lang:
                    out_text = transl.process(src_lang, to_lang, entry_obj.description)
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

def run_all():
    transl = TranslateText([ 'en', 'de', 'fr', 'ru', 'ch', 'jp', 'es' ])
    transl.run()

run_all()
