import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIMIC_DIR = os.path.join(BASE_DIR, 'data', 'mimic-iv-clinical-database-demo-2.2')

CHARTEVENTS_PATH = os.path.join(MIMIC_DIR, 'icu', 'chartevents.csv.gz')
ICUSTAYS_PATH = os.path.join(MIMIC_DIR, 'icu', 'icustays.csv.gz')
PATIENTS_PATH = os.path.join(MIMIC_DIR, 'hosp', 'patients.csv.gz')
DIAGNOSES_PATH = os.path.join(MIMIC_DIR, 'hosp', 'diagnoses_icd.csv.gz')

ITEM_MAP = {
    220045: 'heart_rate',
    220179: 'blood_pressure_systolic',
    220050: 'blood_pressure_systolic',
    220180: 'blood_pressure_diastolic',
    220051: 'blood_pressure_diastolic',
    220277: 'oxygen_saturation',
    223761: 'body_temperature',
    220210: 'respiratory_rate'
}

def load_and_process_vitals():
    print("⏳ قراءة وتنقية قراءات المستشعرات الحيوية من MIMIC...")
    chunks = pd.read_csv(
        CHARTEVENTS_PATH, 
        usecols=['stay_id', 'charttime', 'itemid', 'valuenum'],
        chunksize=100000
    )
    
    vitals_list = []
    for chunk in chunks:
        filtered = chunk[chunk['itemid'].isin(ITEM_MAP.keys())].copy()
        filtered['sensor_name'] = filtered['itemid'].map(ITEM_MAP)
        vitals_list.append(filtered)
        
    vitals_df = pd.concat(vitals_list, ignore_index=True)
    vitals_df['charttime'] = pd.to_datetime(vitals_df['charttime'])
    
    temp_mask = (vitals_df['sensor_name'] == 'body_temperature') & (vitals_df['valuenum'] > 50)
    vitals_df.loc[temp_mask, 'valuenum'] = (vitals_df.loc[temp_mask, 'valuenum'] - 32) * 5/9

    return vitals_df

def extract_features_per_stay(vitals_df):
    print("📊 استخراج ميزات السلاسل الزمنية...")
    pivoted = vitals_df.pivot_table(
        index=['stay_id', 'charttime'], 
        columns='sensor_name', 
        values='valuenum'
    ).reset_index()
    
    aggregated = pivoted.groupby('stay_id').agg({
        'heart_rate': ['mean', 'std', 'max', 'min'],
        'blood_pressure_systolic': ['mean', 'std', 'max'],
        'blood_pressure_diastolic': ['mean', 'std', 'min'],
        'oxygen_saturation': ['mean', 'min'],
        'body_temperature': ['mean', 'max'],
        'respiratory_rate': ['mean', 'max']
    })
    
    aggregated.columns = ['_'.join(col).strip() for col in aggregated.columns.values]
    return aggregated.reset_index()

def load_patient_history():
    print("📜 استخراج التاريخ الطبي والديموغرافي الرقمي...")
    icustays = pd.read_csv(ICUSTAYS_PATH, usecols=['stay_id', 'subject_id'])
    patients = pd.read_csv(PATIENTS_PATH, usecols=['subject_id', 'gender', 'anchor_age'])
    
    # 🟢 تحويل الجنس إلى قيمة رقمية: 1 للأنثى، 0 للذكر
    patients['is_female'] = (patients['gender'] == 'F').astype(int)
    patients = patients.drop(columns=['gender'])

    diagnoses = pd.read_csv(DIAGNOSES_PATH, usecols=['subject_id', 'icd_code'])
    diagnoses['has_heart_disease'] = diagnoses['icd_code'].astype(str).str.startswith(('I50', 'I21', 'I25', '410', '428'), na=False).astype(int)
    diagnoses['has_chronic_condition'] = diagnoses['icd_code'].astype(str).str.startswith(('E11', 'I10', 'J44', '250', '401'), na=False).astype(int)
    
    history = diagnoses.groupby('subject_id').agg({
        'has_heart_disease': 'max',
        'has_chronic_condition': 'max'
    }).reset_index()
    
    patient_history = pd.merge(patients, history, on='subject_id', how='left').fillna(0)
    stay_history = pd.merge(icustays, patient_history, on='subject_id', how='left')
    return stay_history

if __name__ == "__main__":
    print("🚀 بدء تجهيز داتاسيت التدريب المحدثة...")
    vitals_df = load_and_process_vitals()
    features_df = extract_features_per_stay(vitals_df)
    
    history_df = load_patient_history()
    final_df = pd.merge(features_df, history_df, on='stay_id', how='left')
    
    final_df['has_heart_disease'] = final_df['has_heart_disease'].fillna(0).astype(int)
    final_df['has_chronic_condition'] = final_df['has_chronic_condition'].fillna(0).astype(int)
    final_df['anchor_age'] = final_df['anchor_age'].fillna(50)
    final_df['is_female'] = final_df['is_female'].fillna(0).astype(int)
    
    final_df['activity_level_baseline'] = 1
    final_df['room_temperature_baseline'] = 22.0
    
    output_path = os.path.join(BASE_DIR, 'reasoning', 'ml', 'mimic_ml_dataset.csv')
    final_df.to_csv(output_path, index=False)
    print(f"✅ تم تحديث الداتاسيت بنجاح وكل الأعمدة أصبحت رقمية (Numeric) بالكامل!")