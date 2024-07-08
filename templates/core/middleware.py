from account.models import CustomUserModel
from echoverse.models import Categories

class UserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_profile = CustomUserModel.objects.filter(user=request.user).first()
            if user_profile:
                request.user_profile = user_profile
        response = self.get_response(request)
        return response
    


class CategoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        categories = Categories.objects.all()
        request.categories = categories
        response = self.get_response(request)
        return response