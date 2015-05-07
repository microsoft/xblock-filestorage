""" Constants used within tests """
# -*- coding: utf-8 -*-
#
# Constants ###########################################################
STUDIO_EDIT_WRAPPER = '<div class="wrapper-comp-settings is-active editor-with-buttons'
VALIDATION_WRAPPER = '<div class="user-inputs-and-validation">'
USER_INPUTS_WRAPPER = '<div class="xblock-inputs editor_content_wrapper">'
BUTTONS_WRAPPER = '<div class="xblock-actions">'

RESULT_SUCCESS = {'result': 'success'}
RESULT_ERROR = {'result': 'error'}
RESULT_MISSING_EVENT_TYPE = {'result': 'error', 'message': 'Missing event_type in JSON data'}

STATUS_CODE_200 = {'status_code': 200}
STATUS_CODE_400 = {'status_code': 400}
STATUS_CODE_404 = {'status_code': 404}
