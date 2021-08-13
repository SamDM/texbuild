# texbuild

Small command line tool to cleanly compile latex projects.

- Building your document does not pollute your source files
  with auto-generated build files.
- Intermediate build steps are cached using `latexmk` with `lualatex`.
- On failure, you keep the latest successfully generated pdf,
  instead of having a corrupted or blank pdf.
- On failure, it automatically suppresses all interactive prompts
  and just shows the error message.
- Colorful message boxes give a quick clear idea
  of whether a build succeeded or not.

## how does is work?

1. The tool uses the `inotifywait` command line utility too watch for file edits.
   As soon as a file edit is detected in the `src` folder
   (relative to the `texbuild` root directory), it jumps into action.
2. Then, the tool will copy all changes (and only the changes)
   to a build folder (using `rsync`).
   The pdf is then created inside the build folder
   (using `latexmk` with `lualatex`).
   This way, all the intermediary files 
   that would otherwise clutter your workspace are confined to that build folder.
3. If the build was successful, the finished pdf is copied to the `dst` folder.

See the _Project structure_ and _Usage_ sections for more info.

## Installation

This project has no python dependencies,
but you must have `rsync`, `inotifywait` and `latexmk` available on the command line.

```
pip install 'git+https://github.com/SamDM/texbuild'
```

Or, if you are developing `texbuild` itself:

```
git clone 'https://github.com/SamDM/texbuild.git'
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

### step 1:

Just point `texbuild` to your project dir
and give it the the file you want to compile (relative to the `src` dir).
Do not include the `.tex` extension. E.g.:

```bash
texbuild ./example loop my_tex_file
# ┏━━━━╸ ┏━━━━━━━╸ ┏━━╸ ╺━━━━━━━━━━name of file to compile
# ┃      ┃         ┗auto re-compile on file change
# ┃      ┗path to project (root) dir
# ┗name of command line utility
```

See `texbuild -h` for more details.

### step 2:

Make an edit in a file in the `src` directory 
with you favorite text/image/source code/whatever editor.

### step 3:

Open the generated pdf in the `dst` folder with a pdf viewer.
I recommend a pdf viewer that auto-refreshes if the underlying pdf file changes.
For Linux, Okular is good pdf viewer in this setup.

### step 4:

Repeat step 2, the pdf will auto-recompile in the background on every file save.
If the build process gets stuck, using `texbuild <project_dir> clean` can help
to remove corrupted build files.
