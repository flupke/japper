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

$(function() {
    $('#{{ query_id }}').keyup(
        function()
        {
            $.getJSON(
                '{% url "graphite_query_preview" %}',
                {
                    query: $('#{{ query_id }}').val(),
                    {% if graphite_endpoint_id %}
                    endpoint: $('#{{ graphite_endpoint_id }}').val(),
                    {% else %}
                    endpoint: '{{ graphite_endpoint }}',
                    {% endif %}
                    {% if graphite_aggregate_over_id %}
                    aggregate_over: $('#{{ graphite_aggregate_over_id }}').val()
                    {% else %}
                    aggregate_over: '{{ graphite_aggregate_over }}'
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
