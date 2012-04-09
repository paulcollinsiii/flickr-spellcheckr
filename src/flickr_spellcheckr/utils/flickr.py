# -*- coding: UTF-8 -*-

'''
flickr_spellcheckr.utils.flickr
===============================

Module to handle all the query nastiness and pagination with flickr
'''

import datetime
import flickrapi
import time

APIKEY = 'b60fd0ba95f8c583d8ef513d060c68e8'
APISECRET = '9479730e8bc2c49a'


class SimplePhoto(object):
    def __init__(self, title, description, photo_id):
        '''Easier to deal with Photo object from flickr

        :param title: Text of the photo title
        :param description: Text for the description
        :param photo_id: The photo ID
        '''

        self.title = title
        self.description = description
        self.photo_id = photo_id

    def __unicode__(self):
        return u'Title: %(title)s\nDescription: %(description)s' % (
                                                            self.__dict__)

    def __str__(self):
        return 'Title: %(title)s\nDescription: %(description)s' % self.__dict__


class Flickr(object):
    def __init__(self):
        '''Handle querying and iterating over resultant photo data

        :ivar logged_in: Boolean for if we're logged into flickr
        :ivar _flickr: Instance of :obj:`flickrapi`
        '''

        self.logged_in = False
        self._flickr = flickrapi.FlickrAPI(APIKEY, APISECRET, cache=True)

    def login(self):
        '''Setup the :attr:`flickr` object and perform the login to flickr

        It is safe to call this function several times. Subsequent calls have
        no effect.

        :keyword get_token: If get_token_part_one succeeds, get the frob
        :return: True if fully logged in callable to finish login otherwise
        '''

        def finish_login():
            self._flickr.get_token_part_two((token, frob))
            self.logged_in = True
            return True
        if self.logged_in:
            return True
        (token, frob) = self._flickr.get_token_part_one(perms='write')
        if not token:
            return finish_login
        finish_login()

    def photos_iter(self, date_from=None, date_to=None):
        '''Return an iterator over flickr photos and handle all pagination

        The search will only return photos owned by the logged in user.
        The photos objects returned will have their description attached.

        :param date_from: The min date the photo was taken on
        :keyword date_to: The max date the photo was taken on. Default: now
        '''

        def get_photos_element(resp):
            photos = resp.getchildren()
            if len(photos) != 1:
                raise ValueError('Flickr XML response in unexpected format')
            photos = photos[0]
            for key in ('page', 'pages', 'total'):
                if key not in photos.attrib:
                    raise ValueError('Flickr XML response in unexpected '
                                       'format')
            return photos

        def simplephoto_iter(photos):
            for photo in photos.getchildren():
                for key in ('title', 'id'):
                    if key not in photo.attrib:
                        raise ValueError('Flickr XML response in unexpected '
                                           'format')
                children = photo.getchildren()
                if len(children) != 1:
                    raise ValueError('Flickr XML response in unexpected '
                                       'format')
                yield SimplePhoto(title=photo.attrib['title'],
                                  description=children[0].text,
                                  photo_id=photo.attrib['id'])
        if date_from is None:
            date_from = (datetime.datetime.utcnow()
                         - datetime.timedelta(days=40))
        assert self.logged_in, 'Must be logged in to flickr to search photos'
        search_args = {'min_taken_date': time.mktime(date_from.timetuple()),
                       'user_id': 'me',
                       'extras': 'description'}
        if date_to is not None:
            search_args['max_taken_date'] = time.mktime(date_to.timetuple())
        resp = self._flickr.photos_search(**search_args)
        photos = get_photos_element(resp)
        for simplephoto in simplephoto_iter(photos):
            yield simplephoto
        if photos.attrib['pages'] != '1':
            for idx in xrange(2, int(photos.attrib['pages']) + 1):
                resp = self._flickr.photos_search(page=idx, **search_args)
                for simplephoto in simplephoto_iter(get_photos_element(resp)):
                    yield simplephoto

    def save_meta(self, photo):
        '''Save the title and description fields of a photo to Flickr

        :param photo: :obj:`SimplePhoto` object to save to Flickr
        '''
        self._flickr.photos_setMeta(photo_id=photo.photo_id,
                                    title=photo.title,
                                    description=photo.description)

    def tag_list(self):
        '''Return an iterator of the tags the user has
        '''

        resp = self._flickr.tags_getListUser()
        tags = resp.getchildren()[0]
        assert tags.tag == 'who'
        tags = tags.getchildren()[0]
        assert tags.tag == 'tags'
        for tag in tags.getiterator():
            yield tag.text
