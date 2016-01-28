function _insert_after_or_replace(content, after_id) {
    var after_sel = '#' + after_id;
    var container_id = after_id + '_after';
    var container_sel = '#' + container_id;

    if ($(container_sel).length) {
        $(container_sel).html(content);
    } else {
        $('<div class="help-block" id="' + container_id + '">' + content + '</div>').insertAfter(after_sel);
    }
}

function _render_graphite_error(data, after_id)
{
    _insert_after_or_replace('Error: ' + data.error, after_id);
}

