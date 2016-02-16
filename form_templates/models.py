from django.db import models
from fobi.models import FormEntry


class FormTemplateMixin(models.Model):
    template = models.TextField()
    form = models.ForeignKey(to=FormEntry)

    def get_form_class(self):
        """
        Builds an actual Form.
        
        Returns:
            (django.forms.Form)
        """
        form_element_entries = self.form.formelemententry_set.all()[:]
        # This is where the most of the magic happens. Our form is being built
        # dynamically.
        FormClass = assemble_form_class(
            self.form,
            form_element_entries=form_element_entries,
            request=self.request
        )
        return FormClass

    class Meta:
        abstract = True
