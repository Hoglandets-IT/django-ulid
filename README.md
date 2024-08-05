# django-ulid

### Status

This project is actively maintained.
This is a fork from [hassaanalansary/django-ulid](https://github.com/hassaanalansary/django-ulid) that itself is a fork from [ahawker/django-ulid](https://github.com/ahawker/django-ulid) and as such we don't have a proper pip-package yet. For now you will manually need to clone this repo and manually install it to use it. 

### Installation

To install ulid from source:
```bash
    $ git clone git@github.com:Hoglandets-IT/django-ulid.git
    $ cd django-ulid && python setup.py install
```

### Usage

Adding a ULID field to your Django models is straightforward. It can be a normal field or a primary key.

```python
from django.db import models
from django_ulid.models import default, ULIDField

class Person(models.Model):
    id = ULIDField(default=default, primary_key=True, editable=False)
```

Passing in `default` to the `ULIDField` will automatically create a default value using the [ulid.new](https://ulid.readthedocs.io/en/latest/api.html#ulid.api.new) function.
If you do not want a default value, `None` by default, feel free to omit it.

```python
from django.db import models
from django_ulid.models import ULIDField

class Person(models.Model):
    optional_id = ULIDField()
```

Adding a ULID field to your [Django REST Framework](https://www.django-rest-framework.org/) serializers is also straightforward.

Simply importing the `django_ulid.serializers` module will automatically register the `ULIDField` serializer by overriding
the [serializer_field_mapping](https://www.django-rest-framework.org/api-guide/serializers/#customizing-field-mappings) on the default [ModelSerializer](https://www.django-rest-framework.org/api-guide/serializers/#modelserializer).

```python
from django_ulid import serializers
```

If you are using a ULID as a primary key on a model, you need to create a custom [PrimaryKeyRelatedField](https://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield) to automatically serialize
the instance through the foreign key.

```python
import functools
from django_ulid.serializers import ULIDField
from rest_framework import serializers

PersonPrimaryKeyRelatedField = functools.partial(serializers.PrimaryKeyRelatedField,
                                                 allow_null=True,
                                                 allow_empty=True,
                                                 pk_field=ULIDField(),
                                                 queryset=Person.objects.all())

class OrganizationSerializer(serializers.ModelSerializer):
    owner = PersonPrimaryKeyRelatedField()
```

You can use the type `ulid` as a path segment converter in your URLs, similar to the built-in `uuid` converter. It returns a `ULID` instance.

```python
import ulid
from django.urls import path
from django_ulid import path_converter 

def person_view(request, id):
    assert isinstance(id, ulid.ULID)

urlpatterns = [
    path('person/<ulid:id>/', person_view)
]
```

### Contributing

If you would like to contribute, simply fork the repository, push your changes and send a pull request.
Pull requests will be brought into the `master` branch via a rebase and fast-forward merge with the goal of having a linear branch history with no merge commits.

### License

[Apache 2.0](LICENSE)

### Dependencies

* [Django](https://github.com/django/django)
* [ulid-py](https://github.com/ahawker/ulid)
