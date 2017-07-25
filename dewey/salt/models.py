from django.db import models
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

from dewey.environments.models import Host


class Highstate(models.Model):
    host = models.ForeignKey(Host)
    timestamp = models.DateTimeField()
    return_code = models.IntegerField()
    jid = models.CharField(max_length=32)
    received = models.DateTimeField(auto_now_add=True)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return 'highstate {} on host {}'.format(self.jid, self.host.hostname)


class HighstateEvent(models.Model):
    highstate = models.ForeignKey('Highstate')
    state_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    @property
    def host(self):
        return self.highstate.host

    class Meta:
        abstract = True


class StateError(HighstateEvent):
    def __str__(self):
        return 'error {} {}'.format(self.state_id, self.highstate.jid)


class StateChange(HighstateEvent):
    def __str__(self):
        return 'change {} {}'.format(self.state_id, self.highstate.jid)


class Change(models.Model):
    state_change = models.ForeignKey('StateChange')
    change_type = models.CharField(max_length=128)
    content = models.TextField()

    def __str__(self):
        return '{} for state {} {}'.format(self.change_type, self.state_change.state_id, self.state_change.highstate.jid)

    @property
    def highstate(self):
        return self.state_change.highstate

    @property
    def host(self):
        return self.highstate.host

    @property
    def diff(self):
        if self.change_type == 'diff':
            content = self.content.replace('\\n', '\n')
            return highlight(content, DiffLexer(), HtmlFormatter(cssclass='code highlight', noclasses=True))
