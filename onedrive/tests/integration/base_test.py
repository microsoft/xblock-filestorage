""" Base classes for integration tests """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
from xblockutils.base_test import SeleniumBaseTest


# Classes ###########################################################
class OneDriveDocumentBaseTest(SeleniumBaseTest):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """ Base class for OneDrive Document integration tests """
    module_name = __name__
    default_css_selector = 'div.onedrive-xblock-wrapper'
