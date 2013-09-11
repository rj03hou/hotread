from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from links.views import LinkListView
from links.views import LinkCreateView
from links.views import RssCreateView
from links.views import LinkDetailView
from links.views import LinkUpdateView
from links.views import LinkDeleteView
from links.views import UserProfileDetailView
from links.views import UserProfileEditView
from links.views import show_profile
from links.views import post_data
from links.views import show_tag_links



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gogoreader.views.home', name='home'),
    # url(r'^gogoreader/', include('gogoreader.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments', include("django.contrib.comments.urls")),
    url(r'^$', show_profile, name='home'),
    url(r'^post', post_data, name='post_data'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login',name="logout"),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^users/(?P<slug>\w+)/$', UserProfileDetailView.as_view(), name="profile"),
    url(r'edit_profile/$', auth(UserProfileEditView.as_view()), name='edit_profile'),
    url(r'^link/create/$', auth(LinkCreateView.as_view()), name='link_create'),
    url(r'^rss/create/$', auth(RssCreateView.as_view()), name='rss_create'),
    url(r'^link/update/(?P<pk>\d+)/$', auth(LinkUpdateView.as_view()), name='link_update'),
    url(r'^link/delete/(?P<pk>\d+)/$', auth(LinkDeleteView.as_view()), name='link_delete'),
    url(r'^link/(?P<pk>\d+)$', LinkDetailView.as_view(), name='link_detail'),
    url(r'^tag/(?P<pk>\d+)$', show_tag_links, name='link_tag'),

)
