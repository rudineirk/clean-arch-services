from dataclasses import dataclass, field, replace

__all__ = [
    'field',
    'replace',
]


def cls_replace(self, **changes):
    return replace(self, **changes)


cls_replace.__name__ = 'replace'
cls_replace.__qualname__ = 'replace'


def Struct(*args, frozen=True, **kwargs):
    def metaclass(name, bases, namespace):
        if namespace is None:
            namespace = {}

        namespace['replace'] = cls_replace

        cls = type(name, bases, namespace)
        return dataclass(cls, **kwargs)

    if len(args) == 3:
        return metaclass(*args)

    return metaclass
