'''Unit tests for flickr-spellchk
'''

import unittest
from mock import Mock
from flickr_spellr import controller
from flickr_spellr.utils import flickr, speller

class TestBasicController(unittest.TestCase):

    def setUp(self):
        self.flickr = Mock(spec=flickr.Flickr)
        self.speller = Mock(spec=speller.Speller)
    
    def tearDown(self):
        self.flickr = None
        self.speller = None
        
    def testNoPhoto(self):
        self.flickr.login.return_value = True
        self.flickr.photos_iter.return_value = iter([])
        ctrl = controller.DumbController(flickr=self.flickr,
                                         speller=self.speller)
        ctrl.run()
        self.flickr.login.assert_called_with()
        assert self.flickr.photos_iter.called, 'Never tried to iter photos'
    
    def testOnePhotoNoErors(self):
        photo = Mock(spec=flickr.SimplePhoto, title='test', description='test')
        self.flickr.login.return_value = True
        self.flickr.photos_iter.return_value = iter([photo])
        self.speller.err_iter.return_value = iter([])
        ctrl = controller.DumbController(flickr=self.flickr,
                                         speller=self.speller)
        ctrl.run()
        assert self.flickr.photos_iter.called, 'Never tried to iter photos'
        assert self.speller.err_iter.called, 'Never tried to spell check'
        assert self.speller.err_iter.call_count == 2, 'Missed checking a field'
    
    def testOnePhotoOneError(self):
        photo = Mock(spec=flickr.SimplePhoto, title='Speling error',
                     description='')
        spelling_error = Mock()
        spelling_error.word = 'Speling'
        spelling_error.wordpos = 0
        spelling_error.suggest.result = ['a', 'word', 'suggestion']
        self.flickr.login.return_value = True
        self.flickr.photos_iter.return_value = iter([photo])
        self.speller.err_iter.return_value = iter([spelling_error]) 
        ctrl = controller.DumbController(flickr=self.flickr,
                                         speller=self.speller)
        ctrl.run()
        assert self.speller.err_iter.called, 'Never tried to spell check'
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()