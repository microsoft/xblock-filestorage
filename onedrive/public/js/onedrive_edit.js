function OneDriveDocumentEditBlock(runtime, element) {
    var clear_name_button = $('.clear-display-name', element);
    var save_button = $('.save-button', element);
    var validation_alert = $('.validation_alert', element);
    var document_url_input = $('#edit_document_url', element);
    var xblock_inputs_wrapper = $('.xblock-inputs', element);
    var edit_display_name_input = $('#edit_display_name', element);
    var error_message_div = $('.xblock-editor-error-message', element);
    var defaultName = edit_display_name_input.attr('data-default-value');

    ToggleClearDefaultName();

    $('.clear-display-name', element).bind('click', function() {
        $(this).addClass('inactive');
        edit_display_name_input.val(defaultName);
    });

    edit_display_name_input.bind('keyup', function(){
        ToggleClearDefaultName();
    });

    $('.cancel-button', element).bind('click', function() {
        runtime.notify('cancel', {});
    });

    function ToggleClearDefaultName(name, button){
        if (edit_display_name_input.val() == defaultName){
            if (!clear_name_button.hasClass('inactive')){
                clear_name_button.addClass('inactive');
            }
        }
        else {
            clear_name_button.removeClass('inactive');
        }
    }

    function SaveEditing(){
        var data = {
            'display_name': edit_display_name_input.val(),
            'document_url': document_url_input.val(),
        };

        error_message_div.html();
        error_message_div.css('display', 'none');
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            if (response.result === 'success') {
                window.location.reload(false);
            } else {
                error_message_div.html('Error: '+response.message);
                error_message_div.css('display', 'block');
            }
        });
    }
    save_button.bind('click', SaveEditing);
}
