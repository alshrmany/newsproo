# accounts/middleware.py
class ClearRegisterErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # مسح أخطاء التسجيل بعد عرضها
        if hasattr(request, 'session'):
            if 'register_errors' in request.session:
                del request.session['register_errors']
            if 'register_form_data' in request.session:
                del request.session['register_form_data']

        return response