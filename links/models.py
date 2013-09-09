from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.contrib import admin


class LinkVoteCountManager(models.Manager):
    def get_query_set(self):
        return super(LinkVoteCountManager, self).get_query_set().annotate(
            votes=Count('vote')).order_by('-votes')

class Tag(models.Model):
    #tagname submitter published_time
    name = models.CharField("Name", max_length=100)
    submitter = models.ForeignKey(User)
    published_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class Link(models.Model):
    title = models.CharField("Headline", max_length=100)
    submitter = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    published_time = models.DateTimeField(auto_now_add=True)
    rank_score = models.FloatField(default=0.0)
    url = models.URLField("URL", max_length=250, blank=True)
    short_url = models.URLField("ShortURL",max_length=250, blank=True)
    source = models.URLField("Source",max_length=250, blank=True)
    weibo_sharecount = models.PositiveIntegerField(default=0)
    weibo_commentcount = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    with_votes = LinkVoteCountManager()
    objects = models.Manager() # default Manager

    def get_absolute_url(self):
        return reverse('link_detail', kwargs={'pk':str(self.id)})

    def __unicode__(self):
        return self.title

class RssSource(models.Model):
    #tagname submitter published_time
    title = models.CharField("Title", max_length=255)
    published_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    tag = models.ForeignKey(Tag)
    url = models.URLField("URL", max_length=250, blank=True)

    def __unicode__(self):
        return self.title

class Vote(models.Model):
    voter = models.ForeignKey(User)
    link = models.ForeignKey(Link)

    def __unicode__(self):
        return "%s voted for %s" % (self.voter.username, self.link.title)

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    # extra attributes
    bio = models.TextField(null=True)

    def ___unicode__(self):
        return "%s profile" % self.user

def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)
admin.site.register((Tag,RssSource))
