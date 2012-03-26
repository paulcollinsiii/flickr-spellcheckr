# -*- coding: UTF-8 -*-

'''
flickr_spellcheckr.controller
=============================

Manage the spellchecking flow of flickr photos. The first version of this is
a fairly basic command line interface.
'''

from cmd import Cmd
from flickr_spellcheckr.utils import flickr
import datetime
import sys
import os


class Controller(Cmd):

    def __init__(self, speller, flickr, completekey='tab', stdin=None,
                 stdout=None):
        '''Simple command line processor of the flickr spell checker.

        :param flickr: :obj:`~flickr_spellchecker.utils.flickr.Flickr` object
            to handle comm w/ Flickr
        :param speller: :obj:`~enchant.checker.SpellChecker` object to handle
            spellchecking
        '''

        self.flickr = flickr
        self.speller = speller
        self.photos = []
        Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)

    def correct_photos(self, date_from=None, date_to=None):
        '''Return a list of photos with the spelling corrected

        :keyword date_from: The :obj:`datetime.datetime` to search from
        :keyword date_to: The :obj:`datetime.datetime` to search to
        :returns: List of :obj:`~flickr_spellchecker.utils.flickr.SimplePhoto`
            objects that have been edited
        '''

        print >> self.stdout, "Logging into flickr..."
        logged_in = self.flickr.login()
        if callable(logged_in):
            # Not really logged in, must wait then finish login
            raw_input('Press enter when finished authorizing app')
            logged_in()
        print >> self.stdout, "Searching for photos..."
        corrected_photos = []
        for photo in self.flickr.photos_iter(date_from=date_from,
                                             date_to=date_to):
            save_photo = False  # Track if we have modified a photo at all
            for key in ('title', 'description'):
                # pyenchant doesn't like having set_text(None) called...
                if getattr(photo, key) is None:
                    continue
                self.speller.set_text(getattr(photo, key))
                for err in self.speller:
                    keep_going, updated = (self
                       ._read_spellchecker_command(err, getattr(photo, key)))
                    save_photo |= updated  # Binary or with updated (save true)
                    if not keep_going:  # Stop if the user says 'q'
                        break
                # Save the updated text from this key after checking for errors
                if save_photo:
                    setattr(photo, key, self.speller.get_text())
            # Only append the photo to the corrected_photos queue once
            if save_photo:
                corrected_photos.append(photo)
        return corrected_photos

    def do_showchanges(self, _ignored):
        '''Show the list of photos that need to be saved to Flickr
        '''

        for photo in self.photos:
            print photo, '\n'

    def do_savechanges(self, _ignored):
        '''For each photo with spelling corrections go and save the changes

        Note that after this finishes saving all the photos, the list of photos
        to update will be cleared.
        '''

        for photo in self.photos:
            self.flickr.save_meta(photo)
        self.photos = []

    def do_spellcheck(self, dates):
        '''spellcheck [date from] [date to]

        Search your photostream for photos TAKEN (not posted) between the
        given dates. If left blank the defaults are from 40 days ago to the
        present.

        Dates need to be in the format MM/DD/YYYY e.g. 01/14/2012
        '''

        # 1) First find the photos that we need to check
        date_range = []
        try:
            for date in dates.split(' '):  # Try to get a from and to range
                if date == '':
                    continue
                date_range.append(datetime.datetime.strptime(date, '%m/%d/%Y'))
        except ValueError, e:
            print >> self.stdout, e, 'Processing has been aborted'
            return
        # 2) Then call someone else to do the spell checking on each photo
        # and then save that list of corrected photos
        self.photos.extend(self.correct_photos(*date_range))

    def _spellchecker_help(self):
        '''Just prints out the help text for using the spelling corrector
        '''

        print >> self.stdout, '\n'.join((
           "0..N:    replace with the numbered suggestion",
           "R0..rN:  always replace with the numbered suggestion",
           "i:       ignore this wordv",
           "I:       always ignore this word",
           "a:       add word to personal dictionary (only for this session)",
           "e:       edit the word",
           "q:       quit checking",
           "h:       print this help message",
           "----------------------------------------------------"))

    def _read_spellchecker_command(self, error, phrase):
        '''Correct an error

        This is a moderately ugly bit of case switch code in python.

        :returns: Tuple of bools (Continue checking, Word Modified)
        '''

        suggs = error.suggest()
        while True:
            print >> self.stdout, "CHECKING: ", phrase
            print >> self.stdout, "ERROR:", error.word
            print >> self.stdout, "HOW ABOUT:"
            # Replace the word one time with the selected index
            for idx in xrange(0, len(suggs)):
                print >> self.stdout, '%d) %s' % (idx, suggs[idx])
            cmd = raw_input(">> ")
            cmd = cmd.strip()
            if cmd.isdigit():
                repl = int(cmd)
                if repl >= len(suggs):
                    print >> self.stdout, "No suggestion number", repl
                    continue
                print >> self.stdout, "Replacing '%s' with '%s'" % (
                                                    error.word, suggs[repl])
                error.replace(suggs[repl])
                return (True, True)
            # ALWAYS replace the word with the selected index
            elif cmd[0] == "R":
                if not cmd[1:].isdigit():
                    print >> self.stdout, ("Badly formatted command "
                                           "(try 'help')")
                    continue
                repl = int(cmd[1:])
                if repl >= len(suggs):
                    print >> self.stdout, "No suggestion number", repl
                    continue
                error.replace_always(suggs[repl])
                return (True, True)
            # Ignore this word
            elif cmd == "i":
                return (True, False)
            # ALWAYS ignore this word
            elif cmd == "I":
                error.ignore_always()
                return (True, False)
            # Add the word to the dictionary
            elif cmd == "a":
                error.add()
                return (True, False)
            # Edit the word directly
            elif cmd == "e":
                repl = raw_input("New Word: ")
                error.replace(repl.strip())
                #TODO: Check word that's being swapped in
                return (True, True)
            # Quit checking this field in this photo
            elif cmd == "q":
                return (False, False)
            # Output the help docs
            elif "help".startswith(cmd.lower()):
                self._spellchecker_help()
                continue
            # Invalid command
            else:
                print >> self.stdout, "Badly formatted command (try 'help')"
                continue

    def do_EOF(self, line):
        return True


def get_local_settings():
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'flickr-spellcheckr.dat')
    return os.path.join(os.path.expanduser("~"), '.flickr-spellcheckr')


def main():
    import enchant
    from enchant.checker import SpellChecker

    speller = SpellChecker(lang=enchant.DictWithPWL("en_US",
                                                    pwl=get_local_settings()))
    ctrl = Controller(flickr=flickr.Flickr(), speller=speller)
    ctrl.cmdloop()

if __name__ == '__main__':
    main()
