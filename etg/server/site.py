"""
The code for generating the site.
"""
import os
from random import randrange
from twisted.logger import Logger
from twisted.web import resource, static
from twisted.web.util import redirectTo
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .resources import Assets, render_file
from .session import get_session_state

# pylint: disable=invalid-name
log = Logger("etg.site")

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
            autoescape=select_autoescape(['html', 'xml']))
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
        self.putChild(b'company.html', CompanyResource(self.service, self.env))
        self.putChild(b'create_company.html', CompanyCreationResource(self.service, self.env))
        self.putChild(b'admin.html', AdminResource(self.service, self.env))
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
                energy_types.append({'name': etype.name, 'taxes': randrange(-20, 20)})
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
        try:
            state.taxes
        except AttributeError:
            return redirectTo(b"/create_party.html", request)
        name = request.args[b'partyname'][0].decode('utf-8')
        parties = list(filter(lambda p: p.name == name, self.service.simulation.parties))
        companies = list(filter(lambda p: p.name == name, self.service.simulation.companies))
        if len(parties) != 0 or len(companies) != 0:
            log.warn("Player tried to name party {name}, but this entity already exists!",
                     name=name)
            return redirectTo(b"/create_party.html", request)
        state.name = name
        with self.service.simulation as sim:
            sim.add_party(state.name, state.taxes, "rgb(0,0,255)")
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
                                    starttab='Inputs',
                                    energy_types=self.service.simulation.energy_types) \
                                            .encode('utf-8')

class CompanyCreationResource(resource.Resource):
    """
    This class is responsible for giving the players a way to create a new company.
    """
    isLeaf = True

    def __init__(self, service, env, template_name="create_company"):
        super().__init__()
        self.service = service
        self.template = env.get_template(template_name + ".html")

    def render_GET(self, request):
        """
        Generates a random company and then presents it to the player.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        types = self.service.simulation.energy_types
        try:
            state.tiers
        except AttributeError:
            tiers = []
            if randrange(5) == 0:
                idx = randrange(len(types))
                tiers.append({'name': types[idx].name, 'tier': 2})
            else:
                idx = nidx = randrange(len(types))
                tiers.append({'name': types[idx].name, 'tier': 1})
                while idx == nidx:
                    nidx = randrange(len(types))
                tiers.append({'name': types[nidx].name, 'tier':1})
            state.tiers = tiers
        string = ' and '.join("a {} plant".format(tier['name']) for tier in state.tiers)
        return self.template.render(title="Company Creation",
                                    plants=string, tier=state.tiers[0]['tier']).encode('utf-8')

class CompanyResource(resource.Resource):
    """
    The class that builds the company interface.
    """
    isLeaf = True

    def __init__(self, service, env, template_name="company"):
        super().__init__()
        self.service = service
        self.template = env.get_template(template_name + ".html")

    def render_POST(self, request):
        """
        Render the page after a post request, so we got a new name for the company.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        try:
            state.tiers
        except AttributeError:
            return redirectTo(b"/create_company.html", request)
        name = request.args[b'companyname'][0].decode('utf-8')
        parties = list(filter(lambda p: p.name == name, self.service.simulation.parties))
        companies = list(filter(lambda p: p.name == name, self.service.simulation.companies))
        if len(parties) != 0 or len(companies) != 0:
            log.warn("Player tried to name company {name}, but this entity already exists!",
                     name=name)
            return redirectTo(b"/create_company.html", request)
        state.name = name
        with self.service.simulation as sim:
            sim.add_company(state.name, state.tiers, "rgb(0, 0, 255)")
        return self.render_interface(request)

    def render_GET(self, request):
        """
        Render the page for a party based on the session information from the request.
        """
        # pylint: disable=invalid-name
        state = get_session_state(request)
        if state.name == '':
            return redirectTo(b"/create_company.html", request)
        else:
            return self.render_interface(request)

    def render_interface(self, request):
        """
        Render the party interface.
        """
        state = get_session_state(request)
        return self.template.render(title=state.name,
                                    name=state.name,
                                    starttab='Owned',
                                    parties=self.service.simulation.parties,
                                    energy_types=self.service.simulation.energy_types) \
                                            .encode('utf-8')

class AdminResource(resource.Resource):
    """
    A resource to render the Admin panel with start/stop buttons.
    """
    isLeaf = True

    def __init__(self, service, env, template_name="admin"):
        super().__init__()
        self.service = service
        self.template = env.get_template(template_name + ".html")

    def render_GET(self, _):
        """
        Render the actual Admin Interface.
        """
        # pylint: disable=invalid-name
        return self.template.render().encode('utf-8')
