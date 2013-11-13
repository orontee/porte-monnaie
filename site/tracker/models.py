from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import (DateField, DateTimeField,
                              FloatField, ForeignKey, IntegerField,
                              BooleanField,
                              CharField, ManyToManyField, Model,
                              SET_NULL, Manager)
from django.utils import (six, timezone)
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

mark_safe_lazy = lazy(mark_safe, six.text_type)


class User(AbstractUser):
    """Extend the ``User`` class with a ``Purse`` field.
    """
    default_purse = ForeignKey('Purse', verbose_name=_('default purse'),
                               null=True, default=None,
                               on_delete=SET_NULL)


class Purse(Model):
    """Class representing purses.
    """
    name = CharField(_('purse name'), max_length=80)
    users = ManyToManyField(User, verbose_name=_('users'))
    description = CharField(_('description'), max_length=80, blank=True)
    created = DateTimeField(_('created'), auto_now_add=True)

    def __str__(self):
        return u'Purse: {0}'.format(self.id)

    def usernames(self):
        """Return the comma separated list of usernames sorted.
        """
        names = [u.first_name or u.username for u in self.users.all()]
        names.sort()
        return ', '.join(names)

    class Meta(object):
        """Purse metadata.
        """
        ordering = ['name', '-created']
        get_latest_by = 'created'


class Expenditure(Model):
    """Class representing expenditures.

    The attribute ``edit_delay`` controls the number of days from an
    expenditure creation to when it won't be editable anymore.
    """
    amount = FloatField(_('amount'))
    date = DateField(_('date'), default=timezone.now().date())
    description = CharField(_('description'), max_length=80, blank=True)
    author = ForeignKey(User, editable=False, verbose_name=_('author'))
    purse = ForeignKey(Purse, verbose_name=_('purse'))
    generated = BooleanField(_('generated'), default=False, editable=False)
    created = DateTimeField(_('created'), auto_now_add=True)

    edit_delay = 2

    def __str__(self):
        return u'Expenditure: {0}'.format(self.id)

    def is_editable(self):
        """Check whether it is an editable expenditure or not.
        """
        return (timezone.now() - self.created).days <= self.edit_delay

    class Meta(object):
        """Expenditure metadata.
        """
        ordering = ('-date', '-created', 'author')
        get_latest_by = 'date'


class TagManager(Manager):
    """Custom manager for tags.

    Tags of length less than ``min_len`` are excluded. To allow tags
    of any length, set ``min_len`` to ``None``.
    """
    min_len = 2

    def update_from(self, e, stats=None):
        """Update tags from the given expenditure.

        Raise an ``AttributeError`` exception in case ``e`` hasn't the
        needed ``purse``, ``desc``, ``generated`` and ``created``
        attributes.

        No treatment is done for generated expenditures.
        """
        if not e.generated:
            purse = e.purse
            desc = e.description
            qs = Tag.objects.filter(purse__id__exact=purse.id)\
                            .order_by('last_use')
            names = [n.lower() for n in desc.split()
                     if not self.min_len or len(n) > self.min_len]
            for n in names:
                try:
                    t = qs.get(name=n)
                except Tag.DoesNotExist:
                    t = Tag(name=n, purse=purse, weight=1,
                            last_use=e.created)
                    if stats:
                        stats[0] += 1
                else:
                    if t.last_use < e.created:
                        t.weight += 1
                        t.last_use = e.created
                        if stats:
                            stats[1] += 1
                t.save()
        return stats

    def get_names_for(self, purse, limit=20):
        """Return the names of the tags associated to ``purse``.

        The tags are ordered by weight. It returns at most ``limit``
        results in case ``limit`` is not ``None``.

        """
        qs = purse.tag_set.only('name').order_by('-weight')
        if limit is not None:
            qs = qs[:limit]
        return sorted(qs.values_list('name', flat=True))


class Tag(Model):
    """Class representing tags.
    """
    name = CharField(_('name'), max_length=80, db_index=True)
    purse = ForeignKey(Purse, verbose_name=_('purse'))
    weight = IntegerField(_('weight'))
    last_use = DateTimeField(_('last use'))
    objects = TagManager()

    def __str__(self):
        return u'Tag: {0}'.format(self.id)

    class Meta(object):
        """Tag metadata.
        """
        ordering = ('-weight',)


@receiver(post_save, sender=Expenditure)
def update_tags(sender, instance, created, raw, **kwargs):
    """Update tags from the saved expenditure.
    """
    if not raw:
        Tag.objects.update_from(instance)
