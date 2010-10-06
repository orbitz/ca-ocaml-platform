#!/usr/bin/env python
import os

from igs.utils import commands
from igs.utils import logging
from igs.utils import functional as func
from igs.utils import cli

OPTIONS = [
    ('prefix', '-p', '--prefix', 'Prefix directory to install everything into', cli.notNone),
    ('tmpdir', '', '--tmpdir', 'Temporary directory to use, defaults to $TMPDIR and then to /tmp',
     func.compose(cli.defaultIfNone('/tmp'), cli.defaultIfNone(os.getenv('TMPDIR')))),
    ('debug', '-d', '--debug', 'Turn debugging output on', func.identity)
    ]


URLS = [
    ('ocaml', 'http://caml.inria.fr/pub/distrib/ocaml-3.12/ocaml-3.12.0.tar.gz'),
    ('res', 'http://hg.ocaml.info/release/res/archive/release-3.2.0.tar.gz'),
    ('ocaml-pcre', 'http://hg.ocaml.info/release/pcre-ocaml/archive/release-6.1.0.tar.gz'),
    ('fieldslib', 'http://www.janestreet.com/ocaml/fieldslib-0.1.0.tgz'),
    ('type-conv', 'http://hg.ocaml.info/release/type-conv/archive/release-2.0.1.tar.gz'),
    ('sexplib', 'http://www.janestreet.com/ocaml/sexplib310-release-4.2.15.tar.gz'),
    ('bin-prot', 'http://hg.ocaml.info/release/bin-prot/archive/release-1.2.23.tar.gz'),
    ('core', 'http://www.janestreet.com/ocaml/core-0.6.0.tgz'),
    ]


def untarToDir(tarFile, outDir):
    commands.runSystemEx('cd %s; tar -zxvf %s' % (outDir, tarFile), log=logging.DEBUG)

    
def main(options, _args):
    logging.DEBUG = options('debug')
    env = {'PATH': options('prefix') + ':' + os.getenv('PATH')}

    tmpDir = os.path.join(options('tmpdir'), 'ca-ocaml-platform')
    buildDir = os.path.join(tmpDir, 'build')
    commands.runSystem('rm -rf ' + tmpDir, log=logging.DEBUG)
    commands.runSystemEx('mkdir -p ' + tmpDir, log=logging.DEBUG)
    commands.runySystemEx('mkdir -p ' + buildDir, log=logging.DEBUG)
    
    #
    # Download everything first
    for _, url in URLS:
        commands.runSystemEx('wget --quiet -P %s %s' % (tmpDir, url), log=logging.DEBUG)

    for project, url in URLS:
        fileName = os.path.basename(url)
        downloadedName = os.path.join(tmpDir, fileName)
        untarToDir(downloadedName, buildDir)
        
        # Ocaml gets special attention because it needs the prefix
        if project == 'ocaml':
            commands.runSingleProgramEx('cd %s/*%s*; ./configure -prefix %s' % (buildDir, project, options('prefix')),
                                        log=logging.DEBUG)
            commands.runSingleProgramEx('cd %s/*%s*; make world opt install' % (buildDir, project),
                                        log=logging.DEBUG)
        elif project == 'ocaml-pcre':
            commands.runSingleProgramEx('cd %s/*%s*; ./configure' % (buildDir, project),
                                        log=logging.DEBUG)
            commands.runSingleProgramEx('cd %s/*%s*; make install' % (buildDir, project),
                                        log=logging.DEBUG)
        elif project == 'core':
            commands.runSingleProgramEx('cd %s/*%s*; patch -p1 -i %s/patches/core-0.6.0-3.12.0.patch' % (buildDir, project, os.getcwd()),
                                        log=logging.DEBUG)
            commands.runSingleProgramEx('cd %s/*%s*; make' % (buildDir, project),
                                        log=logging.DEBUG)
            commands.runSingleProgramEx('cd %s/*%s*; make install' % (buildDir, project),
                                        log=logging.DEBUG)
        else:
            commands.runSingleProgramEx('cd %s/*%s*; make' % (buildDir, project),
                                        log=logging.DEBUG)
            commands.runSingleProgramEx('cd %s/*%s*; make install' % (buildDir, project),
                                        log=logging.DEBUG)

if __name__ == '__main__':
    main(*cli.buildConfigN(OPTIONS, putInGeneral=False))
