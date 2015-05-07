""" OneDrive for Business Document XBlock implementation """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
import logging
import textwrap
import requests

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from xblockutils.publish_event import PublishEventMixin
from xblockutils.resources import ResourceLoader

from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

LOG = logging.getLogger(__name__)
RESOURCE_LOADER = ResourceLoader(__name__)

# Constants ###########################################################
DEFAULT_DOCUMENT_URL = (
    'https://onedrive.live.com/embed?cid=ADC6477D8F22FD9D&resid=ADC6477D8F22FD9D%21104&'
    'authkey=AFWEOfGpKb8L29w&em=2&wdStartOn=1'
)
EMBED_CODE_TEMPLATE = textwrap.dedent("""
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
DEFAULT_EMBED_CODE = EMBED_CODE_TEMPLATE.format(DEFAULT_DOCUMENT_URL)
DOCUMENT_TEMPLATE = "/templates/html/onedrive.html"
DOCUMENT_EDIT_TEMPLATE = "/templates/html/onedrive_edit.html"


# Classes ###########################################################
class OneDriveDocumentBlock(XBlock, PublishEventMixin):  # pylint: disable=too-many-ancestors
    """
    XBlock providing a OneDrive document embed link
    """
    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="OneDrive for Business Document"
    )
    document_url = String(
        display_name="Document URL",
        help=(
            "Microsoft provides a sharing link for OneDrive documents. In the OneDrive document, "
            "select Share from the menu, click Get a Link and copy the link to this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_DOCUMENT_URL
    )
    embed_code = String(
        display_name="Embed Code",
        help=(
            "Microsoft provides an embed code for OneDrive documents. In the OneDrive document, "
            "select Embed from the menu and copy the embed code into this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_EMBED_CODE
    )

    # Context argument is specified for xblocks, but we are not using herein
    def student_view(self, context):  # pylint: disable=unused-argument
        """
        Player view, displayed to the student
        """
        fragment = Fragment()

        fragment.add_content(RESOURCE_LOADER.render_template(DOCUMENT_TEMPLATE, {"self": self}))
        fragment.add_css(RESOURCE_LOADER.load_unicode('public/css/onedrive.css'))
        fragment.add_javascript(RESOURCE_LOADER.load_unicode('public/js/onedrive.js'))

        fragment.initialize_js('OneDriveDocumentBlock')

        return fragment

    # Context argument is specified for xblocks, but we are not using herein
    def studio_view(self, context):  # pylint: disable=unused-argument
        """
        Editing view in Studio
        """
        fragment = Fragment()
        # Need to access protected members of fields to get their default value
        fragment.add_content(RESOURCE_LOADER.render_template(DOCUMENT_EDIT_TEMPLATE, {
            'self': self,
            'defaultName': self.fields['display_name']._default  # pylint: disable=protected-access
        }))
        fragment.add_javascript(RESOURCE_LOADER.load_unicode('public/js/onedrive_edit.js'))
        fragment.add_css(RESOURCE_LOADER.load_unicode('public/css/onedrive_edit.css'))

        fragment.initialize_js('OneDriveDocumentEditBlock')

        return fragment

    # suffix argument is specified for xblocks, but we are not using herein
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

        if 'display_name' in submissions:
            self.display_name = submissions['display_name']

        if 'document_url' in submissions:
            self.document_url = submissions['document_url']
            document_url = submissions['document_url']
            document_url = document_url.replace('view.aspx', 'embed').replace('redir', 'embed')

            scheme, netloc, path, query_string, fragment = urlsplit(document_url)
            query_params = parse_qs(query_string)
            query_params['action'] = ['embedview']
            query_params['em'] = ['2']
            new_query_string = urlencode(query_params, doseq=True)

            document_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

            self.embed_code = EMBED_CODE_TEMPLATE.format(document_url)

        return {
            'result': 'success',
        }

    # suffix argument is specified for xblocks, but we are not using herein
    @XBlock.json_handler
    def check_url(self, data, suffix=''):  # pylint: disable=unused-argument,no-self-use
        """
        Checks that the given document url is accessible, and therefore assumed to be valid
        """
        try:
            test_url = data['url']
        except KeyError as ex:
            LOG.debug("URL not provided - %s", unicode(ex))
            return {
                'status_code': 400,
            }

        try:
            url_response = requests.head(test_url)
        # Catch wide range of request exceptions
        except requests.exceptions.RequestException as ex:
            LOG.debug("Unable to connect to %s - %s", test_url, unicode(ex))
            return {
                'status_code': 400,
            }

        return {
            'status_code': url_response.status_code,
        }

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """
        return [("OneDrive scenario", "<vertical_demo><onedrive/></vertical_demo>")]
