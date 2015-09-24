""" 
The "File Storage XBlock" allows course staffers to add files stored in various internet file storage services to the courseware (courseware, course info and syllabus) 
by adding a link through an advanced component that they create in edX's Studio authoring tool. The files can be added either as embedded content, 
or as links to the files in their original location.
""" 

import textwrap

import pkg_resources
import urllib2
import mimetypes

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblock.fields import Scope, String
from django.conf import settings

import logging
from functools import partial
from cache_toolbox.core import del_cached_content

from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent
from opaque_keys.edx.keys import CourseKey
LOG = logging.getLogger(__name__)
from filter import Filter

DEFAULT_DOCUMENT_URL = ('https://onedrive.live.com/embed?cid=ADC6477D8F22FD9D&resid=ADC6477D8F22FD9D%21104&authkey=AFWEOfGpKb8L29w&em=2&wdStartOn=1')

class FileStorageXBlock(XBlock):

    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="File Storage",
    )

    document_url = String(
        display_name="Document URL",
        help="Navigate to the document in your browser and ensure that it is public. Copy its URL and paste it into this field.",
        scope=Scope.settings,
        default=DEFAULT_DOCUMENT_URL
    )

    reference_name = String(
        display_name="Reference Name",
        help="The link text.",
        scope=Scope.settings,
        default=""
    )

    output_model = String(
        display_name="Ouput Model",
        help="Currently selected option for how to insert the document into the unit.",
        scope=Scope.settings,
        default="1"
    )
    
    model1 = String(
        display_name="Model1 preselection",
        help="Previous selection.",
        scope=Scope.settings,
        default=""
    )	

    model2 = String(
        display_name="Model2 preselection",
        help="Previous selection.",
        scope=Scope.settings,
        default=""
    )	

    # model3 = String(
        # display_name="Model3 preselection",
        # help="Previous selection.",
        # scope=Scope.settings,
        # default="selected=selected"
    # )	

    output_code = String(
        display_name="Output Iframe Embed Code",
        help="Copy the embed code into this field.",
        scope=Scope.settings,
        default=Filter.EMBED_CODE_TEMPLATE.format(DEFAULT_DOCUMENT_URL)
    )

    message = String(
        display_name="Document display status message",
        help="Message to help students in case of errors.",
        scope=Scope.settings,
        default="Note: Some services may require you to be signed into them to access documents stored there."
    )

    message_display_state = String(
        display_name="Whether to display the status message",
        help="Determines whether to display the message to help students in case of errors.",
        scope=Scope.settings,
        default="block"
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

        # output model = 1 means embed the document
        if self.output_model == "1":
            self.output_code = Filter.get_embed_code(url=self.document_url)
            self.message = "Note: Some services may require you to be signed into them to access documents stored there."
            self.message_display_state = "block"

	    self.model1 = "SELECTED=selected"
	    self.model2 = ""
	    # self.model3 = ""

        # output model = 2 means add a reference to the document
        if self.output_model == "2":
            self.output_code = "<a href="+self.document_url+" target='_blank'>"+self.reference_name+"</a>"
            self.message = ""
            self.message_display_state = "none"

	    self.model1 = ""
	    self.model2 = "SELECTED=selected"
	    # self.model3 = ""

        # output model = 3 means upload the document and add a reference to it
        # if self.output_model == "3":
            # download_url = Filter.get_download_url(self.document_url)
            # reference_name = self.reference_name.encode('utf8')
            # course_key = CourseKey.from_string(str(self.course_id))

            # try:
                # download_response = urllib2.urlopen(download_url)
                # file = download_response.read()
            # except:
                # self.output_code = "Unable to upload the document: " + self.document_url
                # return {'result': 'error'}

            # ext = mimetypes.guess_extension(download_response.headers.type, strict=False)
            # file_name = reference_name.replace(" ", "_") + ext
            # content_loc = StaticContent.compute_location(course_key, file_name)
            # sc_partial = partial(StaticContent, content_loc, file_name, download_response.headers.type)
            # content = sc_partial(file)

            # tempfile_path = None

            # # first let's see if a thumbnail can be created
            # (thumbnail_content, thumbnail_location) = contentstore().generate_thumbnail(
                # content,
                # tempfile_path=tempfile_path,
            # )

            # del_cached_content(thumbnail_location)
            
            # # now store thumbnail location only if we could create it
            # if thumbnail_content is not None:
                # content.thumbnail_location = thumbnail_location

            # # then commit the content
            # contentstore().save(content)
            # del_cached_content(content.location)

            # # readback the saved content - we need the database timestamp
            # readback = contentstore().find(content.location)
            # locked = getattr(content, 'locked', False)

            # asset_url = StaticContent.serialize_asset_key_with_slash(content.location)
            # external_url = settings.LMS_BASE + asset_url

            # self.output_code = "<a href="+asset_url+" target='_blank'>"+reference_name+"</a>"
            # self.message = ""
            # self.message_display_state = "none"

	    # self.model1 = ""
	    # self.model2 = ""
	    # self.model3 = "SELECTED=selected"

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
