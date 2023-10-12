from os.path import abspath, join
from site import getsitepackages
from argparse import ArgumentParser
from tomllib import load
from sys import exit
from subprocess import run
from distro import id
import os

if __name__ == '__main__':
    source_path = abspath(".")
    site_packages_path = list(filter(
        lambda site_package_path: '.venv' in site_package_path,
        getsitepackages(),
    ))[0]

    argumentParser = ArgumentParser("designer", description="Run PyQt6-designer with plugin paths configured in pyproject.toml.")

    argumentParser.add_argument("-v,--verbose", dest='verbose', action='store_true', default=False, help='Enable verbose output.')
    argumentParser.add_argument("-c,--config", dest='config', default=join(source_path, 'pyproject.toml'), help='Path of pyproject.toml.')
    argumentParser.add_argument("-l,--local", dest='local', action='store_true', default=False, help='Use the local qt6 tools instead of qt6_tools.')
    argumentParser.add_argument("-d,--debug", dest='debug', action='store_true', default=False, help='Enable debug output in designer-qt6.')

    args = argumentParser.parse_args()

    if args.debug:
        os.environ['QT_DEBUG_PLUGINS'] = '1'

    toml_file = open(args.config, 'rb')
    config = load(toml_file)
    toml_file.close()

    package_name = config["tool"]["poetry"]["name"]
    source_package_path = join(source_path, package_name)

    qt6_designer_command = []
    if args.local:
        if id() == 'ubuntu':
            qt6_designer_command = ['/usr/lib/qt6/bin/designer']
        elif id() == 'arch':
            qt6_designer_command = ['designer6']
    else:
        qt6_designer_command = ["pyqt6-tools", "designer"]

    qt6_tools_args = []
    if "tool" in config and "qt-designer" in config["tool"] and "widgets" in config["tool"]["qt-designer"]:
        widgets_config = config["tool"]["qt-designer"]["widgets"]
        
        # Widgets from installed packages
        if "site" in widgets_config:
            qt6_tools_args += list(map(
                lambda suffix: join(site_packages_path, suffix),
                widgets_config["site"],
            ))
        
        # Widgets inside the project
        if "source" in widgets_config:
            qt6_tools_args += list(map(
                lambda suffix: join(source_package_path, suffix),
                widgets_config["source"],
            ))

    if args.local:
        path_addition = (':' if os.name == 'posix' else ';').join(qt6_tools_args)
        if 'PYQTDESIGNERPATH' in os.environ:
            os.environ['PYQTDESIGNERPATH'] += ":" + path_addition
        else:
            os.environ['PYQTDESIGNERPATH'] = path_addition
        qt6_tools_args = []
    else:
        flagged_tools_args = []
        for widget_plugin_path in qt6_tools_args:
            flagged_tools_args += ["-p", widget_plugin_path]
        qt6_tools_args = flagged_tools_args

    if args.debug:
        print("Command:", qt6_designer_command + qt6_tools_args)
        print("PYQTDESIGNERPATH:", os.environ['PYQTDESIGNERPATH'] if 'PYQTDESIGNERPATH' in os.environ else "not set")

    exit(run(args=qt6_designer_command + qt6_tools_args).returncode)
