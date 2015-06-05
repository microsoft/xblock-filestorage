"""TO-DO: Write a description of what this XBlock is."""

import textwrap

import pkg_resources
import urllib2
import mimetypes
import json

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
import re

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

    document_url = String(
        display_name="Document URL",
        help=(
            "Navigate to the document in your browser and ensure that it is public. Copy its URL and paste it into this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_DOCUMENT_URL
    )

    reference_name = String(
        display_name="Reference Name",
        help=(
            "The link text."
        ),
        scope=Scope.settings,
        default="Click here"
    )

    output_model = String(
        display_name="Ouput Model",
        help=(
            "Currently selected option for how to insert the document into the unit."
        ),
        scope=Scope.settings,
        default="3"
    )
    
    model1 = String(
        display_name="Model1 preselection",
        help=(
            "Previous selection."
        ),
        scope=Scope.settings,
        default=""
    )	

    model2 = String(
        display_name="Model2 preselection",
        help=(
            "Previous selection."
        ),
        scope=Scope.settings,
        default=""
    )	

    model3 = String(
        display_name="Model3 preselection",
        help=(
            "Previous selection."
        ),
        scope=Scope.settings,
        default="selected=selected"
    )	

    output_code = String(
        display_name="Output Iframe Embed Code",
        help=(
            "Copy the embed code into this field."
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

        self.document_url = submissions['document_url']
        self.reference_name = submissions['reference_name']
        self.output_model = submissions['model']


        if 'display_name' in submissions:

            self.display_name = submissions['display_name']


        if self.output_model == "1":

            self.output_code = "<a href="+self.document_url+" target='_blank'>"+self.reference_name+"</a>"

	    self.model1 = "SELECTED=selected"
	    self.model2 = ""
	    self.model3 = ""

        if self.output_model == "2":

            document_url = self.document_url
            document_url = document_url.replace('embed', 'download')
            reference_name = self.reference_name.encode('utf8')

            course_key = CourseKey.from_string(str(self.course_id))

            onedrive_response = urllib2.urlopen(self.document_url)

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
            LOG.info('course id')
            LOG.info(self.course_id)

	    self.model2 = "SELECTED=selected"
	    self.model1 = ""
	    self.model3 = ""

        if self.output_model == "3":

            document_url = submissions['document_url']
            self.output_code = filter.get_embed_code(url=document_url)

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

class filter():

    @staticmethod
    def get_embed_code(url):

        youtube_regex = '(https?:\/\/(www\.)?)(youtube\.com|youtu\.be|youtube\.googleapis.com)\/(?:embed\/|v\/|watch\?v=|watch\?.+&amp;v=|watch\?.+&v=)?((\w|-){11})(.*?)'

        matched = re.match(youtube_regex, url)

        if matched is not None:
            embed_url = "http://www.youtube.com/oembed?url=" + matched.group() + "&format=json";
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        onedrive_regex = '(https?:\/\/(onedrive\.)?)(live\.com)'

        matched = re.match(onedrive_regex, url)

        if matched is not None:
            document_url = url.replace('view.aspx', 'embed').replace('redir', 'embed')
            return MS_EMBED_CODE_TEMPLATE.format(document_url)

        google_document_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(document|spreadsheets)'

        matched = re.match(google_document_regex, url)

        if matched is not None:
            embed_code = MS_EMBED_CODE_TEMPLATE.format(url)
            return embed_code

        google_presentation_regex = '(https?:\/\/(docs\.)?)(google\.com)\/(presentation)'

        matched = re.match(google_presentation_regex, url)

        if matched is not None:
            embed_code = MS_EMBED_CODE_TEMPLATE.format(url.replace('pub', 'embed'))
            return embed_code

        ted_regex = '(https?:\/\/(www\.)?)(ted\.com)\/talks'

        matched = re.match(ted_regex, url)

        if matched is not None:
            embed_url = "http://www.ted.com/services/v1/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        vimeo_regex = 'https?:\/\/(www\.)?vimeo\.com\/'

        matched = re.match(vimeo_regex, url)

        if matched is not None:
            embed_url = "https://vimeo.com/api/oembed.json?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        office_mix_regex = '(https?:\/\/(www\.)?)(mix\.office\.com)/watch'

        matched = re.match(office_mix_regex, url)

        if matched is not None:
            embed_url = "https://mix.office.com/oembed/?url=" + url
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        slideshare_regex = 'https?:\/\/(www\.)?slideshare\.net'

        matched = re.match(slideshare_regex, url)

        if matched is not None:
            embed_url = "http://www.slideshare.net/api/oembed/2?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        issuu_regex = 'https?:\/\/(www\.)?issuu\.com'

        matched = re.match(issuu_regex, url)

        if matched is not None:
            embed_url = "http://issuu.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        screenr_regex = 'https?:\/\/(www\.)?screenr\.com'

        matched = re.match(screenr_regex, url)

        if matched is not None:
            embed_url = "http://www.screenr.com/api/oembed.json?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']

        soundcloud_regex = 'https?:\/\/(www\.)?soundcloud\.com'

        matched = re.match(soundcloud_regex, url)

        if matched is not None:
            embed_url = "http://soundcloud.com/oembed?url=" + url + "&format=json"
            res = json.load(urllib2.urlopen(embed_url))
            return res['html']
