""" Unit tests for OneDrive components """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
import json
import unittest
from mock import Mock

from nose.tools import assert_equal, assert_not_equal, assert_in
from workbench.runtime import WorkbenchRuntime
from xblock.runtime import KvsFieldData, DictKeyValueStore

from onedrive import OneDriveDocumentBlock
from onedrive.onedrive import DEFAULT_EMBED_CODE, DEFAULT_DOCUMENT_URL
from onedrive.tests.unit.test_utils import generate_scope_ids, make_request
from onedrive.tests.test_const import (
    STUDIO_EDIT_WRAPPER, VALIDATION_WRAPPER, USER_INPUTS_WRAPPER, BUTTONS_WRAPPER
)
from onedrive.tests.test_const import RESULT_SUCCESS, RESULT_ERROR, RESULT_MISSING_EVENT_TYPE
from onedrive.tests.test_const import STATUS_CODE_200, STATUS_CODE_400

# Constants ###########################################################
TEST_SUBMIT_DATA = {
    'display_name': "OneDrive Document",
    'document_url': (
        "https://onedrive.live.com/view.aspx?cid=ADC6477D8F22FD9D&"
        "resid=ADC6477D8F22FD9D%21104&app=Word"
    ),
}
TEST_VALIDATE_URL_DATA = {
    'url': DEFAULT_DOCUMENT_URL,
}
TEST_VALIDATE_UNDEFINED_DATA = {
    'url': 'undefined'
}
TEST_VALIDATE_NONEXISTENT_URL_DATA = {
    'url': (
        "https://onedrive.live.com/embed?resid=nonexistent&ithint=file%2cdocx"
    )
}
TEST_COMPLETE_PUBLISH_DOCUMENT_DATA = {
    'url': DEFAULT_DOCUMENT_URL,
    'displayed_in': 'iframe',
    'event_type': 'edx.onedrive.document.displayed',
}
TEST_INCOMPLETE_PUBLISH_DATA = {
    'url': DEFAULT_DOCUMENT_URL,
    'displayed_in': 'iframe',
}


# Classes ###########################################################
class TestOneDriveDocumentBlock(unittest.TestCase):
    """ Tests for OneDriveDocumentBlock """

    @classmethod
    def make_document_block(cls):
        """ helper to construct a OneDriveDocumentBlock """
        runtime = WorkbenchRuntime()
        key_store = DictKeyValueStore()
        db_model = KvsFieldData(key_store)
        ids = generate_scope_ids(runtime, 'onedrive')
        return OneDriveDocumentBlock(runtime, db_model, scope_ids=ids)

    def test_document_template_content(self):  # pylint: disable=no-self-use
        """ Test content of OneDriveDocumentBlock's rendered views """
        block = TestOneDriveDocumentBlock.make_document_block()
        block.usage_id = Mock()

        student_fragment = block.render('student_view', Mock())
        # pylint: disable=no-value-for-parameter
        assert_in('<div class="onedrive-xblock-wrapper"', student_fragment.content)
        assert_in('OneDrive Document', student_fragment.content)
        assert_in(DEFAULT_EMBED_CODE, student_fragment.content)

        studio_fragment = block.render('studio_view', Mock())
        assert_in(STUDIO_EDIT_WRAPPER, studio_fragment.content)
        assert_in(VALIDATION_WRAPPER, studio_fragment.content)
        assert_in(USER_INPUTS_WRAPPER, studio_fragment.content)
        assert_in(BUTTONS_WRAPPER, studio_fragment.content)

    def test_studio_document_submit(self):  # pylint: disable=no-self-use
        """ Test studio submission of OneDriveDocumentBlock """
        block = TestOneDriveDocumentBlock.make_document_block()

        body = json.dumps(TEST_SUBMIT_DATA)
        res = block.handle('studio_submit', make_request(body))
        # pylint: disable=no-value-for-parameter
        assert_equal(json.loads(res.body), RESULT_SUCCESS)

        assert_equal(block.display_name, TEST_SUBMIT_DATA['display_name'])
        assert_equal(block.document_url, TEST_SUBMIT_DATA['document_url'])

        body = json.dumps('')
        res = block.handle('studio_submit', make_request(body))
        assert_equal(json.loads(res.body), RESULT_ERROR)

    def test_check_document_url(self):  # pylint: disable=no-self-use
        """ Test verification of the provided OneDrive Document URL"""
        block = TestOneDriveDocumentBlock.make_document_block()

        data = json.dumps(TEST_VALIDATE_URL_DATA)
        res = block.handle('check_url', make_request(data))
        # pylint: disable=no-value-for-parameter
        assert_not_equal(json.loads(res.body), STATUS_CODE_400)

        data = json.dumps(TEST_VALIDATE_UNDEFINED_DATA)
        res = block.handle('check_url', make_request(data))

        assert_equal(json.loads(res.body), STATUS_CODE_400)

        data = json.dumps(TEST_VALIDATE_NONEXISTENT_URL_DATA)
        res = block.handle('check_url', make_request(data))

        assert_not_equal(json.loads(res.body), STATUS_CODE_200)

        data = json.dumps({})
        res = block.handle('check_url', make_request(data))

        assert_equal(json.loads(res.body), STATUS_CODE_400)

    def test_document_publish_event(self):  # pylint: disable=no-self-use
        """ Test event publishing in OneDriveDocumentBlock"""
        block = TestOneDriveDocumentBlock.make_document_block()

        body = json.dumps(TEST_COMPLETE_PUBLISH_DOCUMENT_DATA)
        res = block.handle('publish_event', make_request(body))
        # pylint: disable=no-value-for-parameter
        assert_equal(json.loads(res.body), RESULT_SUCCESS)

        body = json.dumps(TEST_INCOMPLETE_PUBLISH_DATA)
        res = block.handle('publish_event', make_request(body))

        assert_equal(json.loads(res.body), RESULT_MISSING_EVENT_TYPE)
