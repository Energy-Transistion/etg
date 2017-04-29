"""
The code for generating the site.
"""
import os
from twisted.web import resource, static
from jinja2 import Environment, FileSystemLoader

from .resources import Assets, render_file

# pylint: disable=too-many-instance-attributes
class ETGSite(resource.Resource):
    """
    The class resposible for grabbing the correct pages from a resource.
    """
    def __init__(self, options, service):
        super(ETGSite, self).__init__()
        self.service = service
        self.assets = Assets(path=options['assets'])
        self.styles_dir = options['styles']
        self.javascript_dir = options['javascript']
        self.html_templates = options['templates']
        self.image_path = options['images']
        self.env = Environment(
            loader=FileSystemLoader(self.html_templates),
            autoescape=False)
        self.html_info = options['html_info']
        self._generate_assets()
        self.putChild(b'', self)

    def _generate_assets(self):
        """
        A method for generating all the assets for the website. Used when creating the resource.
        """
        self.putChild(b'styles', self.assets.get_styles_resource(self.styles_dir))
        self.putChild(b'js', self.assets.get_javascript_resource(self.javascript_dir))
        self.pages = self.assets.get_static_html(self.env, self.html_info)
        self.putChild(b'images', static.File(self.image_path))

    def render_GET(self, request):
        """
        Render the index page without keeping up the server.
        """
        # pylint: disable=invalid-name
        with open(os.path.join(self.html_info, 'index.html'), 'r') as f:
            content = render_file(f, self.env, 'index')
        return content.encode('utf-8')

    # def render_GET(self, request):
    #     """
    #     Render the initial interface for the game.
    #     """
    #     # pylint: disable=invalid-name
    #     return self.pages.getChild('index.html', request).render_GET(request)

    def getChild(self, path, request):
        if path[-5:] == b".html":
            return self.pages.getChild(path, request)
        else:
            return resource.Resource.getChild(self, path, request)

class PartyResource(resource.Resource):
    """
    The class that builds the party interface.
    """
    def __init__(self, env):
        super().__init__()
        self.env = env
