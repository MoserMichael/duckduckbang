import dcachebase
import fasttext

class LanguageIdentification:

    def __init__(self):
        pretrained_lang_model = "/lid.176.bin"
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        # model doesn't like newlines.
        text = text.replace("\n"," ")
        predictions = self.model.predict(text, k=2) # returns top 2 matching languages
        print(f"result: {predictions} text: {text}")
        if len(predictions) > 0:
            return predictions[0]
        return None

def run_identify_language():
    cache = dcachebase.DescriptionCacheBase()
    identify = LanguageIdentification()

    cache.read_description_cache()

    for base_url in cache.map_url_to_descr.keys():
        entry_obj = cache.cache_get(base_url)
        if entry_obj is not None:
            entry_obj.language_description = identify.predict_lang(entry_obj.description)
        cache.set_changed()

    cache.write_description_cache()

run_identify_language()
