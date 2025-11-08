// دالة للتبديل بين نوافذ التسجيل
function switchToRegister() {
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (loginModal) {
        loginModal.hide();
    }

    setTimeout(() => {
        const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
        registerModal.show();
        clearFormErrors('registerForm');
    }, 300);
}

function switchToLogin() {
    const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
    if (registerModal) {
        registerModal.hide();
    }

    setTimeout(() => {
        const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        loginModal.show();
        clearFormErrors('loginForm');
    }, 300);
}

// دالة لعرض نافذة تسجيل الدخول
function showLoginModal(nextUrl = null) {
    if (nextUrl) {
        document.getElementById('loginNext').value = nextUrl;
        document.getElementById('registerNext').value = nextUrl;
    }

    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
    clearFormErrors('loginForm');
}

// دالة لعرض نافذة التسجيل
function showRegisterModal(nextUrl = null) {
    if (nextUrl) {
        document.getElementById('loginNext').value = nextUrl;
        document.getElementById('registerNext').value = nextUrl;
    }

    const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
    registerModal.show();
    clearFormErrors('registerForm');
}

// مسح أخطاء النماذج
function clearFormErrors(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
    }
}

// التحقق من كلمات المرور
document.addEventListener('DOMContentLoaded', function () {
    const password1 = document.getElementById('registerPassword1');
    const password2 = document.getElementById('registerPassword2');

    if (password1 && password2) {
        password2.addEventListener('input', function () {
            if (password1.value !== password2.value) {
                password2.classList.add('is-invalid');
            } else {
                password2.classList.remove('is-invalid');
            }
        });
    }

    // إغلاق الـ Modal بعد التسجيل الناجح
    const forms = document.querySelectorAll('#loginForm, #registerForm');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري المعالجة...';
                submitBtn.disabled = true;
            }
        });
    });
});

// دالة للتحقق من التسجيل قبل تنفيذ إجراء
function requireAuth(actionCallback, nextUrl = null) {
    {% if user.is_authenticated %}
    if (typeof actionCallback === 'function') {
        actionCallback();
    }
    {% else %}
    showLoginModal(nextUrl || window.location.pathname);
    {% endif %}
}

// إعادة تعيين النماذج عند إغلاق الـ Modals
document.addEventListener('DOMContentLoaded', function () {
    const modals = ['loginModal', 'registerModal'];

    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function () {
                const form = this.querySelector('form');
                if (form) {
                    form.reset();
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = modalId === 'loginModal'
                            ? '<i class="fas fa-sign-in-alt me-2"></i> تسجيل الدخول'
                            : '<i class="fas fa-user-plus me-2"></i> إنشاء حساب';
                    }
                }
                clearFormErrors(modalId === 'loginModal' ? 'loginForm' : 'registerForm');
            });
        }
    });
});