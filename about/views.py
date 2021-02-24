from django.views.generic.base import TemplateView


class about_author_page(TemplateView):
    template_name = 'about/author.html'


class about_tech_page(TemplateView):
    template_name = 'about/tech.html'
