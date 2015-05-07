""" Utility functions used within unit tests """
# -*- coding: utf-8 -*-
#

# Imports ###########################################################
from webob import Request

from xblock.fields import ScopeIds


# Methods ###########################################################
def generate_scope_ids(runtime, block_type):
    """ helper to generate scope IDs for an XBlock """
    def_id = runtime.id_generator.create_definition(block_type)
    usage_id = runtime.id_generator.create_usage(def_id)
    return ScopeIds('user', block_type, def_id, usage_id)


def make_request(body, method='POST'):
    """ helper to make a request """
    request = Request.blank('/')
    request.method = 'POST'
    request.body = body.encode('utf-8')
    request.method = method
    return request
