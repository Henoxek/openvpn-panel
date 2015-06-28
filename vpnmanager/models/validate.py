import re


class ArgumentValidationException(Exception):
    pass


class RegexValidator(object):

    def __init__(self, rules):
        self.rules = rules

    def validate(self, obj):
        result = {}
        for k, v in obj.iteritems():
            if k not in self.rules:
                raise ArgumentValidationException('Unknown field "%s"' % k)
            if self.rules[k] is None:
                result[k] = v
            if re.match(self.rules[k], v) is None:
                raise ArgumentValidationException('Invalid value for %s: %s' % (k, v))
        return result
