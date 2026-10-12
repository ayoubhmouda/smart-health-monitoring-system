<!-- MedicalHistory.vue -->
<template>
  <div class="w-full min-h-screen bg-[#F0F6F5] text-slate-600 font-sans antialiased p-6 flex flex-col gap-6" dir="rtl" @click="activeMenuRuleId = null">
    
    <!-- 🟢 الترويسة العلوية باللون التركوازي الغامق الموحد لهوية نظام MediWatch -->
    <header class="w-full rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-b from-[#0a3d48] via-[#0e4f5e] to-[#08323c] text-white select-none shrink-0">
      <div class="flex items-center gap-3.5">
        <!-- أيقونة الملف الطبي حرة ومباشرة بدون أي إطار أو خلفية -->
        <Icon icon="solar:document-text-bold" class="w-8 h-8 text-teal-300 shrink-0" />
        
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs text-teal-300 font-mono font-extrabold uppercase tracking-wider">سجل الملف الطبي</span>
            <span 
              class="text-[10px] px-2.5 py-0.5 rounded-full font-bold border"
              :class="canEdit ? 'bg-white/10 text-teal-200 border-white/5' : 'bg-amber-500/20 text-amber-200 border-amber-400/20'"
            >
              {{ canEdit ? 'صلاحيات الطبيب المعالج' : 'صلاحيات القراءة والمتابعة فقط' }}
            </span>
          </div>
          <h1 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">إدارة الملف الطبي للمريض: {{ patientName }}</h1>
          <p class="text-xs text-teal-200/70 mt-1 font-medium">
            {{ canEdit ? 'تحديث البيانات التاريخ المرضي، إدارة مقدمي الرعاية، والتحكم بالقواعد السريرية الخاصة' : 'استعراض البيانات الديموغرافية، السجل المرضي المزمن، وكادر الرعاية والقواعد المعتمدة للحالة' }}
          </p>
        </div>
      </div>

      <!-- أزرار الرجوع وحفظ التغييرات الشاملة -->
      <div class="flex items-center gap-2.5 w-full sm:w-auto justify-end select-none">
        <button 
          @click="router.push('/dashboard')" 
          class="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 font-bold text-xs backdrop-blur-sm transition-all cursor-pointer"
        >
          لوحة المراقبة
        </button>
        <button 
          v-if="canEdit"
          @click="saveAllChanges" 
          class="bg-teal-500/20 hover:bg-teal-500/30 text-teal-200 border border-teal-400/20 font-bold text-xs px-6 py-2.5 rounded-xl backdrop-blur-sm transition-all shadow-lg shadow-teal-900/10 cursor-pointer"
        >
          حفظ التغييرات السريرية
        </button>
      </div>
    </header>

    <!-- الهيكل المنظم للملف الطبي -->
    <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start w-full">
      
      <!-- العمود الأيمن: السوابق الطبية وإدارة كادر مقدمي الرعاية -->
      <div class="lg:col-span-5 flex flex-col gap-6">
        
        <!-- 🟢 1. البيانات الديموغرافية الأساسية للمريض -->
        <div class="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">1</span>
              <span class="font-extrabold text-white text-xs">البيانات الأساسية للمريض</span>
            </div>
            <!-- أيقونة حرة بدون إطار -->
            <Icon icon="solar:user-bold" class="w-5 h-5 text-white/90 shrink-0" />
          </div>

          <div class="p-6 space-y-3.5 text-xs">
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">الاسم الكامل للمريض <span v-if="canEdit" class="text-rose-500">*</span></label>
              <input 
                v-model="patientForm.full_name" 
                type="text" 
                :disabled="!canEdit"
                :readonly="!canEdit"
                required 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 disabled:opacity-75 disabled:cursor-not-allowed" 
              />
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5">تاريخ الميلاد <span v-if="canEdit" class="text-rose-500">*</span></label>
              <input 
                v-model="patientForm.date_of_birth" 
                type="date" 
                :disabled="!canEdit"
                :readonly="!canEdit"
                required 
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 disabled:opacity-75 disabled:cursor-not-allowed" 
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5">الجنس <span v-if="canEdit" class="text-rose-500">*</span></label>
                <select 
                  v-model="patientForm.gender" 
                  :disabled="!canEdit"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 outline-none font-bold text-slate-900 disabled:opacity-75 disabled:cursor-not-allowed"
                >
                  <option value="M">ذكر (Male)</option>
                  <option value="F">أنثى (Female)</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5">تصنيف الحالة</label>
                <select 
                  v-model="patientForm.element_type" 
                  :disabled="!canEdit"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 outline-none font-bold text-slate-900 disabled:opacity-75 disabled:cursor-not-allowed"
                >
                  <option value="patient">مريض (Patient)</option>
                  <option value="elderly">مسن رعاية (Elderly)</option>
                  <option value="disabled">احتياجات خاصة (Disabled)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 🟢 2. بطاقة السوابق الطبية والأمراض المزمنة -->
        <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">2</span>
              <span class="font-extrabold text-white text-xs">التاريخ الطبي والمزمن الفعلي للمريض</span>
            </div>
            <!-- أيقونة حرة بدون إطار -->
            <Icon icon="solar:notes-bold" class="w-5 h-5 text-white/90 shrink-0" />
          </div>

          <div class="p-6 space-y-3">
            <label 
              class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl transition-colors"
              :class="canEdit ? 'cursor-pointer hover:bg-slate-50' : 'cursor-default'"
            >
              <input 
                type="checkbox" 
                v-model="medicalHistoryFlags.heart_disease" 
                :disabled="!canEdit"
                class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 disabled:opacity-75"
                :class="canEdit ? 'cursor-pointer' : 'cursor-default'"
              />
              <div>
                <p class="text-sm font-bold text-slate-750">التاريخ المرضي لأمراض القلب (Heart Disease)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">قصور القلب، احتشاء عضلة القلب، أو الذبحة الصدرية السابقة</p>
              </div>
            </label>

            <label 
              class="flex items-start gap-3 bg-slate-50/50 p-4 border border-slate-200 rounded-2xl transition-colors"
              :class="canEdit ? 'cursor-pointer hover:bg-slate-50' : 'cursor-default'"
            >
              <input 
                type="checkbox" 
                v-model="medicalHistoryFlags.chronic_conditions" 
                :disabled="!canEdit"
                class="rounded text-teal-600 focus:ring-teal-500/50 w-4 h-4 mt-0.5 disabled:opacity-75"
                :class="canEdit ? 'cursor-pointer' : 'cursor-default'"
              />
              <div>
                <p class="text-xs font-bold text-slate-750">الإصابة بأمراض مزمنة عامة (Chronic Conditions)</p>
                <p class="text-[10px] text-slate-400 mt-0.5 font-medium">داء السكري (Type 2 Diabetes)، أو ارتفاع ضغط الدم (Hypertension)</p>
              </div>
            </label>
          </div>
        </div>

        <!-- 🟢 3. بطاقة إدارة الكادر لمقدمي الرعاية -->
        <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-white/10 text-teal-300 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">3</span>
              <span class="font-extrabold text-white text-xs">مقدمو الرعاية المتابعون للحالة</span>
            </div>
            <div class="flex items-center gap-3 select-none">
              <button 
                v-if="canEdit"
                @click="openAssignCaregiverModal" 
                class="text-[9px] font-bold text-teal-200 bg-white/10 hover:bg-white/20 border border-white/10 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
              >
                + إسناد مقدم رعاية
              </button>
              <!-- أيقونة حرة بدون إطار -->
              <Icon icon="solar:users-group-rounded-bold" class="w-5 h-5 text-white/90 shrink-0" />
            </div>
          </div>

          <div class="p-6 space-y-4">
            <div v-if="loadingCaregivers" class="text-center py-6 text-xs text-slate-400 font-bold animate-pulse">
              جاري تحميل كادر مقدمي الرعاية...
            </div>

            <div v-else-if="assignedCaregivers.length === 0" class="text-center py-6 text-xs text-slate-400 font-bold border border-dashed border-slate-200 rounded-2xl select-none">
              لا يوجد مقدمو رعاية مسندون لمتابعة هذا المريض حالياً.
            </div>

            <!-- جدول السجلات لمقدمي الرعاية المتابعين -->
            <div v-else class="w-full overflow-hidden border border-slate-200 rounded-2xl select-none">
              <table class="w-full text-right border-collapse text-[11px]">
                <thead class="bg-slate-50 border-b border-slate-200">
                  <tr class="text-slate-500 font-bold">
                    <th class="p-2.5 pr-4">الاسم</th>
                    <th class="p-2.5">اسم المستخدم</th> 
                    <th class="p-2.5">رقم الهاتف</th>
                    <th v-if="canEdit" class="p-2.5 text-left pl-4">الإجراءات</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="care in assignedCaregivers" :key="care.id" class="hover:bg-slate-50/50">
                    <td class="p-2.5 pr-4 font-bold text-slate-800">{{ care.full_name }}</td>
                    <td class="p-2.5 font-mono text-slate-500 font-bold">@{{ care.username }}</td> 
                    <td class="p-2.5 font-mono text-slate-600 font-bold">{{ care.phone_number || 'غير مضاف' }}</td>
                    <td v-if="canEdit" class="p-2.5 text-left pl-4">
                      <div class="flex items-center justify-end gap-1.5">
                        <button @click="openEditCaregiverModal(care)" class="text-[9px] font-bold text-sky-700 bg-sky-50 border border-sky-100 px-2.5 py-1 rounded-lg cursor-pointer">تعديل</button>
                        <button @click="removeCaregiver(care.id)" class="text-[9px] font-bold text-rose-600 bg-rose-50 border border-rose-100 px-2.5 py-1 rounded-lg cursor-pointer">حذف</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- العمود الأيسر: 4. القواعد والبروتوكولات السريرية الخاصة بالمريض -->
      <div class="lg:col-span-7 bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col overflow-visible">
        <div class="bg-[#0a3d48] text-white p-4.5 rounded-t-3xl flex items-center justify-between gap-3 select-none">
          <div class="flex items-center gap-2">
            <span class="w-5 h-5 bg-white/10 text-teal-300 font-bold rounded-lg flex items-center justify-center text-[10px] font-mono">4</span>
            <span class="font-extrabold text-white text-xs">البروتوكولات السريرية الخاصة بالمريض</span>
          </div>
          <!-- زر باني القواعد وأيقونة حرة بدون إطار -->
          <div class="flex items-center gap-3 select-none">
            <button 
              v-if="canEdit"
              @click="router.push(`/patients/${patientId}/rules/new`)" 
              class="text-[9px] font-bold text-teal-200 bg-white/10 hover:bg-white/20 border border-white/10 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              + إضافة قاعدة
            </button>
            <Icon icon="solar:tuning-2-bold" class="w-5 h-5 text-white/90 shrink-0" />
          </div>
        </div>

        <div class="p-6 flex-1 flex flex-col gap-4 overflow-visible">
          <div v-if="loadingRules" class="text-center py-6 text-xs text-slate-400 font-bold animate-pulse">
            جاري جلب القواعد المخصصة للمريض...
          </div>

          <div v-else-if="customRules.length === 0" class="text-center py-12 text-xs text-slate-400 font-bold border border-dashed border-slate-200 rounded-3xl select-none">
            لا توجد قواعد مخصصة مضافة لهذا المريض حالياً، يطبق النظام البروتوكولات العامة للمستشفى فقط.
          </div>

          <div v-else class="space-y-3 overflow-visible">
            <!-- 🟢 الكرت بالكامل قابل للنقر لفتح صفحة تعديل القاعدة فوراً -->
            <div 
              v-for="rule in customRules" 
              :key="rule.id" 
              @click="canEdit ? router.push(`/patients/${patientId}/rules/edit/${rule.id}`) : null"
              class="p-4 bg-slate-50/50 hover:bg-slate-100/80 border border-slate-200 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 relative overflow-visible transition-all duration-200 select-none group/rule"
              :class="canEdit ? 'cursor-pointer' : 'cursor-default'"
            >
              <!-- تفاصيل القاعدة -->
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2 mb-1.5">
                  <span 
                    class="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border font-mono"
                    :class="rule.severity === 'critical' ? 'bg-rose-50 text-rose-700 border-rose-200' : (rule.severity === 'high' ? 'bg-orange-50 text-orange-700 border-orange-200' : 'bg-yellow-50 text-yellow-700 border-yellow-200')"
                  >
                    {{ rule.severity }}
                  </span>
                  <h4 class="font-extrabold text-slate-800 text-xs truncate group-hover/rule:text-teal-700 transition-colors">
                    {{ rule.name }}
                  </h4>
                </div>
                <p class="text-[10px] text-slate-400 font-semibold leading-relaxed truncate">التوصية: {{ rule.action_template }}</p>
              </div>

              <!-- 🟢 مجموعة التحكم المعزولة (@click.stop) -->
              <div class="flex items-center gap-2 flex-shrink-0 select-none" @click.stop>
                
                <!-- 1. زر التفعيل المنزلق -->
                <button 
                  type="button"
                  :disabled="!canEdit"
                  @click.stop="toggleRuleStatus(rule)" 
                  class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="rule.is_active ? 'bg-emerald-500' : 'bg-slate-300'"
                  :title="canEdit ? (rule.is_active ? 'تعطيل القاعدة' : 'تفعيل القاعدة') : 'للقراءة فقط'"
                >
                  <span 
                    class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out"
                    :class="rule.is_active ? 'translate-x-0' : '-translate-x-4'" 
                  ></span>
                </button>

                <!-- 2. زر النقاط الثلاث بدون أي إطار أو خلفية -->
                <div v-if="canEdit" class="relative" @click.stop>
                  <button 
                    @click.stop="activeMenuRuleId = activeMenuRuleId === rule.id ? null : rule.id"
                    class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 rounded-lg flex items-center justify-center transition-colors cursor-pointer"
                    title="خيارات"
                  >
                    <Icon icon="solar:menu-dots-bold" class="w-4 h-4" />
                  </button>

                  <!-- القائمة المنسدلة: نصوص صافية وبطبقة z-50 كاملة الوضوح -->
                  <div 
                    v-if="activeMenuRuleId === rule.id"
                    class="absolute left-0 top-full mt-1 w-24 bg-white rounded-xl border border-slate-200 shadow-xl py-1 z-50 flex flex-col text-xs font-bold animate-[fadeIn_0.15s_ease-out]"
                  >
                    <button 
                      @click.stop="router.push(`/patients/${patientId}/rules/edit/${rule.id}`)"
                      class="w-full text-center py-2 px-3 hover:bg-slate-50 text-slate-700 transition-colors cursor-pointer"
                    >
                      تعديل
                    </button>
                    <button 
                      @click.stop="deleteCustomRule(rule.id); activeMenuRuleId = null"
                      class="w-full text-center py-2 px-3 hover:bg-rose-50 text-rose-600 transition-colors cursor-pointer border-t border-slate-100"
                    >
                      حذف
                    </button>
                  </div>
                </div>

              </div>

            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- منبثقة إسناد أو إنشاء حساب مقدم رعاية معتمد -->
    <div v-if="showAssignModal && canEdit" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-55 flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl border border-slate-200 shadow-xl w-full max-w-md p-6 space-y-4" dir="rtl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-sm font-extrabold text-slate-800">إسناد أو إنشاء حساب مقدم رعاية للمريض</h3>
          <button @click="showAssignModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl cursor-pointer">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-600 mb-1.5">خيارات مقدم الرعاية</label>
            <select v-model="caregiverForm.option" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900 cursor-pointer">
              <option value="existing">اختيار مقدم رعاية مسجّل مسبقاً</option>
              <option value="new">إنشاء حساب جديد كلياً لمقدم الرعاية</option>
            </select>
          </div>

          <div v-if="caregiverForm.option === 'existing'" class="space-y-2">
            <label class="block font-bold text-slate-600 mb-1">اختر مقدم الرعاية من القائمة</label>
            <select v-model="caregiverForm.existing_id" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900 cursor-pointer">
              <option v-for="care in allCaregivers" :key="care.id" :value="care.id">
                {{ care.full_name }} (@{{ care.username }})
              </option>
            </select>
          </div>

          <div v-if="caregiverForm.option === 'new'" class="space-y-3 p-3 bg-slate-50 rounded-2xl border border-slate-100">
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">الاسم الكامل لمقدم الرعاية</label>
              <input v-model="caregiverForm.full_name" type="text" required class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">اسم المستخدم (Username)</label>
              <input v-model="caregiverForm.username" type="text" required class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold font-mono text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">رقم هاتف مقدم الرعاية</label>
              <input v-model="caregiverForm.phone_number" type="text" placeholder="+218900000000" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold font-mono text-slate-900" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 mb-1">كلمة المرور</label>
              <input v-model="caregiverForm.password" type="password" required placeholder="••••••••" class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 outline-none font-bold text-slate-900" />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="showAssignModal = false" class="px-4 py-2 rounded-xl text-slate-500 font-bold hover:bg-slate-100 cursor-pointer">إلغاء</button>
            <button @click="submitAssignCaregiver" class="bg-teal-600 hover:bg-teal-700 text-white font-bold px-5 py-2 rounded-xl shadow-xs cursor-pointer">حفظ وإسناد مقدم الرعاية</button>
          </div>
        </div>
      </div>
    </div>

    <!-- منبثقة تعديل بيانات مقدم الرعاية -->
    <div v-if="showEditCaregiverModal && canEdit" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-55 flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl border border-slate-200 shadow-xl w-full max-w-md p-6 space-y-4" dir="rtl">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="text-sm font-extrabold text-slate-800">تعديل بيانات حساب مقدم الرعاية</h3>
          <button @click="showEditCaregiverModal = false" class="text-slate-400 hover:text-slate-600 font-bold text-xl cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="submitEditCaregiver" class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-600 mb-1">الاسم الكامل لمقدم الرعاية</label>
            <input v-model="editCaregiverForm.full_name" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900" />
          </div>
          <div>
            <label class="block font-bold text-slate-600 mb-1">اسم المستخدم (Username)</label>
            <input v-model="editCaregiverForm.username" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono" />
          </div>
          <div>
            <label class="block font-bold text-slate-600 mb-1">رقم الهاتف للتواصل والـ SMS</label>
            <input v-model="editCaregiverForm.phone_number" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus:bg-white focus:border-teal-500 outline-none font-bold text-slate-900 font-mono" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="showEditCaregiverModal = false" class="px-4 py-2 rounded-xl text-slate-500 font-bold hover:bg-slate-100 cursor-pointer">إلغاء</button>
            <button type="submit" class="bg-sky-600 hover:bg-sky-700 text-white font-bold px-5 py-2 rounded-xl shadow-xs cursor-pointer">حفظ التعديلات</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import api from '../api'
import { useDoctorStore } from '../stores/doctor'

const router = useRouter()
const route = useRoute()
const doctorStore = useDoctorStore()

const patientId = ref(route.params.id)
const patientName = ref('المريض')
const patientData = ref({})
const loading = ref(true)
const loadingRules = ref(true)
const loadingCaregivers = ref(true)

const assignedCaregivers = ref([])
const allCaregivers = ref([])
const showAssignModal = ref(false)
const showEditCaregiverModal = ref(false)

// معرف القاعدة التي تم فتح قائمة خياراتها حالياً
const activeMenuRuleId = ref(null)

// الصلاحية الصارمة: الطبيب المعالج المسند للمريض فقط
const canEdit = computed(() => {
  if (!doctorStore.id) return false
  
  // استخراج معرف الطبيب المعالج المسند للمريض
  const patientDoctor = patientData.value?.doctor
  const patientDoctorId = (patientDoctor && typeof patientDoctor === 'object') ? patientDoctor.id : patientDoctor
  
  // إذا كان المريض جديداً وغير مسند لأحد بعد، يمكن للطبيب/المدير تعديله وإسناده
  if (!patientDoctorId) return true

  // الصلاحية تُمنح فقط إذا كان المستخدم المسجل هو نفسه الطبيب المشرف على الحالة
  return Number(patientDoctorId) === Number(doctorStore.id)
})

// استمارة بيانات المريض
const patientForm = ref({
  full_name: '',
  date_of_birth: '',
  gender: 'M',
  element_type: 'patient'
})

const caregiverForm = ref({
  option: 'existing',
  existing_id: null,
  full_name: '',
  username: '',
  phone_number: '',
  password: ''
})

const editCaregiverForm = ref({ id: null, full_name: '', username: '', phone_number: '' })
const customRules = ref([])

const medicalHistoryFlags = ref({
  heart_disease: false,
  chronic_conditions: false
})

const fetchPatientDetails = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/monitored-elements/${patientId.value}/`)
    patientData.value = res.data
    patientName.value = res.data.full_name

    patientForm.value = {
      full_name: res.data.full_name || '',
      date_of_birth: res.data.date_of_birth || '',
      gender: res.data.gender || 'M',
      element_type: res.data.element_type || 'patient'
    }

    const medRes = await api.get('/api/medical-histories/', {
      params: { monitored_element: patientId.value }
    })
    const history = medRes.data?.[0] || (medRes.data.results?.[0])
    
    if (history) {
      const conditions = history.chronic_conditions || []
      const condNames = conditions.map(c => {
        if (typeof c === 'string') return c.toLowerCase()
        if (c && typeof c === 'object') return (c.name || '').toLowerCase()
        return ''
      })
      
      medicalHistoryFlags.value = {
        heart_disease: condNames.includes('heart_disease'),
        chronic_conditions: condNames.includes('diabetes')
      }
    }
  } catch (e) {
    console.error('فشل استعادة السجل الطبي وتفاصيل المريض:', e)
  } finally {
    loading.value = false
  }
}

const fetchAssignedCaregivers = async () => {
  loadingCaregivers.value = true
  try {
    const res = await api.get('/api/caregivers/', {
      params: { monitored_element: patientId.value }
    })
    assignedCaregivers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) {
    console.error('فشل جلب مقدمي الرعاية المسندين:', e)
  } finally {
    loadingCaregivers.value = false
  }
}

const fetchAllCaregiversList = async () => {
  try {
    const res = await api.get('/api/caregivers/')
    allCaregivers.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (allCaregivers.value.length > 0) {
      caregiverForm.value.existing_id = allCaregivers.value[0].id
    }
  } catch (e) {
    console.error('فشل جلب قائمة كافة مقدمي الرعاية:', e)
  }
}

const fetchCustomRules = async () => {
  loadingRules.value = true
  try {
    const res = await api.get('/api/rules/', {
      params: { monitored_element: patientId.value }
    })
    const allRules = Array.isArray(res.data) ? res.data : (res.data.results || [])
    customRules.value = allRules.filter(r => r.monitored_element === Number(patientId.value))
  } catch (e) {
    console.error('فشل جلب القواعد المخصصة للمريض:', e)
  } finally {
    loadingRules.value = false
  }
}

// دالة التبديل المباشر لتفعيل/إيقاف القاعدة
const toggleRuleStatus = async (rule) => {
  if (!canEdit.value) return
  const prev = rule.is_active
  rule.is_active = !rule.is_active
  try {
    await api.patch(`/api/rules/${rule.id}/`, {
      is_active: rule.is_active
    })
  } catch (e) {
    rule.is_active = prev
    console.error('فشل تغيير حالة تفعيل البروتوكول:', e)
    alert('تعذر تغيير حالة تفعيل البروتوكول')
  }
}

const openAssignCaregiverModal = async () => {
  if (!canEdit.value) return
  caregiverForm.value = { option: 'existing', existing_id: null, full_name: '', username: '', phone_number: '', password: '' }
  await fetchAllCaregiversList()
  showAssignModal.value = true
}

const submitAssignCaregiver = async () => {
  if (!canEdit.value) return
  try {
    if (caregiverForm.value.option === 'new') {
      await api.post('/api/caregivers/', {
        username: caregiverForm.value.username,
        password: caregiverForm.value.password,
        full_name: caregiverForm.value.full_name,
        phone_number: caregiverForm.value.phone_number,
        monitored_element: patientId.value
      })
    } else {
      const currentIds = assignedCaregivers.value.map(c => c.id)
      const newId = caregiverForm.value.existing_id
      
      if (newId && !currentIds.includes(newId)) {
        currentIds.push(newId)
      }

      await api.patch(`/api/monitored-elements/${patientId.value}/`, {
        caregivers: currentIds
      })
    }

    showAssignModal.value = false
    alert('تم إسناد وربط مقدم الرعاية للحالة بنجاح!')
    await fetchPatientDetails()
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل إسناد مقدم الرعاية:', e)
    alert('تعذر إتمام العملية، يرجى التأكد من البيانات المدخلة')
  }
}

const openEditCaregiverModal = (care) => {
  if (!canEdit.value) return
  editCaregiverForm.value = {
    id: care.id,
    full_name: care.full_name || '',
    username: care.username || '',
    phone_number: care.phone_number || ''
  }
  showEditCaregiverModal.value = true
}

const submitEditCaregiver = async () => {
  if (!canEdit.value) return
  try {
    await api.patch(`/api/caregivers/${editCaregiverForm.value.id}/`, {
      full_name: editCaregiverForm.value.full_name,
      username: editCaregiverForm.value.username,
      phone_number: editCaregiverForm.value.phone_number
    })
    showEditCaregiverModal.value = false
    alert('تم تحديث بيانات حساب مقدم الرعاية بنجاح!')
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل تعديل بيانات مقدم الرعاية:', e)
  }
}

const removeCaregiver = async (caregiverId) => {
  if (!canEdit.value) return
  if (!confirm('هل أنت متأكد من فك ارتباط وإلغاء إسناد مقدم الرعاية عن المريض؟')) return
  try {
    const remainingIds = assignedCaregivers.value
      .map(c => c.id)
      .filter(id => id !== caregiverId)

    await api.patch(`/api/monitored-elements/${patientId.value}/`, {
      caregivers: remainingIds
    })

    alert('تم إلغاء إسناد وفك ارتباط مقدم الرعاية عن المريض.')
    await fetchPatientDetails()
    await fetchAssignedCaregivers()
  } catch (e) {
    console.error('فشل إلغاء إسناد مقدم الرعاية:', e)
  }
}

const deleteCustomRule = async (id) => {
  if (!canEdit.value) return
  if (!confirm('هل أنت متأكد من رغبتك في حذف هذا البروتوكول المخصص للمريض؟')) return
  try {
    await api.delete(`/api/rules/${id}/`)
    fetchCustomRules()
  } catch (e) {
    console.error('فشل حذف القاعدة المخصصة:', e)
  }
}

const saveAllChanges = async () => {
  if (!canEdit.value) {
    alert('غير مصرح لك بتعديل هذا الملف الطبي.')
    return
  }
  try {
    await api.patch(`/api/monitored-elements/${patientId.value}/`, {
      full_name: patientForm.value.full_name,
      date_of_birth: patientForm.value.date_of_birth,
      gender: patientForm.value.gender,
      element_type: patientForm.value.element_type
    })

    const chronic_conditions = []
    if (medicalHistoryFlags.value.heart_disease) {
      chronic_conditions.push({ name: 'heart_disease' })
    }
    if (medicalHistoryFlags.value.chronic_conditions) {
      chronic_conditions.push({ name: 'diabetes' })
    }

    const medRes = await api.get('/api/medical-histories/', {
      params: { monitored_element: patientId.value }
    })
    const history = medRes.data?.[0] || (medRes.data.results?.[0])

    if (history) {
      await api.patch(`/api/medical-histories/${history.id}/`, {
        chronic_conditions: chronic_conditions
      })
    }

    alert('تم تحديث وحفظ السجل الشخصي والفسيولوجي المكتمل للمريض بنجاح!')
    fetchPatientDetails()
  } catch (e) {
    console.error('فشل حفظ التعديلات الطبية الشاملة:', e)
    alert('تعذر حفظ التعديلات، يرجى مراجعة البيانات')
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    patientId.value = newId
    patientName.value = 'المريض'
    patientData.value = {}
    patientForm.value = { full_name: '', date_of_birth: '', gender: 'M', element_type: 'patient' }
    assignedCaregivers.value = []
    customRules.value = []
    
    fetchPatientDetails()
    fetchAssignedCaregivers()
    fetchCustomRules()
  }
}, { immediate: true })

onMounted(async () => {
  if (!doctorStore.id) {
    await doctorStore.fetchProfile()
  }
  fetchPatientDetails()
  fetchAssignedCaregivers()
  fetchCustomRules()
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #0d9488;
}
</style>