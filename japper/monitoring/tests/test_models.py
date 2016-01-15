from collections import Counter
import datetime

from ..models import State
from ..status import Status


def test_state_group_by_host():
    now = datetime.datetime.now()
    one_day = datetime.timedelta(days=1)

    states = [
        State(host='host1', name='foo', status=Status.passing),
        State(host='host1', name='bar', status=Status.passing),
        State(host='host2', name='baz', status=Status.critical),
        State(host='host3', name='fizz', status=Status.critical,
              last_status_change=now),
        State(host='host3', name='buzz', status=Status.warning,
              last_status_change=now - one_day),
        State(host='host3', name='wizz', status=Status.passing,
              last_status_change=now - one_day * 2),
    ]

    assert State.group_by_host(states) == [
        (
            'host1',
            [states[0], states[1]],
            Counter(passing=2),
            None,
            True,
            False
        ),
        (
            'host2',
            [states[2]],
            Counter(critical=1),
            None,
            True,
            True
        ),
        (
            'host3',
            [states[3], states[4], states[5]],
            Counter(critical=1, warning=1, passing=1),
            states[4].last_status_change,
            True,
            True
        ),
    ]
