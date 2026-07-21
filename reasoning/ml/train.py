import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def create_target_labels(df):
    # شروط أكثر صرامة للخطر الحقيقي
    critical_spo2 = df['oxygen_saturation_min'] < 85.0
    critical_hr = (df['heart_rate_max'] > 130) | (df['heart_rate_min'] < 45)
    critical_bp = (df['blood_pressure_systolic_max'] > 180) | (df['blood_pressure_diastolic_min'] < 50)
    critical_rr = (df['respiratory_rate_max'] > 35) | (df['respiratory_rate_mean'] < 8)
    critical_temp = (df['body_temperature_max'] > 39.5) | (df['body_temperature_mean'] < 35.0)
    
    # خطر مزمن حقيقي: وجود مرض قلب + علامات حيوية سيئة للغاية
    chronic_risk = (df['has_heart_disease'] == 1) & (df['heart_rate_mean'] > 100)

    is_high_risk = critical_spo2 | critical_hr | critical_bp | critical_rr | critical_temp | chronic_risk
    return is_high_risk.astype(int)

def train_and_save_model():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATASET_PATH = os.path.join(BASE_DIR, 'reasoning', 'ml', 'mimic_ml_dataset.csv')

    print("📖 تحميل داتاسيت MIMIC المجهزة...")
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"الملف غير موجود: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    # 1. إنشاء العمود المستهدف (Target)
    df['is_high_risk'] = create_target_labels(df)

    # 2. تصفية الأعمدة الرقمية فقط
    ignore_cols = ['stay_id', 'subject_id', 'is_high_risk']
    feature_cols = [col for col in df.columns if col not in ignore_cols]

    # 🟢 حماية إضافية: إبقاء الأعمدة الرقمية فقط
    X_df = df[feature_cols].select_dtypes(include=[np.number])
    X = X_df.fillna(X_df.mean())
    y = df['is_high_risk']

    feature_cols = X.columns.tolist()

    print(f"📊 إجمالي الحالات للتدريب: {len(X)}")
    print(f"⚠️ عدد الحالات المصنفة كخطر: {y.sum()} من أصل {len(y)} ({y.mean()*100:.1f}%)")

    # 3. تقسيم البيانات
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. التدريب
    print("🌲 تدريب نموذج Random Forest...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # 5. التقييم
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("\n📈 نتائج تقييم النموذج:")
    print(f" - Accuracy:  {accuracy:.2f}")
    print(f" - Precision: {precision:.2f}")
    print(f" - Recall:    {recall:.2f}")
    print(f" - F1-score:  {f1:.2f}")
    print(" - Confusion Matrix:\n", cm)

    # 6. الحفظ
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'random_forest.pkl')

    with open(model_path, 'wb') as f:
        pickle.dump({'model': model, 'feature_names': feature_cols}, f)

    print(f"\n✅ تم حفظ النموذج المحدث بنجاح في: {model_path}")
    return model, feature_cols, accuracy, precision, recall, f1

if __name__ == "__main__":
    train_and_save_model()