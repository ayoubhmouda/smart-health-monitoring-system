import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from .data_generator import ClinicalScenarioGenerator
from .feature_engineering import prepare_training_data
import os

def train_and_save_model():
    print("Generating training scenarios...")
    generator = ClinicalScenarioGenerator()
    all_scenarios = generator.generate_mixed_scenarios(num_each=30)  # 30 من كل نوع

    print(f"Total data points: {len(all_scenarios)}")
    X, y = prepare_training_data(all_scenarios)

    # تحويل الميزات من قواميس إلى مصفوفة
    import pandas as pd
    X_df = pd.DataFrame(X)
    feature_names = X_df.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X_df, y, test_size=0.2, random_state=42)

    print("Training Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1:.2f}")
    print("Confusion Matrix:\n", cm)

    # حفظ النموذج والميزات
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'random_forest.pkl')

    with open(model_path, 'wb') as f:
        pickle.dump({'model': model, 'feature_names': feature_names}, f)

    print(f"Model saved to {model_path}")
    return model, feature_names, accuracy, precision, recall, f1

if __name__ == "__main__":
    train_and_save_model()