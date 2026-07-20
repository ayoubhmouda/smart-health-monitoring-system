import re
with open('/app/core/models.py', 'r') as f:
    content = f.read()
new_class = '''class MedicalHistory(models.Model):
    monitored_element = models.OneToOneField(
        'MonitoredElement', on_delete=models.CASCADE, related_name='medical_history'
    )
    chronic_conditions = models.JSONField(default=list, blank=True, null=True)
    lifestyle = models.JSONField(default=dict, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Medical History of {self.monitored_element.full_name}'
'''
pattern = r'class MedicalHistory\(models\.Model\):.*?(?=\nclass |\Z)'
content = re.sub(pattern, new_class, content, flags=re.DOTALL)
with open('/app/core/models.py', 'w') as f:
    f.write(content)
print('Done')