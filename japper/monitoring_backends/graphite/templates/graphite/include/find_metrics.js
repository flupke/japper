function _render_graphite_query_preview(data, after_id)
{
    var html = 'Metrics: ';
    if (data.result.length) {
        html += '<ul>';
        $.each(
            data.result,
            function(index, entry)
            {
                console.log(entry);
                html += '<li>' + entry.text + '</li>';
            }
        );
        html += '</ul>';
    } else {
        html += '&lt;empty result&gt;';
    }
    _insert_after_or_replace(html, after_id);
}

$(function() {
    $('#{{ query_id }}').keyup(
        function()
        {
            $.getJSON(
                '{% url "graphite_find_metrics" %}',
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
