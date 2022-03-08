from jinja2 import Template


class RenderStatic:

    def __init__(self, text_render):
        self.main_page_template = Template(RenderStatic.readfile("main.template"))
        self.main_page_mobile_template = Template(RenderStatic.readfile("main_mobile.template"))
        self.search_page_template = Template(RenderStatic.readfile("search.template"))
        self.search_page_mobile_template = Template(RenderStatic.readfile("search_mobile.template"))
        self.text_render = text_render

    def render(self,lang):

        def render_imp(mpg_template, srch_template):
            RenderStatic.writefile( main_file_name, 
                    mpg_template.render(
                        search_file=search_file_name, 
                        all_cats_file=all_cats_file) )

            RenderStatic.writefile( search_file_name,
                    srch_template.render(
                        top=self.text_render.show_text_str("[Top]"),
                        go=self.text_render.show_text_str("Search"),
                        openNewTab=self.text_render.show_text_str("Search results in new browser tab")))


        suffix=""
        if lang is not None and lang != "":
            suffix = f"_{lang}"
        main_file_name = f"main{suffix}.html"
        search_file_name = f"search{suffix}.html"
        all_cats_file = f"all_cats{suffix}.html"

        render_imp(self.main_page_template, self.search_page_template)

        main_file_name = f"main_mobile{suffix}.html"
        search_file_name = f"search_mobile{suffix}.html"
        all_cats_file = f"all_cats_mobile{suffix}.html"

        render_imp(self.main_page_mobile_template, self.search_page_mobile_template)


    @staticmethod
    def writefile(file_name, data):
        with open(file_name,'w') as file_obj:
            return file_obj.write(data)

    @staticmethod
    def readfile(file_name):
        with open(file_name,'r') as file_obj:
            return file_obj.read()
        raise ValueError(f"Can't read file {file_name}")
