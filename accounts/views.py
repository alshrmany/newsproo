# accounts/views.py - الإصدار المبسط
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

def register_view(request):
    """إنشاء حساب - الطريقة البسيطة"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # تحقق بسيط
        if not username or len(username) < 3:
            messages.error(request, 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم هذا مستخدم مسبقاً')
        elif password1 != password2:
            messages.error(request, 'كلمات المرور غير متطابقة')
        elif len(password1) < 8:
            messages.error(request, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password1
                )
                login(request, user)
                messages.success(request, f'مرحباً {username}! تم إنشاء حسابك بنجاح.')
                return redirect('news:article_list')
            except:
                messages.error(request, 'حدث خطأ أثناء إنشاء الحساب')

    return redirect('news:article_list')

def custom_login_view(request):
    """تسجيل الدخول - الطريقة البسيطة"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'مرحباً بعودتك {username}!')
            return redirect('news:article_list')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return redirect('news:article_list')
def profile(request):
    return render(request, 'account/profile.html')