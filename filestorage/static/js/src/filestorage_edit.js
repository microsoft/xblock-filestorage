/* Javascript for FileStorageXBlock. */
function FileStorageXBlock(runtime, element) {

  $(element).find('.save-button').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    var data = {

      display_name: $(element).find('input[name=edit_display_name]').val(),
      reference_name: $(element).find('input[name=edit_reference_name]').val(),
      document_url: $(element).find('input[name=edit_document_url]').val(),
      model: $(element).find('select[name=model]').val()

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
	
	if($mymodel > 2){

		$("#add_reference_name").hide();	
	}else{

		$("#add_reference_name").show();
	}
  });

    $(function ($) {
        /* Here's where you'd do things on page load. */

	if($("#output_models" ).val() > 2){

                $("#add_reference_name").hide();
        }

    });
}
