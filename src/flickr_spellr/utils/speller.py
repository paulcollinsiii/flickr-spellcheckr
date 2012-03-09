'''Model to handle all the spell checking
'''

from enchant.tokenize import HTMLChunker
from enchant.checker import SpellChecker


class Speller(object):
    '''Spell checking at it's finest
    '''
    
    def __init__(self):
        #TODO: Might have to subclass HTMLChunker to support skipping IMG titles
        self._checker = SpellChecker('en_US', chunkers=(HTMLChunker,))
        
    def err_iter(self, phrase):
        '''Yield a callable object with suggest, replace and replace_always
        
        Those methods can be used to replace the erronous word(s) with user
        supplied values
        '''
        self._checker.set_text(phrase)
        for err in self._checker:
            yield err
    
    