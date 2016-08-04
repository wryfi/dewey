import base64
import json
import os
import re
import requests

from django.contrib.contenttypes.models import ContentType
from django_enumfield import enum
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.conf import settings
from django.utils import timezone

from dewey.utils import dotutils, ProtocolEnum
from . import ClusterType, OperatingSystem


try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass


VAULT_REGEX = re.compile(r'vault:v\d:.*')


class Environment(models.Model):
    name = models.SlugField(help_text='a short name for this environment')
    hostname_regex = models.CharField(help_text='regex that defines valid host names for this env', max_length=128)
    description = models.TextField(help_text='(optional) description of the environment', blank=True)
    monitored = models.BooleanField(help_text='should new hosts in this environment be monitored by default?')

    def __str__(self):
        return 'environment: {}'.format(self.name)

    @property
    def safes(self):
        return [safe for safe in Safe.objects.filter(vault__environment=self)]


class Role(models.Model):
    name = models.CharField(max_length=256, help_text='matches salt state name')
    description = models.CharField(max_length=256, blank=True)
    safe_acls = GenericRelation('SafeAccessControl')

    def __str__(self):
        return self.name

    @property
    def hosts(self):
        return self.host_set.all()

    @property
    def monitored_hosts(self):
        return [host for host in self.host_set.all() if host.monitored]


class Host(models.Model):
    """
    A network host. Hosts must have a parent, which may be: (1) a piece of hardware
    (e.g. Server, PowerDistributionUnit, or NetworkDevice); or (2) another host
    (e.g. for a static VM); or (3) a cluster of hosts (e.g. a VM on an ESXi cluster)
    """
    hostname = models.CharField(max_length=256, help_text='FQDN')
    environment = models.ForeignKey('Environment')
    roles = models.ManyToManyField('Role', blank=True)
    operating_system = enum.EnumField(OperatingSystem)
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    parent = GenericForeignKey('parent_type', 'parent_id')
    virtual_machines = GenericRelation(
        'Host',
        content_type_field='parent_type',
        object_id_field='parent_id'
    )
    safe_acls = GenericRelation('SafeAccessControl')

    def __str__(self):
        return self.hostname

    @property
    def domain(self):
        components = self.hostname.split('.')
        return '.'.join(components[1:])

    @property
    def kind(self):
        if not self.parent:
            return 'unknown'
        # can't be imported with module - creates circular import
        from hardware.models import Server
        if type(self.parent) == Host or type(self.parent) == Cluster:
            return 'virtual machine'
        elif type(self.parent) == Server:
            return 'bare metal host os'
        else:
            return 'peripheral host'

    @property
    def shortname(self):
        return self.hostname.split('.')[0]

    @property
    def ip_addresses(self):
        grouped = {}
        for assignment in self.address_assignments.all():
            details = {'address': assignment.address, 'network': assignment.network.cidr,
                       'netmask': assignment.network.netmask, 'mask_bits': assignment.network.mask_bits,
                       'gateway': assignment.network.gateway}
            if assignment.network.interface_id not in grouped:
                grouped[assignment.network.interface_id] = [details]
            else:
                grouped[assignment.network.interface_id].append(details)
        return grouped

    @property
    def canonical_assignment(self):
        for assignment in self.address_assignments.all():
            if assignment.canonical:
                return assignment

    @property
    def rolenames(self):
        return sorted([role.name for role in self.roles.all()])

    @property
    def safes(self):
        """
        returns a list of all the secrets safes that this host can access
        """
        safes = []
        all_env_role_acls = []
        my_env_role_acls = []
        for role in self.roles.all():
            for acl in role.safe_acls.filter(safe__vault__all_environments=True):
                all_env_role_acls.append(acl)
            for acl in role.safe_acls.filter(safe__vault__environment=self.environment):
                my_env_role_acls.append(acl)
        all_env_host_acls = self.safe_acls.filter(safe__vault__all_environments=True)
        my_env_host_acls = self.safe_acls.filter(safe__vault__environment=self.environment)
        all_env_all_host_acls = SafeAccessControl.objects.filter(
                safe__vault__all_environments=True
            ).filter(all_hosts=True)
        my_env_all_host_acls = SafeAccessControl.objects.filter(
                safe__vault__environment=self.environment
            ).filter(all_hosts=True)
        # return the safes in the order we want to inherit secrets!
        for acls in [
            all_env_all_host_acls, all_env_role_acls, all_env_host_acls,
            my_env_all_host_acls, my_env_role_acls, my_env_host_acls
        ]:
            for acl in acls:
                safes.append(acl.safe)
        return safes

    @property
    def secrets(self):
        secrets = []
        for safe in self.safes:
            for secret in safe.secret_set.all():
                secrets.append(secret)
        return sorted(secrets, key=lambda sec: sec.name)

    @property
    def salt_secrets(self):
        secrets = {}
        for secret in self.secrets:
            secrets[secret.name] = secret.export_format
        return dotutils.expand_flattened_dict(secrets)

    @property
    def monitored(self):
        monitored = self.environment.monitored
        for mexcept in self.hostmonitoringexception_set.all():
            now = timezone.now()
            if mexcept.start <= now <= mexcept.end:
                monitored = mexcept.monitored
        return monitored

    def delete(self, *args, **kwargs):
        """
        Django's default behavior will cascade deletes here, causing the deletion
        of a sever to delete all of that server's child hosts. So throw an
        error if the cluster has any remaining VMs.
        """
        if self.virtual_machines.all():
            children = [vm.hostname for vm in self.virtual_machines.all()]
            raise RuntimeError('cannot delete host until its VMs have been reassigned: {}'.format(children))
        super(Host, self).delete(*args, **kwargs)


class HostMonitoringException(models.Model):
    host = models.ForeignKey('Host', help_text='host to create exception for')
    monitored = models.BooleanField(help_text='force monitored (True) or unmonitored (False)')
    start = models.DateTimeField(help_text='when should this exception begin?')
    end = models.DateTimeField(help_text='when should this exception end?')

    def __str__(self):
        text = 'monitor {} from {} to {}'.format(self.host.hostname, self.start.date(), self.end.date())
        if self.monitored:
            return text
        else:
            return ' '.join(['do not', text])


class Cluster(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=128, blank=True)
    kind = enum.EnumField(ClusterType)
    members = models.ManyToManyField('Host')
    virtual_machines = GenericRelation(
        'Host',
        content_type_field='parent_type',
        object_id_field='parent_id'
    )

    def __str__(self):
        return 'cluster: {}'.format(self.name)

    def delete(self, *args, **kwargs):
        """
        Django's default behavior will cascade deletes here, causing the deletion
        of a cluster to delete all of that clusters's members and hosts. So throw an
        error if the cluster has any remaining VMs. Otherwise, delete the members
        from the object before calling delete on it.
        """
        if self.virtual_machines.all():
            children = [vm.hostname for vm in self.virtual_machines.all()]
            raise RuntimeError('cannot delete cluster until its hosts have been reassigned: {}'.format(children))
        for member in self.members.all():
            self.members.remove(member)
        self.save()
        super(Cluster, self).delete(*args, **kwargs)


class Vault(models.Model):
    name = models.CharField(max_length=256, help_text='a friendly name for this vault', unique=True)
    all_environments = models.BooleanField(default=False,
                                           help_text='this vault is for secrets shared among environments')
    environment = models.ForeignKey('Environment', null=True, blank=True,
                                    help_text='this vault is specific to the selected environment')
    vault_protocol = enum.EnumField(ProtocolEnum)
    vault_host = models.CharField(max_length=256)
    vault_port = models.PositiveIntegerField()
    transit_key_name = models.CharField(max_length=256)
    vault_user = models.CharField(max_length=128)
    vault_password_variable = models.CharField(max_length=128, help_text='environment variable containing password')

    def __str__(self):
        return 'vault {}'.format(self.name)

    @property
    def password(self):
        return os.environ.get(self.vault_password_variable)

    @property
    def url(self):
        protocol = self.get_vault_protocol_display()
        return '{}://{}:{}'.format(protocol, self.vault_host, self.vault_port)

    @property
    def environment_name(self):
        if self.all_environments:
            return 'all'
        elif self.environment:
            return self.environment.name
        else:
            return 'unknown'

    def save(self, *args, **kwargs):
        if self.all_environments:
            if self.environment:
                raise RuntimeError('you must choose a specific environment, or all environments, not both')
        if not self.all_environments:
            if not self.environment:
                raise RuntimeError('you must choose either a specific environment, or all environments')
        super(Vault, self).save(*args, **kwargs)


class Safe(models.Model):
    """
    a Safe is a collection of secrets encrypted with a specific Vault
    which has an ACL defining what hosts and roles can access its secrets
    """
    name = models.CharField(max_length=256, help_text='name for this collection of secrets')
    vault = models.ForeignKey('Vault')

    @property
    def environment(self):
        return self.vault.environment

    @property
    def environment_name(self):
        return self.vault.environment_name

    @property
    def access_controls(self):
        """
        Provides a representation of the access control objects associated
        with this safe. Does not take environment into consideration.
        """
        access = {'all': False, 'roles': [], 'hosts': []}
        for control in self.safeaccesscontrol_set.all():
            if control.all_hosts:
                access['all'] = True
                return access
            else:
                if type(control.acl_object) == Host:
                    access['hosts'].append(control.acl_object)
                elif type(control.acl_object) == Role:
                    access['roles'].append(control.acl_object)
        return access

    def __str__(self):
        return '{} :: {}'.format(self.name, self.vault.name)


class SafeAccessControl(models.Model):
    """
    SafeAccessControl objects determine what hosts and roles can access a safe
    """
    safe = models.ForeignKey('Safe')
    all_hosts = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    acl_object = GenericForeignKey('content_type', 'object_id')

    @property
    def acl_object_name(self):
        if self.all_hosts:
            return 'all hosts'
        else:
            return '{} {}'.format(self.content_type.name, self.acl_object)

    def save(self, *args, **kwargs):
        if self.all_hosts:
            if self.content_type or self.object_id:
                raise RuntimeError('set either all_hosts, or a specific object, but not both')
        if not self.all_hosts:
            if not self.content_type or not self.object_id:
                raise RuntimeError('you must set either all_hosts or a specific object')
        super(SafeAccessControl, self).save(*args, **kwargs)

    def __str__(self):
        return '{} access to {}'.format(self.acl_object_name, self.safe)


class Secret(models.Model):
    name = models.CharField(max_length=256, help_text='dotted-path key for this secret')
    safe = models.ForeignKey('Safe')
    secret = models.TextField()

    @property
    def export_format(self):
        return '::'.join([self.safe.vault.vault_host, self.safe.vault.transit_key_name, self.secret])

    def _encrypt_secret(self):
        """
        This method transforms any plaintext value in the secret field into a vault
        ciphertext. It should always be called before saving a Secret to avoid
        writing the unencrypted secret to disk; this is handled automatically in most
        cases by the overridden save() method below.
        """
        if not re.match(VAULT_REGEX, self.secret):
            auth_request = requests.post(
                '/'.join([self.safe.vault.url, 'v1/auth/userpass/login', self.safe.vault.vault_user]),
                data=json.dumps({'password': self.safe.vault.password}),
                verify=settings.PLOS_CA_CERTIFICATE
            )
            auth_request.raise_for_status()
            token = auth_request.json()['auth']['client_token']
            auth = {'X-Vault-Token': token}
            endpoint = '/'.join([self.safe.vault.url, 'v1/transit/encrypt', self.safe.vault.transit_key_name])
            encoded = base64.b64encode(bytes(self.secret, 'utf-8'))
            request = requests.post(endpoint, headers=auth,
                                    data=json.dumps({'plaintext': encoded.decode('utf-8')}),
                                    verify=settings.PLOS_CA_CERTIFICATE)
            request.raise_for_status()
            ciphertext = request.json()['data']['ciphertext']
            self.secret = ciphertext
        return self.secret

    @property
    def hosts(self):
        """
        returns a list of hosts that have access to this secret
        """
        if self.safe.access_controls['all']:
            if self.safe.vault.all_environments:
                hosts = Host.objects.all()
            else:
                hosts = Host.objects.filter(environment=self.safe.environment)
        else:
            hosts = [host for host in self.safe.access_controls['hosts'] if host.environment == self.safe.environment]
            for role in self.safe.access_controls['roles']:
                for host in role.hosts.filter(environment=self.safe.environment):
                    hosts.append(host)
        return sorted(set(hosts), key=lambda host: host.hostname)

    def save(self, *args, **kwargs):
        """
        Override the default save() method to first call _encrypt_secret() on the
        in-memory representation of the object.
        """
        self._encrypt_secret()
        if re.match(VAULT_REGEX, self.secret):
            super(Secret, self).save(*args, **kwargs)

    def __str__(self):
        return '{} :: {} :: {}'.format(self.name, self.safe.name, self.safe.vault.name)

    class Meta:
        unique_together = (('name', 'safe'),)

