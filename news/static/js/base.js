// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function () {
    // تحديث التاريخ والوقت
    function updateDateTime() {
        const now = new Date()
        const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
        const timeOptions = { hour: '2-digit', minute: '2-digit' }

        const dateElement = document.getElementById('current-date')
        const timeElement = document.getElementById('current-time')
        const yearElement = document.getElementById('year')

        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('ar-SA', dateOptions)
        }

        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('ar-SA', timeOptions)
        }

        if (yearElement) {
            yearElement.textContent = now.getFullYear()
        }
    }

    updateDateTime()
    setInterval(updateDateTime, 60000)

    // الأخبار العاجلة - تدوير تلقائي
    const breakingNewsItems = document.querySelectorAll('.breaking-news-item')
    if (breakingNewsItems.length > 0) {
        let currentItem = 0

        setInterval(() => {
            breakingNewsItems[currentItem].classList.remove('active')
            currentItem = (currentItem + 1) % breakingNewsItems.length
            breakingNewsItems[currentItem].classList.add('active')
        }, 5000)
    }

    // إدارة حجم الخط
    const baseFontSize = 16
    let currentFontSize = baseFontSize

    document.getElementById('increaseFont')?.addEventListener('click', function () {
        if (currentFontSize < 24) {
            currentFontSize += 2
            updateFontSize()
        }
    })

    document.getElementById('decreaseFont')?.addEventListener('click', function () {
        if (currentFontSize > 12) {
            currentFontSize -= 2
            updateFontSize()
        }
    })

    document.getElementById('resetFont')?.addEventListener('click', function () {
        currentFontSize = baseFontSize
        updateFontSize()
    })

    function updateFontSize() {
        document.body.style.fontSize = currentFontSize + 'px'
        document.getElementById('currentFontSize').textContent = currentFontSize + 'px'
    }

    // تهيئة AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        })
    }

    // تحديث أزرار الوضع الليلي/النهاري بناءً على النظام الجديد
    function updateThemeButtons() {
        const isNightMode = document.documentElement.getAttribute('data-theme') === 'night';

        document.querySelectorAll('.theme-btn').forEach((btn) => {
            if (btn.classList.contains('light-mode')) {
                btn.classList.toggle('active', !isNightMode);
            }
            if (btn.classList.contains('dark-mode')) {
                btn.classList.toggle('active', isNightMode);
            }
        });
    }

    // الاستماع لتغيرات السمة من النظام الجديد
    window.addEventListener('themeChanged', function () {
        updateThemeButtons();
    });

    // أزرار تغيير المظهر القديمة - ربطها بالنظام الجديد
    document.querySelectorAll('.theme-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            if (window.themeManager) {
                window.themeManager.toggleTheme();
            }
        });
    });

    // التهيئة الأولية للأزرار
    updateThemeButtons();
});