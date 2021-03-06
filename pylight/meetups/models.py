import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from misc.models import SlugifyUploadTo


class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    logo = models.ImageField(upload_to=settings.SPONSOR_LOGOS_DIR)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Venue(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name


class MeetupManager(models.Manager):

    def get_upcoming(self, date=None):
        date = date or datetime.date.today()
        try:
            return self.filter(date__gte=date).order_by('date')[0]
        except IndexError:
            raise self.model.DoesNotExist


class Meetup(models.Model):
    number = models.PositiveIntegerField(unique=True)
    date = models.DateTimeField()
    sponsors = models.ManyToManyField(Sponsor, related_name='sponsored_meetups', blank=True)
    venue = models.ForeignKey(Venue, related_name='meetups', null=True, blank=True)
    is_ready = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True)

    objects = MeetupManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '{0} #{1}'.format(settings.MEETUP_NAME, self.number)

    def get_absolute_url(self):
        return reverse('meetups:meetup_detail', kwargs={'number': self.number})


class Speaker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    website = models.URLField(blank=True)
    photo = models.ImageField(
        upload_to=SlugifyUploadTo(settings.SPEAKER_PHOTOS_DIR, ['first_name', 'last_name']),
        blank=True,
    )
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    biography = models.TextField(blank=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    class Meta:
        ordering = ['first_name', 'last_name']


class Talk(models.Model):
    LANGUAGES = (
        ('pl', 'Polish'),
        ('en', 'English'),
    )

    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    speakers = models.ManyToManyField(Speaker, related_name='talks')
    meetup = models.ForeignKey(Meetup, related_name='talks', null=True, blank=True)
    order = models.PositiveSmallIntegerField(null=True)
    slides_file = models.FileField(
        upload_to=SlugifyUploadTo(settings.SLIDES_FILES_DIR, ['meetup', 'title']),
        blank=True,
        max_length=500,
    )
    slides_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    language = models.CharField(choices=LANGUAGES, default='pl', max_length=2)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ExternalLink(models.Model):
    EXTERNAL_LINK_TYPES = (
        ('photos', 'Photos'),
        ('article', 'Article'),
        ('other', 'Other'),
    )

    meetup = models.ForeignKey(Meetup, related_name='external_links')
    url = models.URLField()
    type = models.CharField(max_length=10, choices=EXTERNAL_LINK_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return '{} ({})'.format(self.url, self.meetup)


class TalkProposal(models.Model):
    talk = models.ForeignKey(Talk)
    message = models.TextField(blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Proposal: {}'.format(self.talk)


class Organizer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    photo = models.ImageField(
        upload_to=SlugifyUploadTo(settings.SPEAKER_PHOTOS_DIR, ['first_name', 'last_name']),
        blank=True,
    )
    biography = models.TextField(blank=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
