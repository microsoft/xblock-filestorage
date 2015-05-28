"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import textwrap
import urllib2

from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Any, Boolean, Dict
from xblock.fragment import Fragment

from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
import pkg_resources
import logging
import requests
import urllib2
import tempfile
import mimetypes
import uuid

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblock.fields import Scope, String
from xblockutils.publish_event import PublishEventMixin
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit


import logging
from functools import partial
from cache_toolbox.core import del_cached_content

from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent
from opaque_keys.edx.keys import CourseKey, AssetKey
LOG = logging.getLogger(__name__)


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
        LOG.info('in studio submit')
        if not isinstance(submissions, dict):
            LOG.error("submissions object from Studio is not a dict - %r", submissions)
            return {
                'result': 'error'
            }

        self.ms_document_url = submissions['ms_document_url']
        self.reference_name = submissions['reference_name']
        self.output_model = submissions['model']

        LOG.info('output model: ' + self.output_model)

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

            LOG.info('document_url: ')
            LOG.info(document_url)

            self.output_code = "<a href="+document_url+" target='_blank'>Download the document</a>"
            course_key = CourseKey.from_string('course-v1:edX+DemoX+Demo_Course')

            onedrive_response = urllib2.urlopen('https://msopentechtest01-my.sharepoint.com/personal/student1_msopentechtest01_onmicrosoft_com/_layouts/15/guestaccess.aspx?guestaccesstoken=%2fjM%2bzKOLZXBq5F9XPFQbrqQxIVG%2fvQxKzdGvEbLvX4g%3d&docid=11424b23305084eb8ae8998a4c34f66a5')
            file = onedrive_response.read()

            tmp_file = str(uuid.uuid4())
            ext = mimetypes.guess_extension(onedrive_response.headers.type, strict=False)

            tmp_file = tmp_file + ext

            content_loc = StaticContent.compute_location(course_key, 'test.html')

            LOG.info('location: ')
            LOG.info(content_loc)

            sc_partial = partial(StaticContent, content_loc, 'test.html', onedrive_response.headers.type)

            content = sc_partial(file)
            tempfile_path = None

            # first let's see if a thumbnail can be created
            (thumbnail_content, thumbnail_location) = contentstore().generate_thumbnail(
                content,
                tempfile_path=tempfile_path,
            )

            del_cached_content(thumbnail_location)
            
            # now store thumbnail location only if we could create it
            if thumbnail_content is not None:
                content.thumbnail_location = thumbnail_location

            # then commit the content
            contentstore().save(content)
            del_cached_content(content.location)

            # readback the saved content - we need the database timestamp
            readback = contentstore().find(content.location)
            locked = getattr(content, 'locked', False)

            LOG.info('readback: ')
            LOG.info(readback)
            LOG.info('locked: ')
            LOG.info(locked)

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
