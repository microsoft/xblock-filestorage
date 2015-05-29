"""TO-DO: Write a description of what this XBlock is."""

import textwrap

import pkg_resources
import urllib2
import mimetypes

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, String
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
from django.conf import settings

import logging
from functools import partial
from cache_toolbox.core import del_cached_content

from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent
from opaque_keys.edx.keys import CourseKey
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

            document_url = self.ms_document_url
            document_url = document_url.replace('embed', 'download')
            reference_name = self.reference_name.encode('utf8')

            course_key = CourseKey.from_string('course-v1:edX+DemoX+Demo_Course')

            onedrive_response = urllib2.urlopen(self.ms_document_url)

            file = onedrive_response.read()

            ext = mimetypes.guess_extension(onedrive_response.headers.type, strict=False)


            file_name = reference_name.replace(" ", "_") + ext

            content_loc = StaticContent.compute_location(course_key, file_name)

            sc_partial = partial(StaticContent, content_loc, file_name, onedrive_response.headers.type)

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

            asset_url = StaticContent.serialize_asset_key_with_slash(content.location)
            external_url = settings.LMS_BASE + asset_url

            self.output_code = "<a href="+asset_url+" target='_blank'>"+reference_name+"</a>"

            LOG.info('readback: ')
            LOG.info(readback)
            LOG.info('locked: ')
            LOG.info(locked)
            LOG.info('url')
            LOG.info(asset_url)
            LOG.info('external_url')
            LOG.info(external_url)
            LOG.info('portable_url')
            LOG.info(StaticContent.get_static_path_from_location(content.location))

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
