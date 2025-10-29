from django.shortcuts import redirect
from django.views.generic.base import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/admin')