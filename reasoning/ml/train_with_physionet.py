import os, sys, django, pickle, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("⏳ [1/3] تحميل وتحضير بيانات PhysioNet...")
DATA_PATH = "physionet_cleaned.csv"
if not os.path.exists(DATA_PATH):
    print("❌ ملف البيانات غير موجود.")
    exit(1)

df = pd.read_csv(DATA_PATH)

# بناء الذاكرة الزمنية
df = df.sort_values(by=['Patient_ID', 'Hour'])
for col in ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp']:
    if col in df.columns:
        df[f'{col}_past_hour'] = df.groupby('Patient_ID')[col].shift(1)
        df[f'{col}_change'] = df[col] - df[f'{col}_past_hour']

# ✅ سنستخدم الميزات الـ 15 الأساسية التي يستخدمها Gemini
features = [
    'HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'Age', 'Gender',
    'HR_past_hour', 'HR_change', 'O2Sat_past_hour', 'O2Sat_change', 'Temp_past_hour', 'Temp_change'
]
# نضيف فقط الأعمدة الموجودة فعلاً في الملف
features = [f for f in features if f in df.columns]

target = 'SepsisLabel'
df = df[features + [target]].dropna()

X = df[features]
y = df[target]

print("⚖️ [2/3] تدريب النموذج...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_probs >= 0.3).astype(int)

print("\n📊 تقرير الأداء:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("💾 [3/3] حفظ النموذج...")
model_dir = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'random_forest.pkl')
with open(model_path, 'wb') as f:
    pickle.dump({'model': model, 'feature_names': list(X.columns)}, f)

print(f"\n✅ تم حفظ النموذج في: {model_path}")