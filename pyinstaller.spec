# -*- mode: python ; coding: utf-8 -*-
from os.path import abspath, join
from zipfile import ZipFile
from platform import system
from imagecolorpicker.version import Version
from pathlib import Path

moduleName = 'imagecolorpicker'
rootPath = Path(".")
buildPath = rootPath / 'build'
distPath = rootPath / 'dist'
sourcePath = rootPath / moduleName

block_cipher = None

version = Version()
version.generateVersionModule(buildPath)

a = Analysis(
    [
        join(sourcePath, '__main__.py'),
    ],
    pathex=[],
    binaries=[],
    datas=[
        (buildPath / '{}.py'.format(Version.VersionModuleName), moduleName),
        (join(sourcePath, 'team210.ico'), moduleName),
        (join(sourcePath, 'widgets', 'pickablecolorlabel', 'default.png'), join(moduleName, 'widgets', 'pickablecolorlabel')),
    ],
    hiddenimports=[
        '_cffi_backend',
        'scipy._lib.array_api_compat.numpy.fft',
        'scipy.special._special_ufuncs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{}-{}'.format(moduleName, version.describe()),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=join(sourcePath, 'team210.ico'),
)

exeFileName = '{}-{}{}'.format(moduleName, version.describe(), '.exe' if system() == 'Windows' else '')
zipFileName = '{}-{}-{}.zip'.format(moduleName, version.describe(), 'windows' if system() == 'Windows' else 'linux')

zipfile = ZipFile(distPath / zipFileName, mode='w')
zipfile.write(distPath / exeFileName, arcname=exeFileName)
zipfile.write(rootPath / 'README.md', arcname='README.md')
zipfile.write(rootPath / 'LICENSE', arcname='LICENSE')
zipfile.write(rootPath / 'screenshot.png', arcname='screenshot.png')
zipfile.close()
