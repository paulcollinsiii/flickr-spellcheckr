# -*- coding: UTF-8 -*-

'''Unit tests for mock_flickr-spellchk
'''

from enchant.checker import SpellChecker
from flickr_spellcheckr import controller
from flickr_spellcheckr.utils import flickr
import enchant
import mock
import unittest


class TestBasicController(unittest.TestCase):

    def setUp(self):
        self.mock_flickr = mock.Mock(spec=flickr.Flickr)
        self.mock_speller = mock.MagicMock(spec=SpellChecker)

    def tearDown(self):
        self.mock_flickr = None
        self.mock_speller = None

    def test_no_photo(self):
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([])
        ctrl = controller.Controller(flickr=self.mock_flickr,
                                     speller=self.mock_speller)
        ctrl.do_spellcheck('')
        self.mock_flickr.login.assert_called_with()
        assert self.mock_flickr.photos_iter.called, 'Never iterated photos'

    def test_one_photo_no_errors(self):
        photo = mock.Mock(spec=flickr.SimplePhoto, title='test',
                          description='test')
        self.mock_flickr.login.return_value = True
        self.mock_flickr.photos_iter.return_value = iter([photo])
        self.mock_speller.return_value = iter([])
        ctrl = controller.Controller(flickr=self.mock_flickr,
                                     speller=self.mock_speller)
        ctrl.do_spellcheck('')
        self.assertEqual(self.mock_speller.__iter__.call_count, 2,
                         'Failed to check all fields')


class TestBasicSpelling(unittest.TestCase):

    def setUp(self):
        self.mock_flickr = mock.Mock(spec=flickr.Flickr)
        self.mock_flickr.login.return_value = True
        self.mock_speller = mock.MagicMock(spec=SpellChecker)
        self.real_speller = SpellChecker(lang=enchant.DictWithPWL("en_US"))
        self.photo = mock.Mock(spec=flickr.SimplePhoto, title='Speling eror',
                     description=None)
        self.mock_flickr.photos_iter.return_value = iter([self.photo])

    def tearDown(self):
        self.mock_flickr = None
        self.mock_speller = None
        self.photo = None

    def test_errors_ignored(self):
        orig_text = self.photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'i'
            ctrl.do_spellcheck('')
        self.assertEqual(orig_text, self.photo.title)

    def test_quit_has_no_text_change(self):
        orig_text = self.photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['q']
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertEqual(orig_text, self.photo.title)

    def test_quit_has_empty_save_queue(self):
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['q']
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertEqual(len(ctrl.photos), 0)

    def test_edit_error_output(self):
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['e', 'Spellingg', 'i', ]
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertEqual('Spellingg eror', self.photo.title)

    def test_replace_one(self):
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            results = ['1', 'i']
            mockraw.side_effect = lambda *args: results.pop(0)
            ctrl.do_spellcheck('')
        self.assertEqual('Spelling eror', self.photo.title)

    def test_replace_both(self):
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = '1'
            ctrl.do_spellcheck('')
        self.assertEqual('Spelling error', self.photo.title)

    def test_replace_always(self):
        self.photo = mock.Mock(spec=flickr.SimplePhoto,
                   title='speling errors means speling failures',
                   description='')
        self.mock_flickr.photos_iter.return_value = iter([self.photo])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'R1'
            ctrl.do_spellcheck('')
        self.assertEqual('spelling errors means spelling failures',
                         self.photo.title)

    def test_add_to_personal_dict_callcount(self):
        self.photo = mock.Mock(spec=flickr.SimplePhoto,
                   title='speling errors means speling failures',
                   description='')
        self.mock_flickr.photos_iter.return_value = iter([self.photo])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'a'
            ctrl.do_spellcheck('')
            self.assertEqual(mockraw.call_count, 1, 'Too many adds')

    def test_add_to_personal_dict_text(self):
        self.photo = mock.Mock(spec=flickr.SimplePhoto,
                   title='speling errors means speling failures',
                   description='')
        self.mock_flickr.photos_iter.return_value = iter([self.photo])
        orig_text = self.photo.title[:]
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'a'
            ctrl.do_spellcheck('')
        self.assertEqual(orig_text, self.photo.title)

    def test_spellcheck_tag_text(self):
        self.mock_flickr.tag_list.return_value = iter(['good', 'badspell'])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'i'
            ctrl.do_spellchecktags('')
            self.assertEqual(mockraw.call_count, 1, 'Too many adds')

    def test_spellcheck_tag_text_updates(self):
        self.mock_flickr.tag_list.return_value = iter(['good', 'badspell'])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'i'
            ctrl.do_spellchecktags('')
            self.assertEqual(mockraw.call_count, 1, 'Too many adds')

    def test_spellcheck_tag_text_check_ignored_list(self):
        self.mock_flickr.tag_list.return_value = iter(['good', 'badspell'])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = 'i'
            to_update = ctrl.do_spellchecktags('')
            self.assertEqual([], to_update, 'Ignored errors in list')

    def test_spellcheck_tag_text_check_replaced_list(self):
        self.mock_flickr.tag_list.return_value = iter(['good', 'badspell'])
        with mock.patch('__builtin__.raw_input') as mockraw:
            ctrl = controller.Controller(flickr=self.mock_flickr,
                                         speller=self.real_speller)
            mockraw.return_value = '0'
            to_update = ctrl.do_spellchecktags('')
            self.assertEqual([('badspell', 'bad spell')], to_update,
                             'Ignored errors in list')


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
