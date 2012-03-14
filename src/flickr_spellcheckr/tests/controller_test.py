'''Unit tests for mock_flickr-spellchk
'''

import unittest
import mock
from flickr_spellcheckr import controller
from flickr_spellcheckr.utils import flickr
from enchant.checker import SpellChecker

class TestBasicController(unittest.TestCase):

    def setUp(self):
        self.mock_flickr = mock.Mock(spec=flickr.Flickr)
        self.mock_speller = mock.MagicMock(spec=SpellChecker)

    def tearDown(self):
        self.mock_flickr = None
        self.mock_speller = None


    def testNoPhoto(self):
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([])
        ctrl = controller.Controller(flickr=self.mock_flickr,
                                     speller=self.mock_speller)
        ctrl.do_spellcheck('')
        self.mock_flickr.login.assert_called_with()
        assert self.mock_flickr.photos_iter.called, 'Never tried to iter photos'

    def testOnePhotoNoErors(self):
        photo = mock.Mock(spec=flickr.SimplePhoto, title='test', description='test')
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([photo])
        self.mock_speller.return_value = iter([])
        ctrl = controller.Controller(flickr=self.mock_flickr,
                                     speller=self.mock_speller)
        ctrl.do_spellcheck('')
        assert self.mock_speller.__iter__.call_count == 2, 'Missed checking a field'


class TestBasicSpelling(unittest.TestCase):

    def setUp(self):
        self.mock_flickr = mock.Mock(spec=flickr.Flickr)
        self.mock_speller = mock.MagicMock(spec=SpellChecker)
        self.real_speller = SpellChecker('en_US')

    def tearDown(self):
        self.mock_flickr = None
        self.mock_speller = None

    def onePhotoTwoErrorSetup(self):
        photo = mock.Mock(spec=flickr.SimplePhoto, title='Speling eror',
                     description='')
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([photo])
        return photo

    def testOnePhotoTwoeErrorIgnored(self):
        photo = self.onePhotoTwoErrorSetup()
        orig_text = photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'i'
            ctrl.do_spellcheck('')
        self.assertEqual(orig_text, photo.title)

    def testOnePhotoTwoErrorQuit(self):
        photo = mock.Mock(spec=flickr.SimplePhoto,
                          title='Speling eror abound in ths',
                          description='')
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([photo])
        orig_text = photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['q']
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertEqual(orig_text, photo.title)
        # No changes means no updates pending
        self.assertEqual(len(ctrl.photos), 0)

    def testOnePhotoTwoErrorOneReplaced(self):
        photo = self.onePhotoTwoErrorSetup()
        orig_text = photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['1', 'i']
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertNotEqual(orig_text, photo.title)
        self.assertEqual('Spelling eror', photo.title)

    def testOnePhotoTwoErrorTwoReplaced(self):
        photo = self.onePhotoTwoErrorSetup()
        orig_text = photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = '1'
            ctrl.do_spellcheck('')
        self.assertNotEqual(orig_text, photo.title)
        self.assertEqual('Spelling error', photo.title)

class TestBasicSaving(unittest.TestCase):

    def setUp(self):
        self.mock_flickr = mock.Mock(spec=flickr.Flickr)
        self.mock_speller = mock.NonCallableMagicMock()
        self.ctrl = controller.Controller(flickr=self.mock_flickr,
                                          speller=self.mock_speller)

    def testNoPhoto(self):
        self.ctrl.do_savechanges('')
        self.assertEqual(len(self.mock_flickr.method_calls), 0)

    def testOnePhoto(self):
        self.ctrl.photos = [mock.Mock(spec=flickr.SimplePhoto)]
        self.ctrl.do_savechanges('')
        self.assertEqual(len(self.mock_flickr.method_calls), 1)

    def testClearList(self):
        self.ctrl.photos = [mock.Mock(spec=flickr.SimplePhoto)]
        self.ctrl.do_savechanges('')
        self.assertEqual(len(self.ctrl.photos), 0)


if __name__ == "__main__":
    unittest.main()
