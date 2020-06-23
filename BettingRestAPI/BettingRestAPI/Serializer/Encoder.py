import json

# complex encoder for complex object Message
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)