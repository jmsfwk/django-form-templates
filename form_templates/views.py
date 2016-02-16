from django.core.exceptions import ImproperlyConfigured
from django.template import Template, Context, Engine
from django.views.generic.edit import FormView, SingleObjectMixin, ModelFormMixin


class TemplateContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_template_context_data as the template context.
    """
    context_template_name = None

    def get_template_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs

    def get_context_template_name(self):
        """
        Get the name to use for the rendered template.
        """
        return getattr(self, 'context_template_name', None)


class TemplateRenderMixin(object):
    """
    A mixin that can be used to render an additional template.
    """

    def get_template_context(self, **kwargs):
        return Context(self.get_template_context_data(**kwargs))

    def render_template(self, context=None):
        """
        Returns a string using a template rendered with the given context.
        """
        if context is None:
            context = self.get_template_context()
        return self.get_template_object().render(context)


class FormTemplateMixin(TemplateRenderMixin, TemplateContextMixin):

    def use_template(self, rendered_template):
        """

        """
        self.rendered_template = rendered_template

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity. Does something with the
        rendered template.
        """
        form = self.get_form()
        if form.is_valid():
            self.use_template(self.render_template())
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class FormTemplateView(FormTemplateMixin, FormView):
    """
    A mixin that can render an additional template using form data.

    Method Flowchart

        dispatch()
        http_method_not_allowed()
        ├───get()
        │ ├──get_context_data()
        │ └───render_to_response()
        ├───post()
        │ └───If valid:
        │ │ ├───use_template()
        │ │ ├──get_template_context()
        │ │ ├──render_template()
        │ │ ├──use_template()
        │ └──form_valid() / form_invalid()
        └──render_to_response/redirect()
    """
    template_string = None

    def get_template(self):
        if not self.template_string:
            raise ImproperlyConfigured(
                "No additional template set. Provide a template.")
        return self.template_string

    def get_template_object(self):
        """
        Returns the supplied template.
        """
        return Engine().from_string(self.get_template())


class ModelFormTemplateMixin(object):
    model_template_name = None

    def get_template(self):
        """
        Returns the supplied template.
        """
        model = self.get_object()
        template_name = self.model_template_name or 'template'
        try:
            template_string = getattr(model, template_name)
        except AttributeError as e:
            raise ImproperlyConfigured(
                "%(model)s is missing a template. Define "
                "%(model)s.template, %(cls)s.model_template_name "
                "or override %(cls)s.get_template()." % {
                    'model': model.__class__.__name__,
                    'cls': self.__class__.__name__
                }
            )
        return template_string
