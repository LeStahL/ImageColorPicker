from argparse import (
    Namespace,
    ArgumentParser,
)
from subprocess import (
    run,
    CompletedProcess,
)
from importlib.resources import files
from pathlib import Path
from imagecolorpicker import (
    widgets,
)
from difflib import unified_diff
from sys import exit
from ast import parse
from deepdiff import DeepDiff


if __name__ == '__main__':
    parser: ArgumentParser = ArgumentParser('generate', description='FETT UI and translation generator')
    parser.add_argument(
        '-c', '--check',
        action='store_true',
        dest='check',
        help='Verify all files have been generated.',
    )
    args: Namespace = parser.parse_args()

    buildFolder: Path = Path('build')
    if not buildFolder.exists():
        buildFolder.mkdir()

    # PyQt UI files.
    UIFiles: list[Path] = [
        files(widgets) / 'gradienteditor' / 'gradienteditor.ui',
        files(widgets) / 'mainwindow' / 'mainwindow.ui',
    ]

    errored: bool = False
    for uiFile in UIFiles:
        pyUiFile = Path(uiFile).parent / f'ui_{Path(uiFile).stem}.py'
        print(f"Converting {uiFile} to {pyUiFile}...")

        if args.check:
            # Copy old file to build
            (Path('build') / f'{pyUiFile.stem}_old.py').write_bytes(pyUiFile.read_bytes())

        # Generate
        result: CompletedProcess = run([
            'poetry', 'run',
            'pyuic6', f'{uiFile}',
            '--debug',
            '-o', f'{pyUiFile}',
        ])

        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))

        if args.check:
            newPath: Path = Path('build') / f'{pyUiFile.stem}_new.py'

            # Copy new file to build
            newPath.write_bytes(pyUiFile.read_bytes())

            oldSource: str = (Path('build') / f'{pyUiFile.stem}_old.py').read_text()
            newSource: str = newPath.read_text()

            # diff
            if DeepDiff(parse(oldSource), parse(newSource)):
                for line in unified_diff(
                    oldSource.splitlines(),
                    newSource.splitlines(),
                    fromfile=str(Path('build') / f'{uiFile.name}.old'),
                    tofile=str(Path('build') / f'{uiFile.name}.new'),
                ):
                    print(line)
                errored = True

    if errored:
        print("Generated source were out of date.")
        exit(1)
