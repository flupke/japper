from enum import Enum


class Status(Enum):

    passing = 1
    warning = 2
    critical = 3
    unknown = 4
    flapping = 5

    def do_not_call_in_templates(): pass

    @classmethod
    def from_string(cls, value):
        for entry in cls:
            if entry.name == value:
                return entry
        else:
            raise ValueError('invalid enum value name: %s' % value)

    @classmethod
    def problems(cls):
        return (cls.warning, cls.critical, cls.flapping)

    def is_problem(self):
        return self in self.problems()
