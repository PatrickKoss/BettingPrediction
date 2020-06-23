from rest_framework.authtoken.models import Token
from user.utils.Message import Message
import json
from BettingRestAPI.Serializer.Encoder import ComplexEncoder


def check_authorization(request):
    if "Authorization" not in request.headers:
        message = Message("error", f"No authorization token sent")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return False, json_rep
    user = None
    try:
        user = Token.objects.get(key=request.headers.get('Authorization'))
    except Token.DoesNotExist:
        pass
    if user is None:
        message = Message("error", f"Not logged in")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return False, json_rep
    else:
        return True, None
