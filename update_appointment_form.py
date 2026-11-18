from pathlib import Path

path = Path("core/forms.py")
content = path.read_text(encoding="utf-8")

old = '''    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
'''

new = '''    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = (
            self.fields["service"].queryset.filter(is_active=True)
        )

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
'''

if content.count(old) != 1:
    raise SystemExit("STOP: Expected insertion point not found exactly once.")

path.write_text(content.replace(old, new, 1), encoding="utf-8")
print("SUCCESS: Appointment form now filters active services.")
