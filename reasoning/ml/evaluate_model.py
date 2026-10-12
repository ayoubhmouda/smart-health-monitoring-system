# reasoning/ml/evaluate_model.py
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import (
    confusion_matrix, 
    classification_report, 
    roc_auc_score, 
    accuracy_score, 
    recall_score, 
    precision_score, 
    f1_score
)

# 1. تحديد المسارات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'mimic_ml_dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'random_forest.pkl')

print("⏳ جاري تحميل النموذج وقاعدة البيانات السريرية...")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"لم يتم العثور على النموذج في: {MODEL_PATH}")

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(f"لم يتم العثور على ملف الداتاسيت في: {DATASET_PATH}")

# 2. تحميل النموذج والميزات
with open(MODEL_PATH, 'rb') as f:
    saved_data = pickle.load(f)
    model = saved_data['model']
    feature_names = saved_data['feature_names']
    best_threshold = saved_data.get('best_threshold', 0.25)

# 3. تحميل وتجهيز البيانات
df = pd.read_csv(DATASET_PATH)

# تحديد الهدف المستهدف (Target)
target_col = 'hospital_expire_flag' if 'hospital_expire_flag' in df.columns else 'has_sepsis'
y_true = df[target_col].values

# مطابقة الميزات المطلوبة فقط
for col in feature_names:
    if col not in df.columns:
        df[col] = 0.0

X = df[feature_names]

# 4. التنبؤ وحساب الاحتماليات
y_proba = model.predict_proba(X)[:, 1]
# استخدام عتبة القرار المعتمدة في النظام (0.25)
y_pred_threshold = (y_proba >= best_threshold).astype(int)
y_pred_default = (y_proba >= 0.50).astype(int)

# 5. حساب مصفوفة الارتباك
cm = confusion_matrix(y_true, y_pred_threshold)
tn, fp, fn, tp = cm.ravel()

print("\n" + "="*60)
print("🩻 1. مصفوفة الارتباك (Confusion Matrix) عند العتبة السريرية (" + str(best_threshold) + ")")
print("="*60)
print(f"  [ الحالات المستقرة المشخصة صحيحة (True Negatives) ]: {tn}")
print(f"  [ إنذارات كاذبة لحالات سليمة (False Positives)   ]: {fp}")
print(f"  [ 🚨 حالات تدهور فاتها النظام (False Negatives)  ]: {fn}")
print(f"  [ 🟢 حالات تدهور تم كشفها بنجاح (True Positives)  ]: {tp}")

print("\n" + "="*60)
print("📊 2. المقاييس السريرية الدقيقة (Clinical Performance Metrics)")
print("="*60)
print(f"• الدقة الإجمالية (Accuracy)     : {accuracy_score(y_true, y_pred_threshold)*100:.2f}%")
print(f"• الحساسية/الاستدعاء (Recall/Sens) : {recall_score(y_true, y_pred_threshold)*100:.2f}% (قدرة النظام على صيد الخطر)")
print(f"• الدقة النوعية (Precision)       : {precision_score(y_true, y_pred_threshold)*100:.2f}%")
print(f"• مقياس F1-Score المتوازن         : {f1_score(y_true, y_pred_threshold):.3f}")
print(f"• المساحة تحت المنحنى (ROC-AUC)   : {roc_auc_score(y_true, y_proba):.3f}")

print("\n" + "="*60)
print("⭐ 3. أهم 10 ميزات سريرية يعتمد عليها الذكاء الاصطناعي (Top 10 Features)")
print("="*60)
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
for i in range(min(10, len(feature_names))):
    idx = indices[i]
    print(f" {i+1:2d}. {feature_names[idx]:<30} : {importances[idx]*100:.2f}%")

print("="*60)