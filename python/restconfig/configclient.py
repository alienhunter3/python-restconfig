"""
ConfigParser client module provides drop-in replacements for regular configparser objects that are backed by a REST API.
"""

from configparser import SectionProxy, RawConfigParser, Interpolation
from typing import ValuesView, AbstractSet, Tuple, Callable, Any, Optional, overload, Union, Iterator, List, Mapping, \
    Type, Sequence, Literal
import requests
from .util import naive_url_path_join


class AbstractClassError(Exception):
    """Raised when attempting to use an abstract class method that isn't implemented in the abstract."""
    pass


class RestApiResponseError(Exception):
    """Raised when receiving an invalid response from a remote REST API."""
    pass


class Connection:
    """Abstract parent class for a connection to some type of service providing the same info as a ConfigParser."""
    def __init__(self):
        raise AbstractClassError("Calling not-implemented abstract class method.")

    @property
    def sections(self) -> list[str]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_section(self, name: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def get_section(self, name: str) -> SectionProxy:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def options(self, section: str) -> list[str]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_option(self, section: str, option: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def get_option(self, section: str, option: str) -> str:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def items(self, section: str = None) -> list[tuple]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def defaults(self) -> dict:
        raise AbstractClassError("Calling not-implemented abstract class method.")


class RestApiConnection(Connection):
    """Module that stores authentication and API endpoint information. Confirms connectivity."""
    def __init__(self, base_url: str, username: str = None, password: str = None, headers: dict = None):
        """

        :param base_url: Root URL of API to connect to.
        :param username: Use username if provided.
        :param password: Use password if provided.
        :param token: Use token if provided in lieu of username/password
        """
        self.username = username
        self.password = password
        self.headers = headers
        self.base_url = base_url.strip()

        if self.username is None:
            self.username = ""
        if self.password is None:
            self.password = ""

    @property
    def auth_provided(self):
        if not ((self.username == "") and (self.password == "")):
            return True
        return False

    def get(self, sub_path: str, headers: dict = None, **kwargs) -> requests.Response:
        """Method to make the appropriate get request to the API url specified."""

        if (self.headers is None) and (headers is None):
            headers_dict = None
        else:
            headers_dict = {}
            if self.headers is not None:
                for i in self.headers:
                    headers_dict[i] = self.headers[i]
            if headers is not None:
                for i in headers:
                    headers_dict[i] = headers[i]

        auth_tuple = None
        if self.auth_provided:
            auth_tuple = (self.username, self.password)

        return requests.get(naive_url_path_join(self.base_url, sub_path), auth=auth_tuple, headers=headers_dict,
                            **kwargs)

    def working(self) -> bool:
        try:
            res = self.get("")
            if res.status_code != 200:
                return False
            res_json = res.json()
            if 'data' not in res_json:
                return False
            if 'sections' not in res_json['data']:
                return False
            return True
        except Exception:
            return False

    @property
    def sections(self) -> list[str]:
        res = self.get("")
        if res.status_code != 200:
            raise Api
        return self.get("").json()['data']['sections']

    def has_section(self, name: str) -> bool:
        if name in self.get("").json()['data']['sections']:
            return True
        return False

    def get_section(self, name: str) -> SectionProxy:
        return super().get_section(name)

    def options(self, section: str) -> list[str]:
        return super().options(section)

    def has_option(self, section: str, option: str) -> bool:
        return super().has_option(section, option)

    def get_option(self, section: str, option: str) -> str:
        return super().get_option(section, option)

    def items(self, section: str = None) -> list[tuple]:
        return super().items(section)

    def defaults(self) -> dict:
        return super().defaults()


class ReadOnlyRestConfig(RawConfigParser):

    @overload
    def __init__(
        self,
        defaults: Optional[Mapping[str, Optional[str]]] = ...,
        dict_type: Type[Mapping[str, str]] = ...,
        allow_no_value: Literal[True] = ...,
        *,
        delimiters: Sequence[str] = ...,
        comment_prefixes: Sequence[str] = ...,
        inline_comment_prefixes: Optional[Sequence[str]] = ...,
        strict: bool = ...,
        empty_lines_in_values: bool = ...,
        default_section: str = ...,
        interpolation: Optional[Interpolation] = ...,
        converters: _converters = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        defaults: Optional[_section] = ...,
        dict_type: Type[Mapping[str, str]] = ...,
        allow_no_value: bool = ...,
        *,
        delimiters: Sequence[str] = ...,
        comment_prefixes: Sequence[str] = ...,
        inline_comment_prefixes: Optional[Sequence[str]] = ...,
        strict: bool = ...,
        empty_lines_in_values: bool = ...,
        default_section: str = ...,
        interpolation: Optional[Interpolation] = ...,
        converters: _converters = ...,
    ) -> None: ...

    def __init__(self, defaults: Optional[Mapping[str, Optional[str]]] = None,
                 dict_type: Type[Mapping[str, str]] = None, allow_no_value: Literal[True] = ..., *, delimiters: Sequence[str] = ...,
                 comment_prefixes: Sequence[str] = ..., inline_comment_prefixes: Optional[Sequence[str]] = ...,
                 strict: bool = ..., empty_lines_in_values: bool = ..., default_section: str = ...,
                 interpolation: Optional[Interpolation] = ..., converters: _converters = ...) -> None:
        super().__init__(defaults, dict_type, allow_no_value, delimiters=delimiters, comment_prefixes=comment_prefixes,
                         inline_comment_prefixes=inline_comment_prefixes, strict=strict,
                         empty_lines_in_values=empty_lines_in_values, default_section=default_section,
                         interpolation=interpolation, converters=converters)

    def __len__(self) -> int:
        return super().__len__()

    def __getitem__(self, section: str) -> SectionProxy:
        return super().__getitem__(section)

    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def defaults(self) -> _section:
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
    def getint(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> int: ...

    @overload
    def getint(
        self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ..., fallback: _T = ...
    ) -> Union[int, _T]: ...

    def getint(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> int:
        return super().getint(section, option, raw=raw, vars=vars)

    @overload
    def getfloat(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> float: ...

    @overload
    def getfloat(
        self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ..., fallback: _T = ...
    ) -> Union[float, _T]: ...

    def getfloat(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> float:
        return super().getfloat(section, option, raw=raw, vars=vars)

    @overload
    def getboolean(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> bool: ...

    @overload
    def getboolean(
        self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ..., fallback: _T = ...
    ) -> Union[bool, _T]: ...

    def getboolean(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> bool:
        return super().getboolean(section, option, raw=raw, vars=vars)

    @overload  # type: ignore
    def get(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> str: ...

    @overload
    def get(
        self, section: str, option: str, *, raw: bool = True, vars: dict = None, fallback: object = None
    ) -> Union[str, object]:
        return ""

    def get(self, section: str, option: str, *, raw: bool = ..., vars: Optional[_section] = ...) -> str:
        return super().get(section, option, raw=raw, vars=vars)

    @overload
    def items(self, *, raw: bool = False, vars: dict = None) -> AbstractSet[Tuple[str, SectionProxy]]: ...

    @overload
    def items(self, section: str, raw: bool = ..., vars: Optional[_section] = ...) -> List[Tuple[str, str]]: ...

    def items(self, *, raw: bool = ..., vars: Optional[_section] = ...) -> AbstractSet[Tuple[str, SectionProxy]]:
        return super().items(raw=raw, vars=vars)



