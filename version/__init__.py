from typing import (
    Self,
    Optional,
)
from types import ModuleType
from pygit2 import (
    Repository,
    GIT_DESCRIBE_TAGS,
)
from pathlib import Path
from enum import Enum
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)
from importlib.machinery import ModuleSpec
from importlib.resources import files
import imagecolorpicker


class VersionType(Enum):
    Unavailable = 0x0
    GitTag = 0x1
    GeneratedModule = 0x2


class Version:
    GitRepositorySuffix = '.git'
    NoVCSDescription = "novcs"
    ImportAttemptDescription = "imported"
    DirtySuffix = "-dirty"
    VersionModuleName = 'generated_version'

    def __init__(self: Self) -> None:
        self._repositoryPath: Optional[Path] = self._findRepositoryPath()
        self._versionType: VersionType = VersionType.Unavailable

        if self.hasRepository:
            self._versionType = VersionType.GitTag
            self._repository: Repository = Repository(self.repositoryPath)

        self._versionModule: ModuleType = self._findVersionModule()
        if self.hasVersionModule:
            self.versionType = VersionType.GeneratedModule

    def _findRepositoryPath(self: Self) -> Optional[Path]:
        """
            Return nearest git repository's path above __file__, or None
            if there is none available.
        """
        path = Path(__file__)
        while path.parent != path:
            repoPath: Path = path / Version.GitRepositorySuffix

            if(repoPath.exists()):
                return repoPath

            path = path.parent

        return None
    
    @property
    def repositoryPath(self: Self) -> Optional[Path]:
        return self._repositoryPath
    
    @property
    def hasRepository(self: Self) -> bool:
        return self._repositoryPath is not None

    def _findVersionModule(self: Self) -> Optional[ModuleType]:
        """
            Try to load the version number from a module
            which was generated at build time using `generateVersionModule`.
        """
        try:
            path: Path = Path(files(imagecolorpicker)) / '{}.py'.format(Version.VersionModuleName)
            spec: ModuleSpec = spec_from_file_location(path.name, path)
            module: Optional[ModuleType] = module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except:
            return None
        
    @property
    def versionModule(self: Self) -> Optional[ModuleType]:
        return self._versionModule
    
    @property
    def hasVersionModule(self: Self) -> bool:
        return self._versionModule is not None

    def describe(self: Self) -> str:
        """
            Returns a str containing the most appropriate version description available.
        """
        if self.hasRepository:
            return self._repository.describe(
                describe_strategy=GIT_DESCRIBE_TAGS,
                show_commit_oid_as_fallback=True,
                dirty_suffix=Version.DirtySuffix,
            )
        
        if self.hasVersionModule:
            return self._versionModule.__version__

        return Version.NoVCSDescription

    def generateVersionModule(self: Self, path: str) -> None:
        """
            Generates a module containing the most appropriate version string.
            Use this for example from pyinstaller spec files.
        """
        (Path(path) / (Version.VersionModuleName + '.py')).write_text("""
__version__ = '{}'
""".format(self.describe()))