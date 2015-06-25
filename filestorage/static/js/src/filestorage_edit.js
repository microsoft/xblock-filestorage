/* Javascript for FileStorageXBlock. */
function FileStorageXBlock(runtime, element) {

  $(element).find('.save-button').bind('click', function() {
    var display_name = $(element).find('input[name=edit_display_name]').val().trim();
    if (!display_name) {
      alert("Please enter the title for this component.");
      return;
    }

    var document_url = $(element).find('input[name=edit_document_url]').val().trim();
    if (!document_url) {
      alert("Please enter the document URL.");
      return;
    }

    var model = $(element).find('select[name=model]').val();
    var reference_text = $(element).find('input[name=edit_reference_name]').val().trim();

    if ((model == 2) && !reference_text) {
      alert("Please enter the text to use for the reference.");
      return;
    }
    
    var data = {
      display_name: display_name,
      reference_name: reference_text,
      document_url: document_url,
      model: model
    };

    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      window.location.reload(false);
    });
  });

  $('.cancel-button', element).bind('click', function() {
    runtime.notify('cancel', {});
  });

  $('#output_models').bind('change', function() {
    if ($("#output_models" ).val() == 2){
      $("#add_reference_name").show();
    } else {
      $("#add_reference_name").hide();  
    }
  });

  $(function ($) {
    /* Here's where you'd do things on page load. */
    if ($("#output_models" ).val() == 2){
      $("#add_reference_name").show();
    } else {
      $("#add_reference_name").hide();
    }
  });
}
