from rest_framework.authtoken.models import Token
from BettingRestAPI.utils.Message import Message
import json
from BettingRestAPI.Serializer.Encoder import ComplexEncoder
from django.contrib.auth.models import User, Permission
from rest_framework import status


def check_authorization(request):
    permissions = Permission.objects.filter(
        name__in=["Can view match result", "Can view player", "Can view team", "Can view match"])
    if "Authorization" not in request.headers:
        message = Message("error", f"No authorization token sent")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return False, json_rep, status.HTTP_401_UNAUTHORIZED
    user = None
    try:
        user = Token.objects.get(key=request.headers.get('Authorization'))
    except Token.DoesNotExist:
        pass
    if user is None:
        message = Message("error", f"Not logged in")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return False, json_rep, status.HTTP_401_UNAUTHORIZED
    else:
        user_name = user.user
        user = User.objects.get(username=user_name)
        if not user.has_perms(permissions):
            message = Message("error", f"No permissions")
            json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return False, json_rep, status.HTTP_403_FORBIDDEN
        message = Message("success", f"Here is the data")
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return True, json_rep, status.HTTP_200_OK
