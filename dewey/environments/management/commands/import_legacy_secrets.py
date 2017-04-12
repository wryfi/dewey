import gnupg
import os
import re
import yaml

from django.core.management.base import BaseCommand, CommandError

from dewey.core.utils.dotutils import flatten_dict
from dewey.environments.models import Environment, Host, Role, Safe, SafeAccessControl, Secret, Vault


try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except:
    pass


class Command(BaseCommand):
    help = 'imports legacy secrets from PLOS secrets repos'

    def add_arguments(self, parser):
        parser.add_argument('--directory', '-d', help='directory from which to import export', required=True)
        parser.add_argument('--environment', '-e', help='environment (prod, dev, etc)', required=True)

    def handle(self, *args, **options):
        self.directory = options['directory']
        self.environment = Environment.objects.get(name=options['environment'])
        self.vault = Vault.objects.filter(environment=self.environment).first()
        if not self.vault:
            raise RuntimeError('no vaults defined for {}'.format(self.environment))
        self.gpg = gnupg.GPG(use_agent=True)
        self.import_host_secrets()
        self.import_shared_secrets()

    def import_host_secrets(self):
        host_secrets_dir = os.path.join(self.directory, 'secrets', 'host')
        for secrets_file in os.listdir(host_secrets_dir):
            hostname = '.'.join(secrets_file.split('.')[:-1])
            try:
                secret_host = Host.objects.get(hostname=hostname)
                safe = Safe.objects.create(name='imported secrets for {}'.format(secret_host.hostname), vault=self.vault)
                secrets_yaml = self.read_secrets_file(os.path.join(host_secrets_dir, secrets_file))
                flattened = flatten_dict(secrets_yaml)
                for key, value in flattened.items():
                    Secret.objects.create(name=key, secret=value, safe=safe)
                SafeAccessControl.objects.create(safe=safe, acl_object=secret_host)
            except Host.DoesNotExist:
                self.stdout.write('WARNING! host {} does not exist (in file {})'.format(hostname, secrets_file))

    def import_shared_secrets(self):
        shared_secrets_dir = os.path.join(self.directory, 'secrets', 'shared')
        for secrets_file in os.listdir(shared_secrets_dir):
            safe = Safe.objects.create(name='shared secrets imported from {}'.format(secrets_file), vault=self.vault)
            secrets_yaml = self.read_secrets_file(os.path.join(shared_secrets_dir, secrets_file))
            flattened = flatten_dict(secrets_yaml['secrets'])
            for key, value in flattened.items():
                Secret.objects.create(name=key, secret=value, safe=safe)
            if 'roles' in secrets_yaml.keys():
                if type(secrets_yaml['roles']) != list:
                    secrets_yaml['roles'] = [secrets_yaml['roles']]
                for role in secrets_yaml['roles']:
                    if re.match(r'^[A-Za-z._-]+$', role):
                        role, created = Role.objects.get_or_create(name=role)
                        if created:
                            self.stdout.write('created role {}'.format(role.name))
                        SafeAccessControl.objects.create(safe=safe, acl_object=role)
                    else:
                        self.stdout.write('WARNING! unsupported role regex: {} (in file {})'.format(role, secrets_file))
            if 'hosts' in secrets_yaml.keys():
                for host in secrets_yaml['hosts']:
                    if re.match(r'^[A-Za-z._-]+$', host):
                        try:
                            SafeAccessControl.objects.create(safe=safe, acl_object=Host.objects.get(hostname=host))
                        except Host.DoesNotExist:
                            self.stdout.write(
                                ('WARNING! host {} does not exist, '
                                'cannot create host ACL for safe {} (in file {})').format(
                                    host, safe.name, secrets_file
                                )
                            )
                    else:
                        self.stdout.write('WARNING! unsupported host regex: {} (in file {})'.format(host, secrets_file))

    def read_secrets_file(self, path):
        if path.endswith('.gpg'):
            with open(path, 'rb') as openfile:
                gpgdata = self.gpg.decrypt_file(openfile)
            if gpgdata.ok:
                return yaml.load(gpgdata.data)
        elif path.endswith('.yml'):
            with open(path) as openfile:
                return yaml.load(openfile.read())
