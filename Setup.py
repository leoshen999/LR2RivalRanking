#coding: utf-8

from distutils.core import setup
import py2exe, sys, os

sys.argv.append( 'py2exe' )

CLOUD_PNG = open('cloud.png','rb').read()
CONSOLASHIGH_TTF = open('ConsolasHigh.ttf','rb').read()
SUPPORTEDUNICODE_TXT = open('SupportedUnicode.txt','r').read()
STYLE_CSS = open('style.css','r').read()
SRC_JS = open('src.js','r').read()


setup(
	options = { 'py2exe': {'bundle_files': 1, 'compressed': True, 'includes': ['sip','lxml.etree', 'lxml._elementpath', 'gzip'], 'dll_excludes': ['w9xpopen.exe'] }, },
	windows = [{
				'script': "LR2RivalRanking.py",
				'other_resources': [
					(u'CLOUD_PNG', 1, CLOUD_PNG),
					(u'CONSOLASHIGH_TTF', 2, CONSOLASHIGH_TTF),
					(u'SUPPORTEDUNICODE_TXT', 3, SUPPORTEDUNICODE_TXT),
					(u'STYLE_CSS', 4, STYLE_CSS),
					(u'SRC_JS', 5, SRC_JS)
				],
				'uac_info': "requireAdministrator",
	}],
	zipfile = None,
)