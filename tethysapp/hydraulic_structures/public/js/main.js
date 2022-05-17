$(document).ajaxComplete(function() {
    $.each($('td'), function(ix, elem) {
        if ($(elem).text().length > 1000 && window.location.href.endsWith('/summary/')) {
            $(elem).css({
                'display': 'inline-block',
                'max-height': '225px',
                'overflow-y': 'scroll'
            });
        }
    });
 });
