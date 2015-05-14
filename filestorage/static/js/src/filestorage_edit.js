/* Javascript for FileStorageXBlock. */
function FileStorageXBlock(runtime, element) {

  $(element).find('.save-button').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

    var data = {

      display_name: $(element).find('input[name=edit_display_name]').val(),
      download_link: $(element).find('input[name=edit_download_link]').val(),
      ms_document_url: $(element).find('input[name=edit_ms_document_url]').val(),
      embed_code: $(element).find('textarea[name=edit_embed_code]').val()

    };

    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      window.location.reload(false);
    });

  });

  $(element).find('.cancel-button').bind('click', function() {
    runtime.notify('cancel', {});
  });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
