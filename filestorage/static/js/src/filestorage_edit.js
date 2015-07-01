/* Javascript for FileStorageXBlock. */
function FileStorageXBlock(runtime, element) {

  var display_name = $(element).find('input[name=edit_display_name]');
  var document_url = $(element).find('input[name=edit_document_url]');
  var model = $(element).find('select[name=model]');
  var reference_name = $(element).find('input[name=edit_reference_name]');
  var error_message = $(element).find('.filestorage-xblock .error-message');

  $(element).find('.save-button').bind('click', function() {
    var display_name_val = display_name.val().trim();
    var document_url_val = document_url.val().trim();
    var model_val = model.val();
    var reference_name_val = reference_name.val().trim();

    clearErrors();
    
    if (!display_name_val) {
      display_name.addClass('error');
      error_message.addClass('visible');
      return;
    }

    if (!document_url_val || (!isValidUrl(document_url_val) && !isValidEmbedCode(document_url_val))) {
      document_url.addClass('error');
      error_message.addClass('visible');
      return;
    }

    if ((model_val != 1) && isValidEmbedCode(document_url_val)) {
      document_url.addClass('error');
      error_message.addClass('visible');
      return;
    }

    if ((model_val == 2) && !reference_name_val) {
      reference_name.addClass('error');
      error_message.addClass('visible');
      return;
    }
    
    var data = {
      display_name: display_name_val,
      reference_name: reference_name_val,
      document_url: document_url_val,
      model: model_val
    };

    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      window.location.reload(false);
    });
  });

  display_name.bind('keyup', function(){
    clearErrors();
  });

  document_url.bind('keyup', function(){
    clearErrors();
  });

  reference_name.bind('keyup', function(){
    clearErrors();
  });

  $('.cancel-button', element).bind('click', function() {
    runtime.notify('cancel', {});
  });

  $('#output_models').bind('change', function() {
    clearErrors();
    if ($("#output_models" ).val() == 2){
      $("#add_reference_name").show();
    } else {
      $("#add_reference_name").hide();  
    }
  });
  
  function clearErrors() {
    display_name.removeClass('error');
    document_url.removeClass('error');
    reference_name.removeClass('error');
    error_message.removeClass('visible');
  }
  
  function isValidUrl(url) {
    return /^(https?):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(url);
  }
  
  function isValidEmbedCode(code) {
    return /<iframe /i.test(code);
  }
  

  $(function ($) {
    /* Here's where you'd do things on page load. */
    if ($("#output_models" ).val() == 2){
      $("#add_reference_name").show();
    } else {
      $("#add_reference_name").hide();
    }
  });
}
