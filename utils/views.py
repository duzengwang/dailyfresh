# coding=utf-8
from django.views.generic import View
from django.contrib.auth.decorators import login_required


# 在django中对于类视图添加装饰器的方式
class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)


# 多继承的方案
class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)
