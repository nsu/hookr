from exchange.models import HookrUser

class HookrUserMiddleware(object):
    def process_request(self, request):
        request.user = HookrUser.objects.get(id=request.user.id)