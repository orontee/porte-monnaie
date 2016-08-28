"""Tracker models."""

from django.contrib.auth.models import AbstractUser
from django.db.models import (Count, DateField, DateTimeField,
                              FloatField, ForeignKey,
                              BooleanField,
                              CharField, ManyToManyField, Model,
                              SET_NULL, Sum,
                              Manager)
from django.utils import (six, timezone)
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

mark_safe_lazy = lazy(mark_safe, six.text_type)


class User(AbstractUser):
    """Extend the ``User`` class with a ``Purse`` field."""
    default_purse = ForeignKey('Purse', verbose_name=_('default purse'),
                               null=True, default=None,
                               on_delete=SET_NULL)


class Purse(Model):
    """Class representing purses."""
    name = CharField(_('purse name'), max_length=80)
    users = ManyToManyField(User, verbose_name=_('users'))
    description = CharField(_('description'), max_length=80, blank=True)
    created = DateTimeField(_('created'), auto_now_add=True)

    def __str__(self):
        return u'{0}'.format(self.id)

    def usernames(self):
        """Return the comma separated list of usernames sorted."""
        names = [u.first_name or u.username for u in self.users.all()]
        names.sort()
        return ', '.join(names)

    class Meta(object):
        """Purse metadata."""
        ordering = ['name', '-created']
        get_latest_by = 'created'


class Expenditure(Model):
    """Class representing expenditures.

    The attribute ``edit_delay`` controls the number of days from an
    expenditure creation to when it won't be editable anymore.
    """
    amount = FloatField(_('amount'), db_index=True)
    date = DateField(_('date'), default=timezone.now, db_index=True)
    description = CharField(_('description'), max_length=80, blank=False)
    author = ForeignKey(User, editable=False, verbose_name=_('author'))
    purse = ForeignKey(Purse, verbose_name=_('purse'))
    generated = BooleanField(_('generated'), default=False, editable=False)
    created = DateTimeField(_('created'), auto_now_add=True)

    edit_delay = 2

    def __str__(self):
        return u'{0}'.format(self.id)

    def is_editable(self):
        """Check whether it is an editable expenditure or not."""
        return (timezone.now() - self.created).days <= self.edit_delay

    def save(self, **kwargs):
        """Update tags from the saved expenditure."""
        super(Expenditure, self).save(**kwargs)
        Tag.objects.update_from(self)

    class Meta(object):
        """Expenditure metadata."""
        ordering = ('-date', '-created', 'author')
        get_latest_by = 'date'


class TagManager(Manager):
    """Custom manager for tags.

    Tags of length less than ``min_len`` are excluded. To allow tags
    of any length, set ``min_len`` to ``None``.
    """
    min_len = 2

    def get_tag_names(self, desc):
        """Split description and extract tag names."""
        return [n.lower() for n in desc.split()
                if not self.min_len or len(n) > self.min_len]

    def update_from(self, e, stats=None):
        """Update tags after saving the given expenditure.

        No treatment is done for generated expenditures.
        """
        if not e.generated:
            purse = e.purse
            qs = purse.tag_set.all()
            names = self.get_tag_names(e.description)
            for n in names:
                try:
                    t = qs.get(name=n)
                except Tag.DoesNotExist:
                    t = Tag.objects.create(name=n, purse=purse)
                    t.expenditures.add(e)
                    if stats:
                        stats[0] += 1
                else:
                    if e not in t.expenditures.all():
                        t.expenditures.add(e)
                        if stats:
                            stats[1] += 1
                        t.save()
            for t in e.tag_set.all():
                if t.name not in names:
                    t.expenditures.remove(e)
                    if stats:
                        stats[1] += 1

        return stats

    def get_tags_for(self, purse, lookup_params=None):
        """Return the the tags associated to ``purse``.

        The default query set may be filtered using ``lookup_params``.

        The returned tags are extended with the associated
        expenditures count and amount."""
        qs = purse.tag_set.all()
        if lookup_params is not None:
            qs = qs.filter(**lookup_params)
        qs = qs.annotate(count=Count('expenditures'),
                         amount=Sum('expenditures__amount'))
        return qs


class Tag(Model):
    """Class representing tags."""
    name = CharField(_('name'), max_length=80, db_index=True)
    purse = ForeignKey(Purse, verbose_name=_('purse'))
    expenditures = ManyToManyField(Expenditure,
                                   verbose_name=_('expenditures'))

    objects = TagManager()

    def __str__(self):
        return u'{0}'.format(self.id)
