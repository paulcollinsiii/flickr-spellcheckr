'''Manage the spellchecking flow of flickr photos
'''
import datetime
from flickr_spellr.utils import flickr, speller


class DumbController(object):
    '''Controller to query flickr, do the spell checks and then push updates
    
    DumbController just grabs the photos that were taken in the last 40 days
    and spellchecks those for you. It's the MOST basic of them with no
    updating
    '''


    def __init__(self, flickr, speller):
        '''
        
        :param flickr: :obj:`~flickr.Flickr` object to handle comm w/ Flickr
        :param speller: :obj:`~speller.Speller` object to handle spellchecking
        '''
        
        self.flickr = flickr
        self.speller = speller
    
    def run(self):
        logged_in = self.flickr.login()
        if callable(logged_in):
            # Not really logged in, must wait then finish login
            raw_input('Press enter when finished authorizing app')
            logged_in()
        # Get an iterator for photos based on search params
        for photo in self.flickr.photos_iter(date_from=
                     datetime.datetime.utcnow() - datetime.timedelta(days=40)):
            errors = []
            for key in ('title', 'description'):
                for err in self.speller.err_iter(getattr(photo, key)):
                    errors.append(err)
            if errors:  # if len of errors != 0
                err_words = map(lambda err: err.word, errors)
                print '''Photo: "{0.title}" has the following spelling errors:
{1}'''.format(photo, err_words)

if __name__ == '__main__':
    ctrl = DumbController(flickr=flickr.Flickr(),
                          speller=speller.Speller())
    ctrl.run()
