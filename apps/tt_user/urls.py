from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
urlpatterns = [
    url('^register$',views.RegisterView.as_view()),
    url('^active/(.+)$', views.active),
    url('^exists$', views.exists),
    url('^login$', views.LoginView.as_view()),
    url('^logout$',views.logout_user),
    url('^info$',views.info),
    url('^order$',views.order),
    url('^site$',views.SiteView.as_view()),
    # url('^site$',login_required(views.SiteView.as_view())),
    url('^area$',views.area),
]