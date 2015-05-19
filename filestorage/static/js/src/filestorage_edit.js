/* Javascript for FileStorageXBlock. */
function FileStorageXBlock(runtime, element) {

  $(element).find('.save-button').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    var data = {

      display_name: $(element).find('input[name=edit_display_name]').val(),
      reference_name: $(element).find('input[name=edit_reference_name]').val(),
      ms_document_url: $(element).find('input[name=edit_ms_document_url]').val(),
      model: $(element).find('select[name=model]').val(),

    };

    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      window.location.reload(false);
    });



  });

   $('.cancel-button', element).bind('click', function() {
        runtime.notify('cancel', {});
    });


  $('#output_models').bind('change', function() {

	$mymodel = $("#output_models" ).val();
	
	if($mymodel > 1){

		$("#add_reference_name").hide();	
	}else{

		$("#add_reference_name").show();	

	}
  });

    $(function ($) {
        /* Here's where you'd do things on page load. */

	if($("#output_models" ).val() > 1){

                $("#add_reference_name").hide();
        }

    });
}
