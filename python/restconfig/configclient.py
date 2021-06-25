"""
ConfigParser client module provides drop-in replacements for regular configparser objects that are backed by a REST API.
"""

from configparser import SectionProxy, RawConfigParser, Interpolation
from typing import ValuesView, AbstractSet, Tuple, Callable, Any, Optional, overload, Union, Iterator, List, Mapping, \
    Type, Sequence, Literal
from connection import UNSET, Connection, RestApiConnection


class ReadOnlyConfig(RawConfigParser):

    def __init__(self, backend: Connection):
        self.backend = backend

    def __len__(self) -> int:
        return super().__len__()

    def __getitem__(self, section: str) -> SectionProxy:
        return super().__getitem__(section)

    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def defaults(self) -> dict:
        return super().defaults()

    def sections(self) -> List[str]:
        return super().sections()

    def has_section(self, section: str) -> bool:
        return super().has_section(section)

    def options(self, section: str) -> List[str]:
        return super().options(section)

    def has_option(self, section: str, option: str) -> bool:
        return super().has_option(section, option)

    @overload
    def getint(self, section: str, option: str, *, raw: bool = False, vars: dict = None) -> int: ...

    @overload
    def getint(self, section: str, option: str, *, raw: bool = ..., vars: dict = None, fallback: object = None) \
            -> object:
        pass

    def getint(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> int:
        return super().getint(section, option, raw=raw, vars=vars)

    @overload
    def getfloat(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> float: ...

    @overload
    def getfloat(
        self, section: str, option: str, *, raw: bool = ..., vars: dict = None, fallback: object = None
    ) -> Union[float, object]:
        pass

    def getfloat(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> float:
        return super().getfloat(section, option, raw=raw, vars=vars)

    @overload
    def getboolean(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> bool: ...

    @overload
    def getboolean(
        self, section: str, option: str, *, raw: bool = ..., vars: dict = None, fallback: object = ...
    ) -> Union[bool, object]: ...

    def getboolean(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> bool:
        return super().getboolean(section, option, raw=raw, vars=vars)

    @overload  # type: ignore
    def get(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> str: ...

    @overload
    def get(
        self, section: str, option: str, *, raw: bool = True, vars: dict = None, fallback: object = None
    ) -> Union[str, object]:
        return ""

    def get(self, section: str, option: str, *, raw: bool = ..., vars: dict = None) -> str:
        return super().get(section, option, raw=raw, vars=vars)

    @overload
    def items(self, *, raw: bool = False, vars: dict = None) -> AbstractSet[Tuple[str, SectionProxy]]: ...

    @overload
    def items(self, section: str, raw: bool = ..., vars: dict = None) -> List[Tuple[str, str]]: ...

    def items(self, *, raw: bool = ..., vars: dict = None) -> AbstractSet[Tuple[str, SectionProxy]]:
        return super().items(raw=raw, vars=vars)



