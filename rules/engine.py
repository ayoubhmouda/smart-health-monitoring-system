from reasoning.models import Insight
from .models import Rule, CorrectiveAction

class RuleEngine:
    def __init__(self):
        self.rules = Rule.objects.filter(is_active=True)

    def process(self, insight: Insight):
        actions = []
        for rule in self.rules:
            if self._matches(insight, rule.condition):
                action = CorrectiveAction.objects.create(
                    insight=insight,
                    rule=rule,
                    description=rule.action_template,
                    status=CorrectiveAction.Status.PENDING
                )
                actions.append(action)
        return actions

    def _matches(self, insight, condition):
        # محرك بسيط يتحقق من وجود تطابق بين شروط القاعدة والـ insight
        try:
            conds = condition.get('conditions', [])
            operator = condition.get('operator', 'AND')
            results = []
            for cond in conds:
                results.append(self._evaluate(insight, cond))
            if operator == 'AND':
                return all(results)
            elif operator == 'OR':
                return any(results)
        except Exception:
            return False
        return False

    def _evaluate(self, insight, cond):
        # مثال بسيط: "severity == high" أو "confidence > 0.9"
        if '==' in cond:
            field, value = cond.split('==')
            field = field.strip()
            value = value.strip().strip("'\"")
            return str(getattr(insight, field, '')).lower() == value.lower()
        elif '>' in cond:
            field, value = cond.split('>')
            field = field.strip()
            value = float(value.strip())
            return float(getattr(insight, field, 0)) > value
        elif '<' in cond:
            field, value = cond.split('<')
            field = field.strip()
            value = float(value.strip())
            return float(getattr(insight, field, 0)) < value
        return False