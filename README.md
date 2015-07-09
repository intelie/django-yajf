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

Development
-----------

    git clone git@github.com:intelie/django-yajf.git
    cd django-yajf
    mkvirtualenv django-yajf
    pip install virtualenv  # Otherwise tox will not be able to run
    python setup.py test
