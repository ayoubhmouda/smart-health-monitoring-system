import django, os, pickle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# --- 1. فحص النموذج المخزن ---
model_path = '/app/reasoning/ml/models/random_forest.pkl'
with open(model_path, 'rb') as f:
    data = pickle.load(f)

model = data['model']
feature_names = data['feature_names']
print("=" * 50)
print("فحص النموذج المخزن")
print("=" * 50)
print(f"عدد الأشجار: {model.n_estimators}")
print(f"عدد الميزات التي تدرب عليها: {len(feature_names)}")
print(f"أسماء الميزات: {feature_names}")

# --- 2. التحقق من الميزات التي خزنت في MLModelVersion ---
from reasoning.models import MLModelVersion
last_version = MLModelVersion.objects.order_by('-trained_at').first()
if last_version:
    print(f"\nآخر نموذج مسجل في القاعدة: {last_version.version_name}")
    print(f"Feature list: {last_version.feature_list}")
    print(f"Accuracy: {last_version.accuracy}")
    print(f"F1: {last_version.f1_score}")