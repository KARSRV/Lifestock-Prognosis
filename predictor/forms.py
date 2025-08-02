from django import forms

SYMPTOMS = [
    'painless lumps', 'blisters on hooves', 'blisters on tongue',
    'blisters on gums', 'swelling in limb', 'swelling in muscle', 'blisters on mouth',
    'crackling sound', 'lameness', 'swelling in abdomen', 'swelling in neck',
    'chest discomfort', 'fever', 'shortness of breath', 'swelling in extremities',
    'difficulty walking', 'chills', 'depression'
]

class SymptomForm(forms.Form):
    symptoms = forms.MultipleChoiceField(
        choices=[(symptom, symptom) for symptom in SYMPTOMS],
        widget=forms.CheckboxSelectMultiple,
        label="Select Symptoms"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symptoms'].widget.attrs.update({
            'class': 'custom-checkbox',
        })
