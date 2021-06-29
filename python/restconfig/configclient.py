"""
ConfigParser client module provides drop-in replacements for regular configparser objects that are backed by a REST API.
"""

from configparser import SectionProxy, RawConfigParser, ConverterMapping
from typing import AbstractSet, Tuple, Union, Iterator, List
from .connection import UNSET, Connection


class ReadOnlyConfig(RawConfigParser):

    def __init__(self, backend: Connection, default_section="DEFAULT"):
        self.backend = backend
        self._converters = ConverterMapping(self)
        self.default_section = default_section

    def __len__(self) -> int:
        return self.backend.__len__()

    def __contains__(self, item):
        return self.backend.has_section(item)

    def __getitem__(self, section: str) -> SectionProxy:
        if section not in self:
            raise KeyError(f"No section '{section}' in config.")
        return SectionProxy(self, section)

    def __iter__(self) -> Iterator[str]:
        return self.backend.__iter__()

    def keys(self) -> set:
        return set(self.sections())

    def defaults(self) -> dict:
        return self.backend.defaults()

    def sections(self) -> List[str]:
        return self.backend.sections()

    def has_section(self, section: str) -> bool:
        return self.backend.has_section(section)

    def options(self, section: str) -> List[str]:
        return self.backend.get_section(section)

    def has_option(self, section: str, option: str) -> bool:
        return self.backend.has_option(section, option)

    def getint(self, section: str, option: str, *, raw: bool = False, vars: dict = None, fallback: object = UNSET)\
            -> Union[int, object]:
        try:
            opt = self.backend.get_option(section, option)
        except KeyError:
            return fallback
        return int(opt)

    def getfloat(
        self, section: str, option: str, *, raw: bool = False, vars: dict = None, fallback: object = UNSET
    ) -> Union[float, object]:
        try:
            opt = self.backend.get_option(section, option)
        except KeyError:
            return fallback
        return float(opt)

    def getboolean(
        self, section: str, option: str, *, raw: bool = False, vars: dict = None, fallback: object = UNSET
    ) -> Union[bool, object]:
        try:
            opt = self.backend.get_option(section, option)
        except KeyError:
            return fallback
        return bool(opt)

    def get(
        self, section: str, option: str, *, raw: bool = True, vars: dict = None, fallback: object = None
    ) -> Union[str, object]:
        try:
            return self.backend.get_option(section, option)
        except KeyError:
            return fallback

    def items(self, *, raw: bool = False, vars: dict = None) -> List[Tuple[str, SectionProxy]]:
        s = []
        for i in self.keys():
            s.append((i, SectionProxy(self, i)))
        return s
