import { createI18n } from 'vue-i18n'
import ar from './locales/ar.json'
import en from './locales/en.json'

const i18n = createI18n({
  legacy: false,          // تفعيل الـ Composition API الحديثة لـ Vue 3
  locale: 'ar',           // اللغة الافتراضية عند فتح الموقع (العربية)
  fallbackLocale: 'en',   // اللغة البديلة في حال نسيان ترجمة كلمة معينة
  messages: {
    ar,
    en
  }
})

export default i18n