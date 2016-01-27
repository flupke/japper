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

function _render_graphite_query_preview(data, after_id)
{
    var html = 'Query preview: ';
    if (Object.keys(data.result).length) {
        html += '<ul>';
        $.each(
            data.result,
            function(target, value)
            {
                html += '<li>' + target + ": " + value + '</li>';
            }
        );
        html += '</ul>';
    } else {
        html += '&lt;empty result&gt;';
    }
    _insert_after_or_replace(html, after_id);
}

function _render_graphite_error(data, after_id)
{
    _insert_after_or_replace('Error: ' + data.error, after_id);
}

$(function() {
    $('#{{ query_id }}').keyup(
        function()
        {
            $.getJSON(
                '{% url "graphite_query_preview" %}',
                {
                    query: $('#{{ query_id }}').val(),
                    {% if graphite_endpoint_id %}
                    endpoint: $('#{{ graphite_endpoint_id }}').val()
                    {% else %}
                    endpoint: '{{ graphite_endpoint }}'
                    {% endif %}
                },
                function(data)
                {
                    if (data.status == 'ok') {
                        _render_graphite_query_preview(data, '{{ anchor_id }}');
                    } else if (data.status == 'error') {
                        _render_graphite_error(data, '{{ anchor_id }}');
                    } else {
                        console.log('got invalid response', data);
                    }
                }
            );
        }
    );
});
