# texbuild

Small command line tool to cleanly compile latex projects.

- Building your document does not pollute your source files
  with auto-generated build files.
- It uses `latexmk` with `lualatex` under the hood for compiling and caching.
- On failure, it automatically suppresses all interactive prompts
  and just shows the error message.
- Colorful message boxes give a quick clear idea
  of whether a build succeeded or not.
 
## Installation

This project has no python dependencies,
but you must have `latexmk` and `rsync` available on the command line.

```
pip install 'git+https://gitlab.psb.ugent.be/Utilities/texbuild.git'
```

Or, if you are developing `texbuild` itself:

```
git clone 'https://gitlab.psb.ugent.be/Utilities/texbuild.git'
cd texbuild
pip install -e .
```

## Project structure

This tool requires latex projects to be organized as follows:

```
/project_root/
    ┣ src/  (source code is here)
    ┣ bld/  (`src` is rsynced to here, then pdf is built here)
    ┗ dst/  (output pdf file is copied to here)
```

The only directory actually needed is the `src` directory,
the other directories will be made automatically.

You can safely delete the `bld` and `dst` folders using
the `texbuild` `cli`.
Or you can delete them manually when `texbuild` is not running.

### src

This contains all your Tex source code, this can be arbitrarily structured.
All files inside `src` can safely reference other files by the relative path
from the `src` dir.


### bld

Whenever a change is detected in `src`,
this change will be synchronized to the `bld` directory.
This is done with the `rsync` command line utility in Linux.

Once `rscync` finishes, the project is build automatically in the `bld` dir.
This way, all intermediate junk files are generated inside `bld`,
leaving `src` clean and tidy.


### dst

Once the build process is done, the result pdf is automatically copied to the
`dst` folder.

It is recommended to point your pdf browser to this document,
this way you can keep viewing the old version of document
while the new one is being compiled.
Also, when a compilation error occurs, you are not left with a blank pdf.


## Usage

Just point `texbuild` to your project dir
and to the the file you want to compile (relative to the `src` dir).
Do not include the `.tex` extension. E.g.:

```bash
texbuild ./example loop my_tex_file
# ┏━━━━╸ ┏━━━━━━━╸ ┏━━╸ ╺━━━━━━━━━━name of file to compile
# ┃      ┃         ┗auto re-compile on file change
# ┃      ┗path to project dir
# ┗name of command line utility
```

See `texbuild -h` for more details.

