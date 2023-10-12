# ImageColorPicker
Image color picker tool by Team210

![Screenshot](https://github.com/LeStahL/ImageColorPicker/blob/master/screenshot.png?raw=true)

# Build
You need Python and poetry installed and in your system `PATH`. Before building, install the dependencies by running `poetry config virtualenvs.in-project true` and then `poetry install` from the source root.

For debugging, run `poetry run python -m imagecolorpicker` from the source root.

For building an executable, run `poetry run pyinstaller imagecolorpicker/imagecolorpicker.spec` from the source root. The executable will be generated in the `dist` subfolder.

# License
Image color picker is (c) 2023 Alexander Kraus <nr4@z10.info> and GPLv3; see LICENSE for details.
