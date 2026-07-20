from reasoning.models import Insight
from .models import Rule, CorrectiveAction

class RuleEngine:
    """يحول Insight إلى CorrectiveAction بناءً على قواعد محددة (دور حتمي حسب الورقة)."""

    def __init__(self):
        # يمكن جلب القواعد من قاعدة البيانات في المستقبل
        pass

    def process(self, insight: Insight) -> list[CorrectiveAction]:
        """
        يفحص الـ Insight ويقرر الإجراء المناسب.
        هذه قواعد بسيطة (if/else) كما هو متوقع في الأنظمة الطبية الحتمية.
        """
        actions = []

        # الحصول على قاعدة نشطة أو إنشاء قاعدة افتراضية لتفادي أخطاء عدم إدخال حقل rule_id المطلوب في قاعدة البيانات
        rule = Rule.objects.filter(is_active=True).first()
        if not rule:
            rule, _ = Rule.objects.get_or_create(
                name="Default System Rule",
                defaults={
                    "condition": {"operator": "AND", "conditions": ["severity == high"]},
                    "action_template": "Notify Doctor",
                    "is_active": True
                }
            )

        if insight.severity == Insight.Severity.HIGH or insight.severity == Insight.Severity.CRITICAL:
            # إجراء فوري: إشعار الطبيب
            action = CorrectiveAction.objects.create(
                insight=insight,
                rule=rule,
                description=f"إنذار عاجل: {insight.get_severity_display()} - الثقة {insight.confidence}",
                status=CorrectiveAction.Status.PENDING
            )
            actions.append(action)

        elif insight.severity == Insight.Severity.MEDIUM:
            # إجراء تحذيري: مراقبة إضافية
            action = CorrectiveAction.objects.create(
                insight=insight,
                rule=rule,
                description=f"تحذير: {insight.get_severity_display()} - الثقة {insight.confidence}. مراقبة مستمرة.",
                status=CorrectiveAction.Status.PENDING
            )
            actions.append(action)

        # يمكن إضافة قواعد أكثر تعقيداً هنا لاحقاً (مثل فحص العمر أو أمراض معينة)

        return actions