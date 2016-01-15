from django.conf import settings
from django.core.cache import cache
from boto import ec2


def search_public_dns(private_dns, aws_region, aws_access_key_id,
                      aws_secret_access_key):
    '''
    Retrieve the public DNS name of an EC2 instance from its private DNS name.

    Return the public DNS name, or None if it can't be found for these AWS
    credentials.
    '''
    # Multiple threads/processes might call this function at the same time, we
    # use a distributed lock here to avoir querying the ec2 API more than once
    with cache.lock('japper:search_ec2_public_dns',
                    expire=settings.EC2_DNS_LOCK_EXPIRE):
        # Look in cache
        host_cache_key = _get_cache_key(aws_region, private_dns)
        resolved_host = cache.get(host_cache_key)
        # Update cache if host is not in it
        if resolved_host is None:
            _update_ec2_names_cache(aws_region, aws_access_key_id,
                                    aws_secret_access_key)
        # Search again in cache
        resolved_host = cache.get(host_cache_key)
        if resolved_host is not None:
            return resolved_host


def _update_ec2_names_cache(aws_region, aws_access_key_id,
                            aws_secret_access_key):
    conn = _get_ec2_connection(aws_region, aws_access_key_id,
                               aws_secret_access_key)
    for instance in conn.get_only_instances():
        if not instance.dns_name or not instance.private_dns_name:
            continue
        cache_key = _get_cache_key(aws_region, instance.private_dns_name)
        cache.set(cache_key, instance.dns_name,
                  settings.EC2_DNS_NAMES_CACHE_TTL)


def _get_ec2_connection(aws_region, aws_access_key_id, aws_secret_access_key):
    return ec2.connect_to_region(
        aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


def _get_cache_key(aws_region, private_dns):
    return 'japper:%s:%s' % (aws_region, private_dns)
