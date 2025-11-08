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

// إدارة المظهر
const THEME_KEY = 'news-theme'

function applyTheme(theme) {
    const htmlElement = document.documentElement

    if (theme === 'light') {
        htmlElement.classList.add('light')
        document.querySelector('.light-mode')?.classList.add('active')
        document.querySelector('.dark-mode')?.classList.remove('active')
    } else {
        htmlElement.classList.remove('light')
        document.querySelector('.dark-mode')?.classList.add('active')
        document.querySelector('.light-mode')?.classList.remove('active')
    }

    // حفظ السمة في localStorage
    localStorage.setItem(THEME_KEY, theme)
}

// تهيئة المظهر
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY)

    if (savedTheme) {
        applyTheme(savedTheme)
        return
    }

    // إذا لم توجد تفضيلات محفوظة، نستخدم تفضيلات النظام
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    applyTheme(prefersDark ? 'dark' : 'light')
}

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function () {
    initTheme()

    // أزرار تغيير المظهر
    document.querySelectorAll('.theme-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const theme = btn.classList.contains('dark-mode') ? 'dark' : 'light'
            applyTheme(theme)
        })
    })

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
})

// تهيئة AOS
document.addEventListener('DOMContentLoaded', function () {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        })
    }
})