// نظام إدارة السمات المتقدم - الوضع الليلي والنهاري
class AdvancedThemeManager {
  constructor() {
    this.themeKey = 'app-theme';
    this.settingsKey = 'theme-settings';
    this.currentTheme = this.getSavedTheme() || this.getSystemPreference();
    this.settings = this.getSavedSettings() || {};
    this.autoMode = this.settings.autoMode !== false; // true by default

    this.init();
  }

  // تهيئة النظام
  init() {
    this.applyTheme(this.currentTheme);
    this.applySettings(this.settings);
    this.addThemeToggleButton();
    this.addControlPanel();
    this.listenForSystemChanges();
    this.setupThemeDetection();

    console.log('✅ نظام السمات المتقدم يعمل بنجاح');
  }

  // الحصول على تفضيلات النظام
  getSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'night';
    }
    return 'day';
  }

  // الاستماع لتغيرات النظام
  listenForSystemChanges() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

      const handleSystemChange = (e) => {
        if (this.autoMode) {
          this.applyTheme(e.matches ? 'night' : 'day');
          this.updateUI();
        }
      };

      // دعم المتصفحات القديمة والجديدة
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemChange);
      } else if (mediaQuery.addListener) {
        mediaQuery.addListener(handleSystemChange);
      }
    }
  }

  // إعداد كشف السمة للعناصر
  setupThemeDetection() {
    // مراقبة العناصر المضافَة ديناميكياً
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
          this.applyThemeToElements(mutation.addedNodes);
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  // تطبيق السمة على عناصر محددة
  applyThemeToElements(elements) {
    elements.forEach(element => {
      if (element.nodeType === 1) { // عناصر DOM فقط
        if (element.hasAttribute('data-theme-aware')) {
          this.themeAwareElement(element);
        }
      }
    });
  }

  // معالجة العناصر الواعية للسمة
  themeAwareElement(element) {
    const themeType = element.getAttribute('data-theme-type') || 'bg';
    const dayValue = element.getAttribute('data-day-value');
    const nightValue = element.getAttribute('data-night-value');

    if (dayValue && nightValue) {
      if (this.currentTheme === 'day') {
        element.style[themeType] = dayValue;
      } else {
        element.style[themeType] = nightValue;
      }
    }
  }

  // الحصول على السمة المحفوظة
  getSavedTheme() {
    return localStorage.getItem(this.themeKey);
  }

  // الحصول على الإعدادات المحفوظة
  getSavedSettings() {
    try {
      return JSON.parse(localStorage.getItem(this.settingsKey)) || {};
    } catch (e) {
      return {};
    }
  }

  // حفظ السمة
  saveTheme(theme) {
    localStorage.setItem(this.themeKey, theme);
  }

  // حفظ الإعدادات
  saveSettings(settings) {
    try {
      localStorage.setItem(this.settingsKey, JSON.stringify(settings));
    } catch (e) {
      console.error('Failed to save theme settings:', e);
    }
  }

  // تطبيق السمة
  applyTheme(theme) {
    this.currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);

    // حفظ التفضيل فقط إذا كان الوضع التلقائي معطلاً
    if (!this.autoMode) {
      this.saveTheme(theme);
    }

    // تحديث واجهة المستخدم
    this.updateUI();

    // إطلاق event للسماح للآخرين بالاستجابة لتغير السمة
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: {
        theme: theme,
        settings: this.settings
      }
    }));

    // إشعار لتطبيقات أخرى
    this.showNotification(`  color ${theme === 'day' ? 'hight' : 'black'}`);
  }

  // تطبيق الإعدادات
  applySettings(settings) {
    this.settings = { ...this.settings, ...settings };
    this.autoMode = this.settings.autoMode !== false;

    // تطبيق إعدادات التعتيم
    if (this.settings.reduceBrightness) {
      document.documentElement.style.filter = 'brightness(0.9)';
    } else {
      document.documentElement.style.filter = '';
    }

    // تطبيق إعدادات التباين
    if (this.settings.highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }

    this.saveSettings(this.settings);
    this.updateControlPanel();
  }

  // تبديل السمة
  toggleTheme() {
    const newTheme = this.currentTheme === 'day' ? 'night' : 'day';
    // عند التبديل يدوياً، تعطيل الوضع التلقائي
    this.applySettings({ autoMode: false });
    this.applyTheme(newTheme);
  }

  // تفعيل الوضع التلقائي
  enableAutoMode() {
    this.applySettings({ autoMode: true });
    this.applyTheme(this.getSystemPreference());
  }

  // عرض الإشعارات
  showNotification(message, type = 'info') {
    // إنشاء عنصر الإشعار إذا لم يكن موجوداً
    if (!document.getElementById('theme-notification')) {
      const notification = document.createElement('div');
      notification.id = 'theme-notification';
      notification.style.position = 'fixed';
      notification.style.bottom = '20px';
      notification.style.left = '50%';
      notification.style.transform = 'translateX(-50%)';
      notification.style.padding = '12px 20px';
      notification.style.borderRadius = '8px';
      notification.style.zIndex = '10000';
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.3s ease';
      notification.style.maxWidth = '80%';
      document.body.appendChild(notification);
    }

    const notification = document.getElementById('theme-notification');
    notification.textContent = message;
    notification.style.background = type === 'error' ? 'var(--error)' :
                                  type === 'success' ? 'var(--ok)' : 'var(--brand)';
    notification.style.color = 'white';

    // عرض الإشعار
    notification.style.opacity = '1';

    // إخفاء الإشعار بعد 3 ثوان
    setTimeout(() => {
      notification.style.opacity = '0';
    }, 3000);
  }

  // إضافة زر تبديل السمة
  addThemeToggleButton() {
    if (!document.getElementById('theme-toggle')) {
      const button = document.createElement('button');
      button.id = 'theme-toggle';
      button.className = 'theme-toggle-btn';
      button.innerHTML = this.currentTheme === 'day' ? '🌙' : '☀️';
      button.title = this.currentTheme === 'day' ? 'الوضع الليلي' : 'الوضع النهاري';

      button.addEventListener('click', () => this.toggleTheme());

      document.body.appendChild(button);
    }

    this.updateThemeButtons();
  }

  // إضافة لوحة التحكم
  addControlPanel() {
    if (!document.getElementById('theme-control-panel')) {
      const panel = document.createElement('div');
      panel.id = 'theme-control-panel';
      panel.className = 'theme-control-panel';
      panel.innerHTML = `
        <div class="theme-panel-toggle">🎨</div>
        <h4>إعدادات المظهر</h4>

        <div class="theme-option">
          <label>الوضع التلقائي</label>
          <input type="checkbox" id="theme-auto-mode" ${this.autoMode ? 'checked' : ''}>
          <span class="auto-theme-indicator"></span>
        </div>

        <div class="theme-option">
          <label>السمة:</label>
          <div>
            <span class="theme-preset ${this.currentTheme === 'day' ? 'active' : ''}" data-theme="day">نهاري</span>
            <span class="theme-preset ${this.currentTheme === 'night' ? 'active' : ''}" data-theme="night">ليلي</span>
          </div>
        </div>

        <div class="theme-option">
          <label>خيارات إضافية:</label>
          <div>
            <input type="checkbox" id="theme-reduce-brightness" ${this.settings.reduceBrightness ? 'checked' : ''}>
            <label for="theme-reduce-brightness">تقليل السطوع</label>
          </div>
          <div>
            <input type="checkbox" id="theme-high-contrast" ${this.settings.highContrast ? 'checked' : ''}>
            <label for="theme-high-contrast">تباين عالي</label>
          </div>
        </div>

        <div class="theme-option">
          <button id="theme-export-btn">تصدير الإعدادات</button>
          <button id="theme-import-btn">استيراد الإعدادات</button>
          <input type="file" id="theme-import-file" accept=".json" style="display: none;">
        </div>
      `;

      document.body.appendChild(panel);

      // إضافة event listeners
      document.getElementById('theme-auto-mode').addEventListener('change', (e) => {
        this.applySettings({ autoMode: e.target.checked });
        if (e.target.checked) {
          this.applyTheme(this.getSystemPreference());
        }
      });

      document.querySelectorAll('.theme-preset').forEach(preset => {
        preset.addEventListener('click', () => {
          this.applySettings({ autoMode: false });
          this.applyTheme(preset.dataset.theme);
        });
      });

      document.getElementById('theme-reduce-brightness').addEventListener('change', (e) => {
        this.applySettings({ reduceBrightness: e.target.checked });
      });

      document.getElementById('theme-high-contrast').addEventListener('change', (e) => {
        this.applySettings({ highContrast: e.target.checked });
      });

      document.getElementById('theme-export-btn').addEventListener('click', () => {
        this.exportSettings();
      });

      document.getElementById('theme-import-btn').addEventListener('click', () => {
        document.getElementById('theme-import-file').click();
      });

      document.getElementById('theme-import-file').addEventListener('change', (e) => {
        this.importSettings(e.target.files[0]);
      });

      // toggle panel
      document.querySelector('.theme-panel-toggle').addEventListener('click', () => {
        panel.classList.toggle('open');
      });
    }

    this.updateControlPanel();
  }

  // تصدير الإعدادات
  exportSettings() {
    const settings = {
      theme: this.currentTheme,
      settings: this.settings,
      exportDate: new Date().toISOString()
    };

    const dataStr = JSON.stringify(settings, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `theme-settings-${new Date().getTime()}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();

    this.showNotification('تم تصدير الإعدادات بنجاح', 'success');
  }

  // استيراد الإعدادات
  importSettings(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const settings = JSON.parse(e.target.result);

        if (settings.theme) {
          this.applyTheme(settings.theme);
        }

        if (settings.settings) {
          this.applySettings(settings.settings);
        }

        this.showNotification('تم استيراد الإعدادات بنجاح', 'success');
      } catch (error) {
        this.showNotification('فشل في استيراد الإعدادات', 'error');
        console.error('Failed to import settings:', error);
      }
    };

    reader.readAsText(file);
  }

  // تحديث واجهة المستخدم
  updateUI() {
    this.updateThemeButtons();
    this.updateControlPanel();
  }

  // تحديث أزرار السمة
  updateThemeButtons() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
      toggleBtn.innerHTML = this.currentTheme === 'day' ? '🌙' : '☀️';
      toggleBtn.title = this.currentTheme === 'day' ? 'الوضع الليلي' : 'الوضع النهاري';
    }
  }

  // تحديث لوحة التحكم
  updateControlPanel() {
    const panel = document.getElementById('theme-control-panel');
    if (panel) {
      // تحديث الوضع التلقائي
      const autoModeCheckbox = document.getElementById('theme-auto-mode');
      if (autoModeCheckbox) {
        autoModeCheckbox.checked = this.autoMode;
      }

      // تحديث السمة المختارة
      document.querySelectorAll('.theme-preset').forEach(preset => {
        preset.classList.remove('active');
        if (preset.dataset.theme === this.currentTheme) {
          preset.classList.add('active');
        }
      });

      // تحديث الخيارات الإضافية
      const reduceBrightness = document.getElementById('theme-reduce-brightness');
      if (reduceBrightness) {
        reduceBrightness.checked = this.settings.reduceBrightness || false;
      }

      const highContrast = document.getElementById('theme-high-contrast');
      if (highContrast) {
        highContrast.checked = this.settings.highContrast || false;
      }

      // مؤشر الوضع التلقائي
      const indicator = document.querySelector('.auto-theme-indicator');
      if (indicator) {
        indicator.style.background = this.autoMode ? 'var(--ok)' : 'var(--muted)';
      }
    }
  }

  // الحصول على السمة الحالية
  getCurrentTheme() {
    return this.currentTheme;
  }

  // التحقق إذا كانت السمة ليلية
  isNightMode() {
    return this.currentTheme === 'night';
  }

  // التحقق إذا كانت السمة نهائية
  isDayMode() {
    return this.currentTheme === 'day';
  }

  // الحصول على الإعدادات الحالية
  getCurrentSettings() {
    return this.settings;
  }
}

// تهيئة مدير السمات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
  window.themeManager = new AdvancedThemeManager();

  // إضافة styles إضافية
  const style = document.createElement('style');
  style.textContent = `
    .high-contrast {
      --ink: #ffffff;
      --bg: #000000;
      --paper: #1a1a1a;
      --sep: #333333;
    }

    @media (prefers-reduced-motion: reduce) {
      .theme-transition * {
        transition: none !important;
      }
    }
  `;
  document.head.appendChild(style);
});

// جعل النظام متاحاً عالمياً
window.initThemeManager = function() {
  window.themeManager = new AdvancedThemeManager();
};

// API للاستخدام من قبل التطبيقات الأخرى
window.ThemeAPI = {
  getTheme: () => window.themeManager?.getCurrentTheme(),
  toggleTheme: () => window.themeManager?.toggleTheme(),
  setTheme: (theme) => window.themeManager?.applyTheme(theme),
  onThemeChange: (callback) => {
    window.addEventListener('themeChanged', (e) => callback(e.detail));
  },
  getSettings: () => window.themeManager?.getCurrentSettings(),
  updateSettings: (settings) => window.themeManager?.applySettings(settings)
};