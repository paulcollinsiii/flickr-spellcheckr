Command Line Interface
======================

The command line interface is broken into two segments. Spell checking and
saving.

spellcheck
----------
``spellcheck [date_from] [date_to]`` checks photos whose data `taken` are
between ``date_from`` and ``date_to``. This is different from flickr's tracking
of the date uploaded.

If ``date_to`` is left blank, then it checks everything to the present.
If ``date_from`` is left blank, then it checks everything from 40 days ago to
the present