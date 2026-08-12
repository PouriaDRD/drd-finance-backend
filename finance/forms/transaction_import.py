from django import forms


class TransactionImportForm(forms.Form):
    file = forms.FileField(
        label="Import file",
        help_text=("CSV or Excel (.xlsx) file."),
    )

    def clean_file(self):
        file = self.cleaned_data["file"]

        filename = file.name.lower()

        allowed_extensions = (
            ".csv",
            ".xlsx",
        )

        if not filename.endswith(allowed_extensions):
            raise forms.ValidationError("فقط فایل CSV یا Excel (.xlsx) مجاز است.")

        if file.size == 0:
            raise forms.ValidationError("فایل خالی است.")

        # 20 MB
        max_size = 20 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError("حجم فایل نباید بیشتر از 20 مگابایت باشد.")

        return file
