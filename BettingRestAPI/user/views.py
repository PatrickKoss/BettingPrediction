import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Permission
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from BettingRestAPI.Helper.UserHelper import create_response
from BettingRestAPI.Serializer.UserSerializer import UserSerializer
from BettingRestAPI.utils.Message import Message


# login route
class Login(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # check correctness of body
        if 'username' not in data or 'password' not in data:
            message = Message("error", f"No username or password sent")
            return create_response({"message": message.repr_json()}, status.HTTP_400_BAD_REQUEST)

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
            return create_response({"message": message.repr_json(), "token": token.key, 'user': user},
                                   status.HTTP_200_OK)
        else:
            message = Message("error", f"Either Username or Password is wrong")
            return create_response({"message": message.repr_json()}, status.HTTP_200_OK)


# logout route
class Logout(APIView):
    def post(self, request):
        # check if token is in the header
        if "Authorization" not in request.headers:
            message = Message("error", f"No authorization token sent")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        # logging out is basically deleting the token for the user
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"Successfully logged out")
        if user is None:
            message = Message("error", f"Can´t logout since nobody is logged in")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        else:
            Token.objects.get(key=request.headers.get('Authorization')).delete()
            return create_response({'message': message.repr_json()}, status.HTTP_200_OK)


# route for checking if the user is logged in. Meaning if the token exists. Returns the user to the token.
class GetAuthenticated(APIView):
    def get(self, request):
        if "Authorization" not in request.headers:
            message = Message("error", f"No authorization token sent")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        user = None
        try:
            user = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        message = Message("success", f"Yes still authenticated")
        if user is None:
            message = Message("error", f"Not authenticated")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        else:
            user_name = Token.objects.get(key=request.headers.get('Authorization')).user
            user = User.objects.get(username=user_name)
            user = UserSerializer(user).data
            return create_response({'message': message.repr_json(), 'user': user}, status.HTTP_200_OK)


# register new user
class Register(APIView):
    def post(self, request):
        if "Authorization" not in request.headers:
            message = Message("error", f"No authorization token sent")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(request.body)
        # check request body
        if 'username' not in data or 'email' not in data or 'password' not in data:
            message = Message("error", f"No username or password or email sent")
            return create_response({"message": message.repr_json()}, status.HTTP_400_BAD_REQUEST)
        staff_member = None
        try:
            staff_member = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        if staff_member is None:
            message = Message("error", f"Not authenticated")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        else:
            permission = Permission.objects.get(name="Can add user")
            staff_name = Token.objects.get(key=request.headers.get('Authorization')).user
            staff_user = User.objects.get(username=staff_name)
            if not staff_user.has_perm(permission):
                message = Message("error", f"No permission")
                return create_response({'message': message.repr_json()}, status.HTTP_403_FORBIDDEN)
            else:
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
                    return create_response({"message": message.repr_json(), "token": token.key, 'user': user},
                                           status.HTTP_200_OK)
                else:
                    message = Message("error", "")
                    for error in serialized_user.errors:
                        message.message += serialized_user.errors[error][0] + "\n"
                    return create_response({"message": message.repr_json()}, status.HTTP_400_BAD_REQUEST)


# delete user route
class DeleteUser(APIView):
    def post(self, request, id):
        if "Authorization" not in request.headers:
            message = Message("error", f"No authorization token sent")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        staff_member = None
        try:
            staff_member = Token.objects.get(key=request.headers.get('Authorization'))
        except Token.DoesNotExist:
            pass
        if staff_member is None:
            message = Message("error", f"Not authenticated")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        else:
            staff_name = Token.objects.get(key=request.headers.get('Authorization')).user
            staff_member = User.objects.get(username=staff_name)
            permission = Permission.objects.get(name="Can delete user")
            if not staff_member.has_perm(permission):
                message = Message("error", f"No permission")
                return create_response({'message': message.repr_json()}, status.HTTP_403_FORBIDDEN)
            else:
                delete_user = User.objects.filter(id=id)
                if len(delete_user) == 0:
                    message = Message("error", f"User does not exist")
                    return create_response({'message': message.repr_json()}, status.HTTP_400_BAD_REQUEST)
                else:
                    token, _ = Token.objects.get_or_create(user=delete_user)
                    Token.objects.get(key=token).delete()
                    delete_user.delete()
                    message = Message("success", f"Successfully deleted account {delete_user.name}")
                    return create_response({'message': message.repr_json()}, status.HTTP_200_OK)


# update user data
class UpdateUser(APIView):
    def post(self, request):
        if "Authorization" not in request.headers:
            message = Message("error", f"No authorization token sent")
            return create_response({'message': message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
        data = json.loads(request.body)
        if 'username' not in data or 'email' not in data or 'password' not in data:
            message = Message("error", f"No username or password or email sent")
            return create_response({"message": message.repr_json()}, status.HTTP_400_BAD_REQUEST)
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
                return create_response({"message": message.repr_json(), "token": token.key, 'user': user},
                                       status.HTTP_200_OK)
            else:
                message = Message("error", "")
                for error in serialized_user.errors:
                    message.message += serialized_user.errors[error][0] + "\n"
                return create_response({"message": message.repr_json()}, status.HTTP_400_BAD_REQUEST)
        else:
            message = Message("error", f"Authentication failed")
            return create_response({"message": message.repr_json()}, status.HTTP_401_UNAUTHORIZED)
