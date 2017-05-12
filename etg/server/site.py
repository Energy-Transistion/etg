"""
The code for generating the site.
"""
import html
import os
from random import randrange
from twisted.web import resource, static
from twisted.web.util import redirectTo
from jinja2 import Environment, FileSystemLoader

from .resources import Assets, render_file
from .session import get_session_state

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
        self.putChild(b'party.html', PartyResource(self.service, self.env))
        self.putChild(b'create_party.html', PartyCreationResource(self.service, self.env))
        with open(os.path.join(self.html_info, 'index.html'), 'r') as html_content:
            content = render_file(html_content, self.env, 'index')
        self.content = content.encode('utf-8')

    def render_GET(self, _):
        """
        Render the index page without keeping up the server.
        """
        # pylint: disable=invalid-name
        return self.content

    def getChild(self, path, request):
        if path[-5:] == b".html":
            return self.pages.getChild(path, request)
        else:
            return resource.Resource.getChild(self, path, request)

class PartyCreationResource(resource.Resource):
    """
    This class is responsible for creating the Parties from the webinterface and then redirecting
    the players to the party interface.
    """
    isLeaf = True

    def __init__(self, service, env, template_name="create_party"):
        super().__init__()
        self.service = service
        self.template = env.get_template(template_name + ".html")

    def render_GET(self, request):
        """
        Render a page to show if we do not yet have all the necessary information for this party.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        try:
            state.taxes
        except AttributeError:
            energy_types = []
            for etype in self.service.simulation.energy_types:
                energy_types.append({'name': etype.name, 'taxes': randrange(-50, 50)})
            state.taxes = energy_types
        return self.template.render(title="Party Creation", energy_types=state.taxes) \
                .encode('utf-8')

class PartyResource(resource.Resource):
    """
    The class that builds the party interface.
    """

    isLeaf = True

    def __init__(self, service, env, template_name="party"):
        super().__init__()
        self.env = env
        self.service = service
        self.template = env.get_template(template_name + ".html")

    def render_POST(self, request):
        """
        Render the page after a post request, so we got a new name for the party.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        print(request.args)
        state.name = html.escape(request.args[b'partyname'][0].decode('utf-8'))
        return self.render_interface(request)

    def render_GET(self, request):
        """
        Render the page for a party based on the session information from the request.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        if state.name == '':
            return redirectTo(b"/create_party.html", request)
        else:
            return self.render_interface(request)

    def render_interface(self, request):
        """
        Render the party interface.
        """
        state = get_session_state(request)
        return self.template.render(title=state.name,
                                    name=state.name,
                                    energy_types=self.service.simulation.energy_types) \
                                            .encode('utf-8')
