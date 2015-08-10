from collections import namedtuple
from django.utils.functional import SimpleLazyObject


class EnumQuerySet(tuple):
  """
  Implements a subset of Django QuerySet methods appropriate for enumerated types.
  Values must be instances of the same Enum class.  Must not be empty.
  """

  def __init__(self, values):
    super(EnumQuerySet, self).__init__()
    self.model = values[0].__class__ if values else None

  def values_list(self, *fields, **kwargs):
    """
    See Django QuerySet.values_list.
    Can be used to generate choices.
    """
    flat = kwargs.pop('flat', False)
    if kwargs:
      raise TypeError('Unexpected keyword arguments to values_list: %s'
                      % (list(kwargs.keys()),))
    if flat:
      if len(fields) > 1:
        raise TypeError('"flat" is not valid when values_list is called with more than one field.')
      return [getattr(e, fields[0]) for e in self]
    return [
      tuple([getattr(e, field) for field in fields])
      for e in self
    ]

  def value(self, field):
    """
    Returns the value of a single attribute for all instances in this set.
    """
    return [getattr(e, field) for e in self]

  def order_by(self, ordering):
    """
    Returns a sorted EnumQuerySet based on the order of the attribute passed
    """
    if ordering[:1] == '-':
      attr = ordering[1:]
      reverse = True
    else:
      attr = ordering
      reverse = False
    values = sorted(
      self,
      key=lambda e: getattr(e, attr),
      reverse=reverse
    )
    return EnumQuerySet(values)

  def get(self, **kwargs):
    """
    Lookup an enumerated instance by attribute value.
    Accetps a single keyword argument, which must be an index attribute.
    """
    # manager has the indices, delegate lookup
    # TODO: also check that this queryset contains the return object?
    return self.model.objects.get(**kwargs)

  def filter(self, **kwargs):
    """
    Return all EnumQuerySet populated with all enums that match the values passed.
    Currently only pk= and pk__in= expressions are supported.
    """
    result = []
    for enum in self:
      for key, value in list(kwargs.items()):
        parts = key.split('__')
        values = []
        if len(parts) > 1:
          key = ''.join(parts[:-1])
          if parts[-1] == 'in':
            assert (isinstance(value, list) or isinstance(value, set)), \
                'pk__in= filter expression must provide a list, got %s(%s)' % \
                (value, value.__class__.__name__)
            values = value
        else:
          values.append(value)

        for v in values:
          if getattr(enum, key) == v:
            result.append(enum)

    return EnumQuerySet(result)


class EnumManager(EnumQuerySet):
  """
  A la Django model manager.  Keeps track of all the enumerated instances.
  """

  def __new__(cls, values, conf):
    return EnumQuerySet.__new__(cls, values)

  def __init__(self, values, conf):
    super(EnumManager, self).__init__(values)

    # build indicies
    indexedAttributes = getattr(conf, 'index', [])
    indicies = {}
    # realize lazy instances
    for i, value in enumerate(values):
      if isinstance(value, SimpleLazyObject):
        value._setup()
        values[i] = value._wrapped

    for attr in indexedAttributes:
      items = [(getattr(e, attr), e) for e in values]
      indicies[attr] = dict(items)
    self._indicies = indicies
    self._values = values

  def all(self):
    return self._values

  def get(self, **kwargs):
    key, value = list(kwargs.items())[0]
    if key == 'pk':
      key = self.model._pkField
    return self._indicies[key][value]


class EnumMetaclass(type):
  """
  Interpreter for Enumeration declarative mini-language.
  """
  def __new__(cls, name, bases, args):
    conf = args.pop('EnumMeta', None)
    if conf:
      # create a named tuple superclass
      tup = namedtuple(name, conf.attributes)
      bases = (tup,) + bases

    # create the enumeration class
    cls = type.__new__(cls, name, bases, args)

    if conf:
      # transform enumerated values into enum instances
      instances = []
      for key, value in list(args.items()):
        if isinstance(value, Enum.Map):
          instance_cls = value.base if value.base is not None else cls
          instance = _lazy_enum_instance(cls, instance_cls, value.attrs)
          instances.append(instance)
          setattr(cls, key, instance)
        elif not key.startswith('_') and isinstance(value, tuple):
          # meta-recursive constructor!
          # invoke class constructor within the constructor for the class
          instance = cls(*value)
          instances.append(instance)
          setattr(cls, key, instance)
      # attach a manager
      cls.objects = SimpleLazyObject(lambda: EnumManager(instances, conf))
    return cls


def _lazy_enum_instance(enum_cls, instance_cls, args):
  """
  Enum instances which wish to be created from a subclass of the enum must be
  created via a lazy object since the enum instances are created at class
  definition time, but that means that the subclass does not yet exist. So we
  have to delay the actual instance creation until later, when the subclass is
  available.
  """
  def _instance(instance_cls):
    if isinstance(instance_cls, str):
      from dashboard.core.introspection import getClass
      instance_cls = getClass(instance_cls)

    assert issubclass(instance_cls, enum_cls), \
      'Base class must be a subclass of %s' % enum_cls

    return instance_cls(*args)
  return SimpleLazyObject(lambda: _instance(instance_cls))


class Enum(object, metaclass=EnumMetaclass):
  """
  Abstract base class for enumerations.
  """

  class Map(object):
    def __init__(self, base=None, attrs=None):
      self.base = base
      self.attrs = attrs


class StandardMeta:
  index = 'id', 'displayName'
  attributes = 'id', 'displayName'
