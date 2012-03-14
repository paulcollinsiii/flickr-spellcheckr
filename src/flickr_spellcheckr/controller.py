'''Manage the spellchecking flow of flickr photos
'''

from cmd import Cmd
import datetime
from flickr_spellcheckr.utils import flickr

class Controller(Cmd):
    '''Simple command processor example.'''

    def __init__(self, speller, flickr, completekey='tab', stdin=None, stdout=None):
        '''
        
        :param flickr: :obj:`~flickr.Flickr` object to handle comm w/ Flickr
        :param speller: :obj:`~speller.Speller` object to handle spellchecking
        '''

        self.flickr = flickr
        self.speller = speller
        self.photos = []
        Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)

    def correct_photos(self, date_from=None, date_to=None):
        '''Return a list of photos with the spelling corrected
        '''

        print >> self.stdout, "Logging into flickr..."
        logged_in = self.flickr.login()
        if callable(logged_in):
            # Not really logged in, must wait then finish login
            raw_input('Press enter when finished authorizing app')
            logged_in()
        print >> self.stdout, "Searching for photos..."
        corrected_photos = []
        for photo in self.flickr.photos_iter(date_from=date_from, date_to=date_to):
            save_photo = False  # Track if we have modified a photo at all
            for key in ('title', 'description'):
                self.speller.set_text(getattr(photo, key))
                for err in self.speller:
                    keep_going, updated = (self
                       ._read_spellchecker_command(err, getattr(photo, key)))
                    if updated:
                        save_photo = True
                        setattr(photo, key, self.speller.get_text())
                    if not keep_going:  # Stop if the user says 'q'
                        break
            if save_photo:
                corrected_photos.append(photo)
        return corrected_photos

    def do_showchanges(self, _ignored):
        for photo in self.photos:
            print photo, '\n'

    def do_savechanges(self, _ignored):
        '''For each photo with spelling corrections go and save the changes
        
        Note that after this finishes saving all the photos meta data the list
        of photos to update will be cleared.
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

        # First find the photos that we need to check
        date_range = []
        try:
            for date in dates.split(' '):  # Split it up so we can a from and to range
                if date == '':
                    continue
                date_range.append(datetime.datetime.strptime(date, '%m/%d/%Y'))
        except ValueError, e:
            print >> self.stdout, e, 'Processing has been aborted'
            return
        # Then call someone else to do the spell checking on each photo
        # and then save that list of corrected photos
        self.photos.extend(self.correct_photos(*date_range))

    def _spellchecker_help(self):
        print >> self.stdout, '\n'.join(("0..N:    replace with the numbered suggestion",
           "R0..rN:  always replace with the numbered suggestion",
           "i:       ignore this wordv",
           "I:       always ignore this word",
           "a:       add word to personal dictionary",
           "e:       edit the word",
           "q:       quit checking",
           "h:       print this help message",
           "----------------------------------------------------"))

    def _read_spellchecker_command(self, error, phrase):
        '''Correct an error
        
        This is a moderatly ugly bit of case switch code in python.
        
        :returns: Tuple of bools (Continue checking, Word Modified)
        '''

        suggs = error.suggest()
        while True:
            print >> self.stdout, "CHECKING: ", phrase
            print >> self.stdout, "ERROR:", error.word
            #TODO: Reformat this so people know it's 0-indexed
            print >> self.stdout, "HOW ABOUT:"
            for idx in xrange(0, len(suggs)):
                print >> self.stdout, '%d) %s' % (idx, suggs[idx])
            cmd = raw_input(">> ")
            cmd = cmd.strip()
            if cmd.isdigit():
                repl = int(cmd)
                if repl >= len(suggs):
                    print >> self.stdout, "No suggestion number", repl
                    continue
                print >> self.stdout, "Replacing '%s' with '%s'" % (error.word, suggs[repl])
                error.replace(suggs[repl])
                return (True, True)
            elif cmd[0] == "R":
                if not cmd[1:].isdigit():
                    print >> self.stdout, "Badly formatted command (try 'help')"
                    continue
                repl = int(cmd[1:])
                if repl >= len(suggs):
                    print >> self.stdout, "No suggestion number", repl
                    continue
                error.replace_always(suggs[repl])
                return (True, True)
            elif cmd == "i":
                return (True, False)
            elif cmd == "I":
                error.ignore_always()
                return (True, False)
            elif cmd == "a":
                error.add()
                return (True, False)
            elif cmd == "e":
                repl = raw_input("New Word: ")
                error.replace(repl.strip())
                #TODO: Check word that's being swapped in
                return (True, True)
            elif cmd == "q":
                return (False, False)
            elif "help".startswith(cmd.lower()):
                self._spellchecker_help()
                continue
            else:
                print >> self.stdout, "Badly formatted command (try 'help')"
                continue

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    from enchant.checker import SpellChecker

    speller = SpellChecker('en_US')
    ctrl = Controller(flickr=flickr.Flickr(),
                      speller=speller)
    ctrl.cmdloop()
