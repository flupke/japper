from collections import Counter

from ..models import State
from ..status import Status


def test_state_group_by_host():
    states = [
        State(host='host1', name='foo', status=Status.passing),
        State(host='host1', name='bar', status=Status.passing),
        State(host='host2', name='baz', status=Status.critical),
    ]
    assert State.group_by_host(states) == [
        ('host1', [states[0], states[1]], Counter(passing=2)),
        ('host2', [states[2]], Counter(critical=1)),
    ]
