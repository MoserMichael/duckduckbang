#!/usr/bin/env python3

from pprint import pprint
import typing
import dataclasses
from argostranslate import package

@dataclasses.dataclass
class GraphEntry:
    # target language
    target_lang: typing.List[str]

    # there exists a translation from src to target language.
    exists: bool

    # has been loaded
    present: bool

    # intermediate transformations required to achieve translation to the target language (from source languagei)
    path: typing.List[str]


class LanguageTranslation:
    def __init__(self):
        self.pkg_graph = {}

    def build(self):
        LanguageTranslation._update_index()

        pkgs = LanguageTranslation._get_available_packages()
        for pkg in pkgs:
            #print(f"pkg: {pkg} pkg.__dict__: {pkg.__dict__}")
            print(f"from: {pkg.from_code} / {pkg.from_name} -> {pkg.to_code} / {pkg.to_name}")

            entry = self.pkg_graph.get(pkg.from_code)
            if entry is None:
                entry = GraphEntry([], True, False, [])

            entry.target_lang.append( pkg.to_code )

            self.pkg_graph[ pkg.from_code ] = entry

    def translate(self, from_lang, to_lang, text):
        entry = self.pkg_graph.get(from_lang)
        if entry is None:
            entry = self._discover_path(from_lang, to_lang)
        if entry is None or not entry.exists:
            print(f"no translation from {from_lang} to {to_lang}")
            return
        if not entry.present:
            self._load_translation(entry)
        if not entry.present:
            print(f"can't load translation from {from_lang} to {to_lang}")

    def _discover_path(self, from_lang, to_lang):
        path = self._discover_imp(from_lang, to_lang)
        if path is None:
            return None
        return GraphEntry( [to_lang], True, False, path)
    
    def _discover_imp(from_lang, to_lang):
        if from_lang == to_lang:
            return []

        entry = self.pkg_graph.get(from_lang)
        if entry is None:
            return None:
        for lang in target_lang;
            ret = _discover_imp(lang, to_lang)
            if ret is not None:
                ret.prepend.insert(0, lang)
                return

    def _load_translation(self, entry):
        pass

    def show(self):
        pprint(self.pkg_graph)

    @staticmethod
    def _update_index():
        """Update the package index."""
        package.update_package_index()

    @staticmethod
    def _get_available_packages():
        """Get available packages and update packages list if it is not done"""
        try:
            available_packages = package.get_available_packages()
        except:
            LanguageTranslation._update_index()
            available_packages = package.get_available_packages()

        return available_packages


# src -> [ [trg1]...[trgn].. [trg1, trg2] .... ]


transl = LanguageTranslation()
transl.build()
transl.show()



