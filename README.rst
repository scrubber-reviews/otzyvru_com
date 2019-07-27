===========
Otzyvru com
===========


.. image:: https://img.shields.io/pypi/v/otzyvru_com.svg
        :target: https://pypi.python.org/pypi/otzyvru_com

.. image:: https://img.shields.io/travis/NMelis/otzyvru_com.svg
        :target: https://travis-ci.org/NMelis/otzyvru_com

.. image:: https://readthedocs.org/projects/otzyvru-com/badge/?version=latest
        :target: https://otzyvru-com.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Scrabb reviews


* Free software: MIT license
* Documentation: https://otzyvru-com.readthedocs.io.


### Get comments
```python
from otzyvru_com import scrubber

provider = scrubber('roskomnadzor') # url slug with https://www.otzyvru.com site

provider.start()  # wait...

provider.comments # List<comment>

```

### Comments structure
```
Rating:
    average_rating: float
    on_scale: int

Author:
    name: str

Comment:
    id: int
    title: str,
    text: str,
    date: str(YYYY-M-D)
    rating: Rating
    author: Author
    advantages: list<str>
    disadvantages: list<str>
    sub_comments: list<Comment>
    plus: int
    minus: int

```

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
