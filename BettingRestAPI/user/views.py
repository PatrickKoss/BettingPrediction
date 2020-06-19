import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils.Message import Message


# login route
class Login(APIView):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        user = authenticate(request, username=username, password=password)
        # check if user exists
        if user is not None:
            # get or generate token for authentication later
            token, created = Token.objects.get_or_create(user=user)
            message = Message("success", f"Successfully logged in: {data['username']}")
            user = User.objects.get(username=username)
            user = UserSerializer(user).data
            # return message, token and user information
            response = {"message": message.repr_json(), "token": token.key, 'user': user}
        else:
            message = Message("error", f"Either Username or Password is wrong")
            response = {"message": message.repr_json()}
        json_rep = json.dumps(response, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return Response(json_rep)


# logout route
class Logout(APIView):
    def post(self, request):
        # logging out is basically deleting the token for the user
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"Successfully logged out")
        if user is None:
            message = Message("error", f"Can´t logout since nobody is logged in")
        else:
            Token.objects.get(key=request.headers.get('Authorization')).delete()
        json_rep = json.dumps(message.repr_json(), cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return Response(json_rep)


# route for checking if the user is logged in. Meaning if the token exists. Returns the user to the token.
class GetAuthenticated(APIView):
    def get(self, request):
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"Yes still authenticated")
        if user is None:
            message = Message("error", f"Not authenticated")
        else:
            user_name = Token.objects.get(key=request.headers.get('Authorization')).user
            user = User.objects.get(username=user_name)
            user = UserSerializer(user).data
            json_rep = json.dumps({'message': message.repr_json(), 'user': user}, cls=ComplexEncoder)
            json_rep = json.loads(json_rep)
            return Response(json_rep)
        json_rep = json.dumps({'message': message.repr_json()}, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)

        return Response(json_rep)


# register new user
class Register(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # validate user
        serialized_user = UserSerializer(data=data)
        if serialized_user.is_valid():
            # create user
            user = User.objects.create_user(username=data['username'],
                                            email=data['email'],
                                            password=data['password'])
            token, created = Token.objects.get_or_create(user=user)
            user = UserSerializer(user).data
            message = Message("success", f"Welcome {data['username']}")
            response = {"message": message.repr_json(), "token": token.key, 'user': user}
        else:
            message = Message("error", "")
            for error in serialized_user.errors:
                message.message += serialized_user.errors[error][0] + "\n"
            response = {"message": message.repr_json()}
        json_rep = json.dumps(response, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return Response(json_rep)


# delete user route
class DeleteUser(APIView):
    def post(self, request):
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        if user is None:
            message = Message("error", f"Can´t delete the user since the authorization failed")
        else:
            user_name = Token.objects.get(key=request.headers.get('Authorization')).user
            Token.objects.get(key=request.headers.get('Authorization')).delete()
            user = User.objects.get(username=user_name)
            user.delete()
            message = Message("success", f"Successfully deleted account {user_name}")
        json_rep = json.dumps(message.repr_json(), cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return Response(json_rep)


# update user data
class UpdateUser(APIView):
    def post(self, request):
        data = json.loads(request.body)
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        if user is not None:
            serialized_user = UserSerializer(data=data)
            # validate the user and make sure that the user exists error is ignored when the username is the same as in
            # the authentication
            if serialized_user.is_valid() or str(user.user) == str(data['username']):
                # update user
                user = User.objects.get(username=user.user)
                user.username = data['username']
                user.set_password(data['password'])
                user.email = data['email']
                user.save()
                # create or get user just in case
                token, created = Token.objects.get_or_create(user=user)
                user = UserSerializer(user).data
                message = Message("success", f"Successfully updated account: {data['username']}")
                response = {"message": message.repr_json(), "token": token.key, 'user': user}
            else:
                message = Message("error", "")
                for error in serialized_user.errors:
                    message.message += serialized_user.errors[error][0] + "\n"
                response = {"message": message.repr_json()}
        else:
            message = Message("error", f"Authentication failed")
            response = {"message": message.repr_json()}
        json_rep = json.dumps(response, cls=ComplexEncoder)
        json_rep = json.loads(json_rep)
        return Response(json_rep)


# complex encoder for complex object Message
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
