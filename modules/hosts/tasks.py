import logging

from celery import shared_task

from plop.pdns import zones

from .models import AddressAssignment, Host

logger = logging.getLogger('.'.join(['dewey', __name__]))


def create_dns_record(record_zone, record_key, record_type, record_value):
    logger.info('Attempting to create DNS {} record for {}'.format(record_type, record_key))
    zone = zones.Zone(record_zone)
    if not zone.exists():
        zone.create()
        logger.warning('Created new DNS zone {}; you may need to log in to poweradmin '
                       'and update the details for the zone!'.format(record_zone))
    record = zones.Record(record_zone, record_key, record_type, record_value)
    if record.exists():
        record.update()
        logger.info('Updated DNS {} record for {}'.format(record_type, record_key))
    else:
        record.create()
        logger.info('Created DNS {} record for {}'.format(record_type, record_key))


def delete_dns_record(record_zone, record_key, record_type, record_value):
    logger.info('Attempting to delete DNS {} record {}'.format(record_type, record_key))
    zone = zones.Zone(record_zone)
    if zone.exists():
        record = zones.Record(record_zone, record_key, record_type, record_value)
        if record.exists():
            record.delete()
            logger.info('Deleted DNS {} record {}'.format(record_type, record_key))
        else:
            logger.warning('Record {} does not exist, not deleted'.format(record_key))
    else:
        logger.warning('Zone {} does not exist - cannot delete record {}'.format(record_zone, record_key))


@shared_task(default_retry_delay=60, max_retries=5)
def create_dns_records(assignment):
    host, address = assignment.host, assignment.address
    try:
        # only create A record for "canonical" addresses
        if assignment.canonical:
            create_dns_record(host.domain, host.hostname, 'A', address)
        # create PTR records for all addresses
        create_dns_record(assignment.network.reverse_zone, assignment.ptr_name, 'PTR', host.hostname)
    except Exception as ex:
        logger.error('Error creating DNS records for assignment {}: {}'.format(address, ex))
        raise self.retry(exc=ex)


@shared_task(default_retry_delay=60, max_retries=5)
def delete_dns_records(assignment):
    # this first try/except block is necessary for cascading deletes on Host objects
    try:
        host, address = assignment.host, assignment.address
    except (Host.DoesNotExist, AddressAssignment.DoesNotExist):
        logger.debug('Host or AddressAssignment does not exist!')
        return
    try:
        delete_dns_record(host.domain, host.hostname, 'A', address)
        delete_dns_record(assignment.network.reverse_zone, assignment.ptr_name, 'PTR', host.hostname)
    except Exception as ex:
        logger.error('Error deleting DNS records for assignment {}: {}'.format(address, ex))
        raise self.retry(exc=ex)


@shared_task(default_retry_delay=600, max_retries=5)
def sync_dns_records():
    try:
        for assignment in AddressAssignment.objects.all():
            create_dns_records.delay(assignment)
    except Exception as ex:
        raise self.retry(exc=ex)
