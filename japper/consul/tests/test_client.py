from ..client import parse_nagios_output


def test_parse_nagios_output():
    assert parse_nagios_output("OK - user: 3.29, nice: 0.50, sys: 0.91, iowait: 0.50, irq: 0.50, softirq: 0.50 idle: 97.28 | 'user'=3.29 'nice'=0.50 'sys'=0.91 'softirq'=0.50 'iowait'=0.50 'irq'=0.50 'idle'=97.28\ ") == \
            ('OK - user: 3.29, nice: 0.50, sys: 0.91, iowait: 0.50, irq: 0.50, softirq: 0.50 idle: 97.28', {'user': 3.29, 'nice': 0.5, 'sys': 0.91, 'softirq': 0.5, 'iowait': 0.5, 'irq': 0.5, 'idle': 97.28})
    assert parse_nagios_output("DISK OK| /=10691MB;19996;20006;0;20016 /dev=0MB;7490;7500;0;7510 /mnt=1380MB;65485;65495;0;65505\ ") == \
            ('DISK OK', {'/': '10691MB', '/dev': '0MB', '/mnt': '1380MB'})
    assert parse_nagios_output('Agent not live or unreachable') == \
            ('Agent not live or unreachable', {})
    assert parse_nagios_output("SLOTS OK | 'gpu'=1 'gevent'=8 'cpu'=8") == \
            ('SLOTS OK', {'gpu': 1, 'gevent': 8, 'cpu': 8})
