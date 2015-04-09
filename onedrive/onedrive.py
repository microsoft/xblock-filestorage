"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import logging
import requests

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblock.fields import Scope, String
from xblockutils.publish_event import PublishEventMixin
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit

RESOURCE_LOADER = ResourceLoader(__name__)
LOG = logging.getLogger(__name__)

DOCUMENT_TEMPLATE = "/static/html/onedrive_docs.html"
DOCUMENT_EDIT_TEMPLATE = "/static/html/onedrive_docs_edit.html"

DEFAULT_EMBED_CODE = (
    "<iframe src='https://msopentechtest01-my.sharepoint.com/personal/v-vibhal_msopentechtest01_onmicrosoft_com/_layouts/15/guestaccess.aspx?guestaccesstoken="
    "snTu4LxeXjUa5udXsBpJlp77ltnNUCFAPLUKWqfzbds%3d&docid=08b94b60461904b99b59d98a2e4345cc2&action=embedview' width='891px' height='525px' frameborder='0'>"
    "This is an embedded <a target='_blank' href='http://office.com'>Microsoft Office</a> document, powered by "
    "<a target='_blank' href='http://office.com/webapps'>Office Online</a>.</iframe>"
)

DEFAULT_DOCUMENT_URL = (
    "https://msopentechtest01-my.sharepoint.com/personal/v-vibhal_msopentechtest01_onmicrosoft_com/_layouts/15/guestaccess.aspx?guestaccesstoken="
    "snTu4LxeXjUa5udXsBpJlp77ltnNUCFAPLUKWqfzbds%3d&docid=08b94b60461904b99b59d98a2e4345cc2&action=embedview"
    )

class OneDriveXBlock(XBlock, PublishEventMixin):

    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Microsoft OneDrive Document"
    )
    document_url = String(
        display_name="Document URL",
        help=(
            "Copy the OneDrive Document URL into this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_DOCUMENT_URL
    )

    embed_code = String(
        display_name="Embed Code",
        help=(
            "Embed code for OneDrive document"
        ),
        scope=Scope.settings,
        default=DEFAULT_EMBED_CODE
    )
    """
    TO-DO: document what your XBlock does.
    """

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the OneDriveXBlock, shown to students
        when viewing courses.
        """
        fragment = Fragment()

        fragment.add_content(RESOURCE_LOADER.render_template(DOCUMENT_TEMPLATE, {"self": self}))
        fragment.add_css(RESOURCE_LOADER.load_unicode('static/css/onedrive_docs.css'))
        fragment.add_javascript(RESOURCE_LOADER.load_unicode('static/js/src/onedrive_docs.js'))

        fragment.initialize_js('OneDriveDocumentBlock')

        return fragment

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
        fragment.add_javascript(RESOURCE_LOADER.load_unicode('static/js/src/onedrive_docs_edit.js'))
        fragment.add_css(RESOURCE_LOADER.load_unicode('static/css/onedrive_edit.css'))

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
        if 'onedrive_url' in submissions:

            self.document_url = submissions['onedrive_url']

            scheme, netloc, path, query_string, fragment = urlsplit(submissions['onedrive_url'])
            query_params = parse_qs(query_string)
            query_params['action'] = ['embedview']
            new_query_string = urlencode(query_params, doseq=True)

            url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

            self.embed_code = (
                "<iframe src='" + url + "' width='891px' height='525px' frameborder='0'>"
                "This is an embedded <a target='_blank' href='http://office.com'>Microsoft Office</a> "
                "document, powered by <a target='_blank' href='http://office.com/webapps'>Office Online</a>.</iframe>"
            )

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
            print "Unable to connect to %s - %s", test_url, unicode(ex)
            LOG.debug("Unable to connect to %s - %s", test_url, unicode(ex))
            return {
                'status_code': 400,
            }

        return {
            'status_code': url_response.status_code,
        }

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("OneDriveXBlock",
             """<vertical_demo>
                <onedrive/>
                <onedrive/>
                <onedrive/>
                </vertical_demo>
             """),
        ]
