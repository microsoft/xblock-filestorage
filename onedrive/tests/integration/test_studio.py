""" Runs tests for the studio views """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
from ddt import ddt, unpack, data
from .base_test import OneDriveDocumentBaseTest
from .studio_scenarios import DOCUMENT_SCENARIOS
from onedrive.onedrive import DEFAULT_DOCUMENT_URL


# Classes ###########################################################
@ddt  # pylint: disable=too-many-ancestors
class OneDriveDocumentStudioTest(OneDriveDocumentBaseTest):
    """
    Tests for OneDrive Document studio view.
    """
    default_css_selector = '#document-settings-tab'

    def studio_save(self):
        """ Save changes made in studio for OneDrive Document """
        self.browser.find_element_by_css_selector('#document-submit-options').click()

    @data(*DOCUMENT_SCENARIOS)
    @unpack
    def test_save_document(self, page_name):
        """
        Verify that option changes in OneDrive Document studio view
        are appropriately saved and visible immediately after
        """
        self.go_to_page(page_name, view_name='studio_view')
        # Expecting every input value to be valid
        self.assertTrue(self.browser.find_element_by_css_selector('.validation_alert.covered'))
        display_name_input = self.browser.find_element_by_css_selector('#edit_display_name')
        # Change display name
        display_name_input.clear()
        display_name_input.send_keys('My Document')

        self.studio_save()
        self.go_to_page(page_name, css_selector='div.onedrive-xblock-wrapper')
        document_iframe = self.browser.find_element_by_css_selector('iframe')
        # Expecting that default document is the one loaded in the IFrame
        self.assertEqual(document_iframe.get_attribute("src"), DEFAULT_DOCUMENT_URL)
        # Expecting that the new display name is the title of the IFrame
        self.assertEqual(document_iframe.get_attribute("title"), 'My Document')
