#!/usr/bin/env python
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from setuptools import setup, Command
import re
import os
import ConfigParser
import unittest
import sys


class SQLiteTest(Command):
    """
    Run the tests on SQLite
    """
    description = "Run tests on SQLite"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.environ['TRYTOND_DATABASE_URI'] = 'sqlite://'
        os.environ['DB_NAME'] = ':memory:'

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


class XMLTests(Command):
    """Runs the tests and save the result to an XML file

    Running this requires unittest-xml-reporting which can
    be installed using::

        pip install unittest-xml-reporting

    """
    description = "Run tests with coverage and produce jUnit style report"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import coverage
        import xmlrunner
        cov = coverage.coverage(source=["trytond.modules.avalara"])
        cov.start()
        from tests import suite
        xmlrunner.XMLTestRunner(output="xml-test-results").run(suite())
        cov.stop()
        cov.save()
        cov.xml_report(outfile="coverage.xml")


class RunAudit(Command):
    """Audits source code using PyFlakes for following issues:
        - Names which are used but not defined or used before they are defined.
        - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print "Audit requires PyFlakes installed in your system."
            sys.exit(-1)

        warns = 0
        # Define top-level directories
        dirs = ('.')
        for dir in dirs:
            for root, _, files in os.walk(dir):
                if root.startswith(('./build', './doc')):
                    continue
                for file in files:
                    if not file.endswith(('__init__.py', 'upload.py')) \
                            and file.endswith('.py'):
                        warns += flakes.checkPath(os.path.join(root, file))
        if warns > 0:
            print "Audit finished with total %d warnings." % warns
            sys.exit(-1)
        else:
            print "No problems found in sourcecode."
            sys.exit(0)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = [
    'avatax',
]
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(
    name='trytond_avalara',
    version=info.get('version', '0.0.1'),
    description='Tryton module for tax rate calculation',
    long_description=read('README.rst'),
    author='Openlabs Technologies and Consulting (P) Ltd',
    url='http://www.openlabs.co.in/',
    package_dir={'trytond.modules.avalara': '.'},
    packages=[
        'trytond.modules.avalara',
        'trytond.modules.avalara.tests',
    ],
    package_data={
        'trytond.modules.avalara':
            info.get('xml', []) + [
                'tryton.cfg', 'locale/*.po', 'icons/*.svg', 'view/*.xml'
            ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
    ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    avalara = trytond.modules.avalara
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    cmdclass={
        'xmltests': XMLTests,
        'audit': RunAudit,
        'test': SQLiteTest,
    },
)
