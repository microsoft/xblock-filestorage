"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import textwrap
import urllib2

from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Any, Boolean, Dict
from xblock.fragment import Fragment

from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

""" easy for develop, to be removed"""

DEFAULT_DOCUMENT_URL = (
    'https://onedrive.live.com/embed?cid=ADC6477D8F22FD9D&resid=ADC6477D8F22FD9D%21104&'
    'authkey=AFWEOfGpKb8L29w&em=2&wdStartOn=1'
)
MS_EMBED_CODE_TEMPLATE = textwrap.dedent("""
    <iframe
        src="{}"
        frameborder="0"
        width="960"
        height="569"
        allowfullscreen="true"
        mozallowfullscreen="true"
        webkitallowfullscreen="true">
    </iframe>
""")



class FileStorageXBlock(XBlock):


    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="File Storage",
    )


    ms_document_url = String(
        display_name="Document URL",
        help=(
            "select Share from the menu, click Get a Link and copy the link to this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_DOCUMENT_URL
    )

    reference_name = String(
        display_name="Reference Name",
        help=(
            "The name used as link."
        ),
        scope=Scope.settings,
        default=""
    )

    output_model = String(
        display_name="Ouput Model",
        help=(
            "The name used as link."
        ),
        scope=Scope.settings,
        default="3"
    )
    
    model1 = String(
        display_name="Model1 preselection",
        help=(
            "preselect from."
        ),
        scope=Scope.settings,
        default=""
    )	
    model2 = String(
        display_name="Model2 preselection",
        help=(
            "preselect from."
        ),
        scope=Scope.settings,
        default=""
    )	
    model3 = String(
        display_name="Model3 preselection",
        help=(
            "preselect from."
        ),
        scope=Scope.settings,
        default="selected=selected"
    )	
    output_code = String(
        display_name="Output Iframe Embed Code",
        help=(
            "select Embed from the menu and copy the embed code into this field."
        ),
        scope=Scope.settings,
        default=MS_EMBED_CODE_TEMPLATE.format(DEFAULT_DOCUMENT_URL)
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        The primary view of the FileStorageXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/filestorage.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/filestorage.css"))
        frag.add_javascript(self.resource_string("static/js/src/filestorage.js"))
        frag.initialize_js('FileStorageXBlock')
        return frag


    def studio_view(self, context=None):
        """
        he primary view of the FileStorageXBlock, shown to teachers
        when viewing courses.
        """

        html = self.resource_string("static/html/filestorage_edit.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/filestorage.css"))
        frag.add_javascript(self.resource_string("static/js/src/filestorage_edit.js"))
        frag.initialize_js('FileStorageXBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):  # pylint: disable=unused-argument
        """
        Change the settings for this XBlock given by the Studio user
        """
        if not isinstance(submissions, dict):
            LOG.error("submissions object from Studio is not a dict - %r", submissions)
            return {
                'result': 'error'
            }

        self.ms_document_url = submissions['ms_document_url']
        self.reference_name = submissions['reference_name']
        self.output_model = submissions['model']

        if 'display_name' in submissions:

            self.display_name = submissions['display_name']


        if self.output_model == "1":

            self.output_code = "<a href="+self.ms_document_url+" target='_blank'>"+self.reference_name+"</a>"

	    self.model1 = "SELECTED=selected"
	    self.model2 = ""
	    self.model3 = ""

        if self.output_model == "2":

            document_url = submissions['ms_document_url']
            document_url = document_url.replace('embed', 'download')

            self.output_code = "<a href="+document_url+" target='_blank'>Download the document</a>"
	    
	    self.model2 = "SELECTED=selected"
	    self.model1 = ""
	    self.model3 = ""

        if self.output_model == "3":

            document_url = submissions['ms_document_url']
            document_url = document_url.replace('view.aspx', 'embed').replace('redir', 'embed')

            scheme, netloc, path, query_string, fragment = urlsplit(document_url)
            query_params = parse_qs(query_string)
            query_params['action'] = ['embedview']
            query_params['em'] = ['2']
            new_query_string = urlencode(query_params, doseq=True)

            document_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

            self.output_code = MS_EMBED_CODE_TEMPLATE.format(document_url)

	    self.model3 = "SELECTED=selected"
	    self.model2 = ""
	    self.model1 = ""

        return {'result': 'success'}


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("FileStorageXBlock",
             """<vertical_demo>
                <filestorage/>
                <filestorage/>
                <filestorage/>
                </vertical_demo>
             """),
        ]
