import fasttext
import dcachebase

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
            lang_pred = predictions[0]
            if lang_pred is not None and len(lang_pred) > 0:
                return lang_pred[0]
        return None

def run_identify_language():
    cache = dcachebase.DescriptionCacheBase()
    identify = LanguageIdentification()

    cache.read_description_cache()
    num_set = 0

    for base_url in cache.map_url_to_descr.keys():
        entry_obj = cache.cache_get(base_url)
        if entry_obj is not None and entry_obj.description != '':
            descr = identify.predict_lang(entry_obj.description)
            #if descr != entry_obj.language_description
            print(f"descr: {descr}")
            entry_obj.language_description = descr
            cache.cache_set(base_url, entry_obj)
            num_set += 1
            cache.write_description_cache()

run_identify_language()
