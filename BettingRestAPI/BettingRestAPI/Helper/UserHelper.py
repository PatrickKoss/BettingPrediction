import json

from rest_framework.response import Response

from BettingRestAPI.Serializer.Encoder import ComplexEncoder


def create_response(data_dict, status_code):
    json_rep = json.dumps(data_dict, cls=ComplexEncoder)
    json_rep = json.loads(json_rep)
    return Response(json_rep, status=status_code)
