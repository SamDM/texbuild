#!/usr/bin/env python3

import shutil
from argparse import Namespace
from os import path
from shutil import copy2
from subprocess import run, CalledProcessError
from typing import List

from texbuild.arbitrary import default, makedir, having_cwd


# ---------------------------------------------------------------------------------------------------------------------


class Bcolors:
    HEADER    = '\033[95m'
    INFOBLUE  = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


def print_markup(txt, markup=Bcolors.INFOBLUE, *args, **kwargs):
    print(markup + txt + Bcolors.ENDC, *args, **kwargs)


def print_frame(txt, markup=Bcolors.INFOBLUE + Bcolors.BOLD):
    border = "*" * (max(map(len, txt.splitlines())) + 4)
    print_markup(border, Bcolors.BOLD)
    print_markup("| ", Bcolors.BOLD, end='')
    print_markup(txt, markup, end='')
    print_markup(" |", Bcolors.BOLD)
    print_markup(border, Bcolors.BOLD)

# ---------------------------------------------------------------------------------------------------------------------


class TexBuild:
    """
    Clean build system to make Tex files with latexmk

    Under the hood it rsyncs all source files to a build directory,
    then the build is done with `latexmk` in that directory and the output is copied to a destination directory (dst).
    This has three advantages:
        - It prevents intermediary files from polluting the source code folders
        - It makes it easier to find the output files: just look in the dst folder.
        - It makes it easy to clean/reset a corrupted latexmk state: just delete the build folder.

    This class is opinionated in the sense that it assumes you only use Tex for pdf outputs.
    It also assumes that luatex is the engine you want to use for that purpose.
    Finally, it assumes the following structure for your Tex project::

        /tex_root/
            ┣ src/  (source code is here)
            ┣ bld/  (`src` is rsynced to here, then pdf is built here)
            ┗ dst/  (output pdf file is copied to here)
    """

    def __init__(self, tex_root: str):
        """
        :param tex_root: The parent folder containing the source directory.
            This folder contains the source (src), build (bld) and destination (dst) directories.
        """
        self._tex_root = tex_root
    
    @property
    def tex_root(self):
        return self._tex_root
    
    @property
    def tex_src(self):
        return path.join(self.tex_root, "src")

    @property
    def tex_bld(self):
        return path.join(self.tex_root, "bld")

    @property
    def tex_dst(self):
        return path.join(self.tex_root, "dst")
    
    def init_dirs(self):
        makedir(self.tex_root, recursive=True, exists_ok=True)
        makedir(self.tex_src, exists_ok=True)

    def copy_build_files(self):
        """
        Synchronizes files in the source directory to the build directory.
        Files existing only in the build directory are not modified.
        """
        rsync_command = ["rsync", "-av", self.tex_src + "/", self.tex_bld]

        print_frame("COPYING BUILD FILES TO BLD DIRECTORY")
        makedir(self.tex_bld, exists_ok=True)
        run(rsync_command)

    def _run_latexmk_in_bld_dir(self, tex_filename: str, latexmk_opts: List):
        build_command = ["latexmk",
                         "-halt-on-error", "-interaction=nonstopmode",
                         "-pdflatex=lualatex", "-pdf", tex_filename + ".tex"] + \
                        latexmk_opts

        with having_cwd(self.tex_bld):
            print_frame("BUILDING DOCUMENT")
            run(build_command, check=True)

    def _copy_to_dst(self, tex_filename: str, pdf_filename: str):
        """
        tex_filename and pdf_filename must be given WITHOUT the file extension
        """

        document_pdf_bld = path.join(self.tex_bld, tex_filename + ".pdf")
        document_pdf_dst = path.join(self.tex_dst, pdf_filename + ".pdf")

        makedir(self.tex_dst, exists_ok=True)
        copy2(document_pdf_bld, document_pdf_dst)

    def build_document(self, tex_filename, pdf_filename=None, latexmk_opts=None):
        """
        tex_filename and pdf_filename must be given WITHOUT the file extension
        """

        latexmk_opts = default(latexmk_opts, [])
        pdf_filename = default(pdf_filename, tex_filename)

        try:
            self.copy_build_files()
            self._run_latexmk_in_bld_dir(tex_filename, latexmk_opts)
            self._copy_to_dst(tex_filename, pdf_filename)
            # Yeee!
            print_markup("BUILD SUCCESSFUL", Bcolors.OKGREEN, end="\n\n")
            success = True
        except CalledProcessError:
            # Nooo...
            print_markup("BUILD FAILED", Bcolors.FAIL, end="\n\n")
            success = False
        return success

    def wait_for_code_changes(self):
        watch_command = ["inotifywait", "-e", "modify,create,delete,attrib", "-r", self.tex_src]

        print_frame("WATCHING SRC DIRECTORY FOR CHANGES")
        run(watch_command)

    def loop(self, *args, **kwargs):
        while True:
            try:
                self.build_document(*args, **kwargs)
                self.wait_for_code_changes()
            except KeyboardInterrupt:
                print()
                print_markup("QUITTING (interrupt signal received)", Bcolors.WARNING)
                break

    def clean(self):
        """Removes the build directory"""
        print_frame("CLEANING BLD DIRECTORY")
        encountered_errors = False

        if path.exists(self.tex_bld):
            def report_error(func, pafh, exc_info):
                nonlocal encountered_errors
                encountered_errors = True

                print("(error) got error removing: " + pafh)
                print(func)
                print(exc_info[1])

            shutil.rmtree(self.tex_bld, onerror=report_error)
        else:
            print(f"{self.tex_bld} already removed")
            
        if encountered_errors:
            print_markup("CLEANUP FINISHED (errors encountered)", Bcolors.WARNING)
        else:
            print_markup("CLEANUP FINISHED", Bcolors.OKGREEN)

# ---------------------------------------------------------------------------------------------------------------------


def parse_cmd_args():
    import argparse

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='texbuild', description='Build Tex pdf documents.')
    parser.add_argument('root', type=str, help="tex project root folder, contains `src`, `bld` and `dst` sub-folders")
    subparsers = parser.add_subparsers(dest="cmd", required=True, help="which of these actions to take")
    
    # create helper parser
    bld_parser = argparse.ArgumentParser(add_help=False)
    bld_parser.add_argument('document', type=str,
                            help="main document to build (relative to `src`, omit .tex extension)")
    bld_parser.add_argument('--latexmk-opts', nargs='*', help="options passed to latexmk")

    # create the command specific parsers
    subparsers.add_parser('copy', help='copy all source files to the build directory')
    subparsers.add_parser('build', help='build the target document once', parents=[bld_parser])
    subparsers.add_parser('loop', help='re-build the target document on every source code change', parents=[bld_parser])
    subparsers.add_parser('clean', help='remove the build directory')

    return parser.parse_args()


def run_args(ns: Namespace):
    tb = TexBuild(ns.root)
    if ns.cmd == "copy":
        tb.copy_build_files()
    if ns.cmd == "build":
        tb.build_document(ns.document, ns.latexmk_opts)
    if ns.cmd == "loop":
        tb.loop(ns.document, ns.latexmk_opts)
    if ns.cmd == "clean":
        tb.clean()


def main():
    run_args(parse_cmd_args())


if __name__ == '__main__':
    main()
