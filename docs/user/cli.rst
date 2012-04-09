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
the present.

Dates are expected to be in the MM/DD/YYYY format

spellchecktags
--------------
``spellchecktags`` gets the full list of tags and then outputs the list of
corrections to the screen. Due to the way the Flickr API works, you will need
to manually go to Flickr and change the tags through their web interface.

savechanges
-----------
``savechanges`` takes all the spelling changes from ``spellcheck`` and commits
them to Flickr.

showchanges
-----------
``showchanges`` shows all the spelling changes that would be saved to Flickr
from a ``savechanges``