"""
This module handles all the generation of the wegpages based on Jinja2 templates.
"""
import os
import shutil
import sass
import yaml
from twisted.web import static

class Assets:
    """
    A class to generate all the assets in a common directory that is automatically generated each
    time.

    :param path: The path where the assets should be generated, if necessary. Defaults to the

    .. py:attribute:: path

       The path where the assets are generated.
    """
    def __init__(self, path="."):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        self.path = path
        self._style_path = os.path.join(self.path, 'styles')
        self._html_path = os.path.join(self.path, 'html')
        self._static_styles = None

    def get_styles_resource(self, style_dir):
        """
        A function to create a resource that allows acces to the styles. Takes the path to a
        directory with style files as either scss or css.
        """
        if not self._static_styles:
            sass.compile(dirname=(style_dir, self._style_path))
            self._static_styles = static.File(self._style_path)
        return self._static_styles

    def get_javascript_resource(self, js_dir):
        """
        A function to create a resource that allows access to the javascript files. Takes the path
        to a directory with javascript files.
        """
        # pylint: disable=no-self-use
        return static.File(js_dir)

    def get_static_html(self, templates, text_dir, **kwargs):
        """
        A function to create a resource that allows access to the static html files. Takes the path
        to a template and a YAML file with values that should go into this template. The files in
        the returned resource have the same name as the files in text_dir, but with extension
        '.html'.

        :param template: The template that the text should be rendered in. It can take any number of
                         arguments.
        :param text_dir: A folder of YAML files that give the information that the template needs.
        """
        for dirpath, _, files in os.walk(text_dir):
            out_path = dirpath.replace(text_dir, self._html_path)
            os.makedirs(out_path)
            for file_path in files:
                if file_path[0] == '.':
                    continue
                file_name, _ = os.path.splitext(file_path)
                with open(os.path.join(dirpath, file_path), 'r') as file:
                    opts = yaml.load(file)
                try:
                    template_name = opts['template']
                except KeyError:
                    template_name = file_name
                template = templates.get_template(template_name + '.html')
                with open(os.path.join(out_path, file_name + '.html'), 'w') as file:
                    file.write(template.render(**{**kwargs, **opts}))
        return static.File(self._html_path)
