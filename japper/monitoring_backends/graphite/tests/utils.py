import json

from httmock import all_requests


def build_json_response(data):
    @all_requests
    def json_response(url, request):
        return {
            'status_code': 200,
            'content': json.dumps(data)
        }
    return json_response
