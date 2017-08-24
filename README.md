Django-YAJF, Yet Another JSONField
==================================

Another JSONField? Here's why
-----------------------------

Because most implementations don't allow you to use
any kind of JSON-compatible object (like numbers, for example):

    # In some implementations you can see this:

    >>> obj.value = 2.02
    2.02  # this is fine... in some implementations

    >>> obj.value = '2.02'
    2.02  # WAT

    >>> obj.value = {'foo': 'bar'}
    {'foo': 'bar'}  # This is fine
    >>> obj.value = 'Foobar'
    # BOOM! Exception; if it's a string, the field
    # expects it to be a json-dumped object, so
    >>> obj.value = '"Foobar"'
    # this works =S

The goal was to allow any JSON-valid object to be accepted
by the field. This has some problems because since Django<1.8
there's only `to_python` as a method to convert strings to
objects, so we can't usually tell the difference of
`to_python('2.02')` as from retrieved from db or an user
attribution, and this is important as they have different
behaviors.

Right now we're inspecting the call stack to check
if the value was retrieved from a db, and *only in that
case* it'll be converted to Python (`json.loads`, you know).
Anything else will store the value in the object as-is.
Actually, **if you're using Django 1.8**, we won't hack
anything because this version calls a specific method
to convert all values fetched from the database.


How to install and use
----------------------

    $ pip install django-yajf

    # models.py
    from yajf import JSONField

    class MyModel(models.Model):
        value = JSONField()

    # You can override the json module used (for `loads` and `dumps`),
    # it is useful if you want a different (maybe faster?) json module.
    # It defaults to `import json`.
    JSONField(json=another_json_module)

    # You can also pass `load_kwargs` and `dump_kwargs`,
    # they'll be passed around between conversions, like
    # `json.loads(val, **self.load_kwargs)`:
    JSONField(load_kwargs={'cls': MyDecoder}, dump_kwargs={'cls': MyEncoder})


DecimalJSONField
----------------

Be default `JSONField` will dump any Decimal to a string before serializing,
and it does so in order to not lose precision, but it still loads as a float.
There's another field, `DecimalJSONField`, which loads any float-like value as
a Decimal directly:

    from decimal import Decimal
    from yajf import DecimalJSONField

    class MyModel(models.Model):
        value = DecimalJSONField()

    obj = MyModel()
    obj.value = Decimal(0.1 + 0.2)  # will serialize and de-serialize as Decimal(0.3)

Internally `DecimalJSONField` is just a simple `JSONField` with a predefined
`load_kwargs`, so this is the exact implementation:

    class DecimalJSONField(JSONField):
        LOAD_KWARGS = {
            'parse_float': lambda x: Decimal(x)
        }


Using *dumps* and *loads* directly from the field
-------------------------------------------------

Both of our field classes have two classmethods, `dumps` and `loads` that
will call the related methos on the json module using the default arguments,
so for example:

    dumped = DecimalJSONField.dumps(Decimal(0.1 + 0.2))

    # Is the same as calling:
    dumped = json.dumps(Decimal(0.1 + 0.2), **DecimalJSONField.DUMP_KWARGS)

    # actually, it's the same as:
    dumped = DecimalJSONField.JSON_MODULE.dumps(Decimal(0.1 + 0.2), **DecimalJSONField.DUMP_KWARGS)
    # but remember, `DecimalJSONField.JSON_MODULE = json` by default

If you by any chance use a custom json module, you can call the methods with `**kwargs`
and they'll ignore the default arguments:

    dumped = DecimalJSONField.dumps(Decimal(0.1 + 0.2), foo="bar")

    # is the same as
    dumped = DecimalJSONField.JSON_MODULE.dumps(Decimal(0.1 + 0.2), foo="bar")
    

Development
-----------

    $ git clone git@github.com:intelie/django-yajf.git
    $ cd django-yajf
    $ mkvirtualenv django-yajf
    $ pip install virtualenv  # Otherwise tox will not be able to run
    $ python setup.py test
