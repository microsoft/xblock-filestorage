""" Runs tests for publish event functionality """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
from .base_test import OneDriveDocumentBaseTest


# Classes ###########################################################
class OneDriveDocumentPublishTestCase(OneDriveDocumentBaseTest):  # pylint: disable=too-many-ancestors
    """
    Tests for OneDrive event publishing functionality.
    """

    def test_document_publish_event(self):
        """ Tests whether the publish event for document was triggered """
        document = self.go_to_page('Document')
        load_event_complete = document.find_element_by_css_selector('.load_event_complete')
        self.assertEqual(
            load_event_complete.get_attribute('value'),
            "I've published the event that indicates that the load has completed"
        )
