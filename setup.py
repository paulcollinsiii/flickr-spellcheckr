# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages


setup(name='flickr-spellcheckr',
      version='0.2.0',
      description='Commandline spellchecker for flickr photos',
      author='Paul Collins',
      author_email='paul.collins.iii@gmail.com',
      license='BSD',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Utilities'
                   ],
      packages=find_packages(where='src'),
      package_dir={'flickr_spellcheckr' : 'src/flickr_spellcheckr'},
      install_requires=['flickrapi >= 1.4.2',
                        'pyenchant >= 1.6.5',
                        'pyreadline', ],
      entry_points={
        'console_scripts': [
            'flickr-spellcheckr = flickr_spellcheckr.controller:main'
            ]
        },
      test_suite='nose.colletor',
      tests_require=['nose', 'mock'],
      url='https://github.com/paulcollinsiii/flickr-spellcheckr'
      )
