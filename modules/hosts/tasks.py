import logging

from celery import shared_task

from plop.pdns import zones

logger = logging.getLogger('.'.join(['dewey', __name__]))


def create_dns_record(record_zone, record_key, record_type, record_value):
    logger.info('Create DNS {} record for {}'.format(record_type, record_key))
    if not record_zone.exists():
        record_zone.create()
        logger.warning('Created new DNS zone {}; you may need to log in to poweradmin and update '
                       'the details for the zone!'.format(record_zone.name))
    record = zones.Record(record_zone, record_key, record_type, record_value)
    if record.exists():
        record.update()
        logger.info('Updated DNS {} record for {}'.format(record_type, record_key))
    else:
        record.create()
        logger.info('Created DNS {} record for {}'.format(record_type, record_key))


def delete_dns_record(record_zone, record_key, record_type, record_value):
    logger.info('Delete DNS {} record {}'.format(record_type, record_key))
    if record_zone.exists():
        record = zones.Record(record_zone, record_key, record_type, record_value)
        if record.exists():
            record.delete()
            logger.info('Deleted DNS {} record {}'.format(record_type, record_key))
        else:
            log.warning('Record {} does not exist, not deleted'.format(record_key))
    else:
        log.warning('Zone {} does not exist - cannot delete record {}'.format(record_zone, record_key))


@shared_task(default_retry_delay=60, max_retries=5)
def create_dns_records(assignment):
    try:
        host, address = assignment.host, assignment.address
        forward_zone = zones.Zone(host.domain)
        create_dns_record(forward_zone, host.hostname, 'A', address)
        reverse_zone = zones.Zone(assignment.network.reverse_zone)
        create_dns_record(reverse_zone, assignment.ptr_name, 'PTR', host.hostname)
    except Exception as ex:
        log.error('Error creating DNS records for assignment {}: {}'.format(address, ex))
        raise create_dns_records.retry(exc=ex)


@shared_task(default_retry_delay=60, max_retries=5)
def delete_dns_records(assignment):
    try:
        host, address = assignment.host, assignment.address
        forward_zone = zones.Zone(host.domain)
        delete_dns_record(forward_zone, host.hostname, 'A', address)
        reverse_zone = zones.Zone(assignment.network.reverse_zone)
        delete_dns_record(reverse_zone, assignment.ptr_name, 'PTR', host.hostname)
    except Exception as ex:
        log.error('Error deleting DNS records for assignment {}: {}'.format(address, ex))
        raise delete_dns_records.retry(exc=ex)
