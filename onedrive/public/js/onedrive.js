/* Javascript for OneDriveDocumentBlock. */
function OneDriveDocumentBlock(runtime, element) {
    var iframe = $('iframe', element);
    var xblock_wrapper = $('.onedrive-xblock-wrapper', element);
    var display_name = xblock_wrapper.attr('data-display-name');

    if(iframe.length > 0){
        var iframe_src = iframe.attr('src');

        if ((iframe_src.indexOf("document") >= 0) ||
            (iframe_src.indexOf("spreadsheets") >= 0)){
            /* add class to iframe containing OneDrive document */
            iframe.addClass('no-width-height');
        }

        iframe.attr('title', display_name);
    }

    function SignalDocumentLoaded(ev, presented_within){
        var document_url = $(ev.target).attr('src');
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'publish_event'),
            data: JSON.stringify({
                url: document_url,
                displayed_in: presented_within,
                event_type: 'edx.onedrive.document.displayed'
            }),
            success: function(){
                $('.load_event_complete', element).val("I've published the event that indicates that the load has completed");
            }
        });
    }

    iframe.load(function(e){SignalDocumentLoaded(e, 'iframe');});

}
