# ImageColorPicker
Image color picker tool by Team210

![Screenshot](https://github.com/LeStahL/ImageColorPicker/blob/master/screenshot.png?raw=true)

# Build
You need Python and poetry installed and in your system `PATH`. Before building, install the dependencies by running `poetry config virtualenvs.in-project true` and then `poetry install` from the source root.

For debugging, run `poetry run python -m imagecolorpicker` from the source root.

For building an executable, run `poetry run pyinstaller imagecolorpicker/imagecolorpicker.spec` from the source root. The executable will be generated in the `dist` subfolder.

# Use
ImageColorPicker can
* Load images from files with formats supported by Qt6 (By selecting `File->Open` or dragging image files onto the preview).
* Paste images or html with images into the preview with `Edit->Paste` or `CTRL+v`.
* Drop images or html with images into the preview over drag&drop (for example from web browsers). This will resolve URLS per http request and decode base-64 encoded images.
* Select the color format you want to copy when hitting `CTRL+c` over the `Copy`-dropdown.
* Copy the currently selected color by pressing `CTRL+c`.

# License
ImageColorPicker is (c) 2023 Alexander Kraus <nr4@z10.info> and GPLv3; see LICENSE for details.
