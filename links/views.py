from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
import datetime

from .models import Link, Vote, UserProfile, Tag
from .forms import UserProfileForm
from .forms import LinkForm
from django.shortcuts import render

from django.http import HttpResponse
from django.template import RequestContext, loader

from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
import simplejson as json


'''
	title = models.CharField("Headline", max_length=100)
	submitter = models.ForeignKey(User)
	submitted_on = models.DateTimeField(auto_now_add=True)
	rank_score = models.FloatField(default=0.0)
	url = models.URLField("URL", max_length=250, blank=True)
	description = models.TextField(blank=True)

	with_votes = LinkVoteCountManager()
	objects = models.Manager() # default Manager
'''

def show_tag_links(request,pk):
    tag_id = int(pk)
    return show_profile(request,tag_id)
    #return HttpResponse("hello world!%d"%tag_id)

def show_profile(request,tag_id=0):
    tag_list = Tag.objects.all()[:50]
    if tag_id == 0:
        link_lists = Link.objects.all().order_by('-rank_score')[:50]
    else:
        link_lists = Link.objects.filter(tag_id=tag_id).order_by('-rank_score')[:50]
    content_list = []
    for link in link_lists:
        #hours = (datetime.datetime.now()-link.published_time.replace(tzinfo=None)).seconds/60/60
        timedelta = datetime.datetime.now()-link.published_time
        hours = timedelta.days*24 + timedelta.seconds/60/60
        content_list.append({"link":link,"hours":hours})

    template = loader.get_template('home.html')
    context = RequestContext(request, {
		'content_list':content_list,'tag_list':tag_list
	})
    return HttpResponse(template.render(context))


def post_data(request):
	data = { 'code': 200, }
	name = request.GET.get('v', '')
	if not name:
		data['code'] = 1000
	else:
		link_lists = Link.objects.filter(id=name)
		link_lists.weibo_commentcount +=1
		link_lists.save()
	return HttpResponse(json.dumps(data))


class LinkCreateView(CreateView):
	model = Link
	form_class = LinkForm
	
	def form_valid(self, form):
		f = form.save(commit=False)
		f.rank_score = 0.0
		f.submitter = self.request.user
		f.save()
		return super(LinkCreateView, self).form_valid(form)


class LinkListView(ListView):
	model = Link
	query = Link.with_votes.all()
	paginate_by = 5

class LinkDetailView(DetailView):
	model = Link

class LinkUpdateView(UpdateView):
	model = Link
	form_class = LinkForm

class LinkDeleteView(DeleteView):
	model = Link
	success_url = reverse_lazy('home');

class UserProfileDetailView(DetailView):
	model = get_user_model()
	slug_field = 'username'
	template_name = 'user_detail.html'

	def get_object(self, queryset=None):
		user = super(UserProfileDetailView, self).get_object(queryset)
		UserProfile.objects.get_or_create(user=user)
		return user

class UserProfileEditView(UpdateView):
	model = get_user_model()
	template_name = 'edit_profile.html'
	form_class = UserProfileForm

	def get_object(self, queryset=None):
		return UserProfile.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self):
		return reverse('profile', kwargs={'slug': self.request.user})