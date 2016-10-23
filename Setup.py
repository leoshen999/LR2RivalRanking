#coding: utf-8

from distutils.core import setup
import py2exe, sys, os

sys.argv.append( 'py2exe' )

CLOUD_PNG = open('resources/cloud.png','rb').read()
STYLE_CSS = open('resources/style.css','r').read()
SRC_JS = open('resources/src.js','r').read()
CONSOLASHIGH_TTF = open('resources/ConsolasHigh.ttf','rb').read()


setup(
	options = { 'py2exe': {'bundle_files': 1, 'compressed': True, 'includes': ['sip', "PyQt4.QtCore","PyQt4.QtGui","PyQt4.QtNetwork",'lxml.etree', 'lxml._elementpath', 'gzip'], 'dll_excludes': ['w9xpopen.exe'] }, },
	windows = [{
				'script': "LR2RivalRanking.py",
				'other_resources': [
					(u'CLOUD_PNG', 1, CLOUD_PNG),
					(u'STYLE_CSS', 2, STYLE_CSS),
					(u'SRC_JS', 3, SRC_JS),
					(u'CONSOLASHIGH_TTF', 4, CONSOLASHIGH_TTF)
				],
				'uac_info': "requireAdministrator",
	}],
	zipfile = None,
)