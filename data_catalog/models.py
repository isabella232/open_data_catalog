"""Models for the data catalog."""

from collections import defaultdict

from django.db import models
from autoslug import AutoSlugField
from markdown import markdown


class Tag(models.Model):
    """
    A model for unique tags. The name field is indexed in order for fast
    queries.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def search_resources(keyword):
        """
        Return all resources linked to a tag. If the tag is not found,
        search through App, Data, and Idea models for instances that contain
        the keyword in their name.
        """
        results = {}
        try:
            tag = Tag.objects.select_related().get(name__iexact=keyword)
        except Tag.DoesNotExist:
            results['apps'] = App.objects.filter(name__icontains=keyword)
            results['data'] = Data.objects.filter(name__icontains=keyword)
            results['ideas'] = Idea.objects.filter(name__icontains=keyword)
        else:
            results['apps'] = tag.apps.all()
            results['data'] = tag.data.all()
            results['ideas'] = tag.ideas.all()
        return results


class Resource(models.Model):
    """An abstract model for resources submitted to the data catalog."""
    name = models.CharField(max_length=100, db_index=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField()

    class Meta:
        abstract = True


class App(Resource):
    """A model for a submitted application."""
    url = models.URLField('URL', verify_exists=False)
    tags = models.ManyToManyField(Tag, related_name='apps')

    def __unicode__(self):
        return self.name


class Data(Resource):
    """A model for submitted data."""
    url = models.URLField('URL', verify_exists=False, blank=True)
    tags = models.ManyToManyField(Tag, related_name='data')

    class Meta:
        verbose_name_plural = 'Data'

    def __unicode__(self):
        return self.name


class Idea(Resource):
    """A model for submitted ideas."""
    type = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField(Tag, related_name='ideas')

    def __unicode__(self):
        return self.name
