from .util import naive_url_path_join, response_ok
import requests
from configparser import SectionProxy, RawConfigParser
from urllib.parse import quote_plus

UNSET = object()


class AbstractClassError(Exception):
    """Raised when attempting to use an abstract class method that isn't implemented in the abstract."""
    pass


class RestApiResponseError(Exception):
    """Raised when receiving an invalid response from a remote REST API."""
    pass


class Connection:
    """Abstract parent class for a connection to some type of service providing the same info as a ConfigParser."""

    def __len__(self) -> int:
        return len(self.sections())

    def sections(self) -> list[str]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_section(self, name: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def options(self, section: str) -> list[str]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_option(self, section: str, option: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def get_option(self, section: str, option: str, fallback=UNSET) -> str:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def items(self, section: str = UNSET) -> list[tuple]:
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

    def sections(self) -> list[str]:
        res = self.get("")
        if res.status_code != 200:
            raise RestApiResponseError(f"Received code {res.status_code}")
        return self.get("").json()['data']['sections']

    def has_section(self, name: str) -> bool:
        if name in self.get("").json()['data']['sections']:
            return True
        return False

    def options(self, section: str) -> list[str]:
        return super().options(section)

    def has_option(self, section: str, option: str) -> bool:
        return super().has_option(section, option)

    def get_option(self, section: str, option: str, fallback=UNSET) -> str:

        r = self.get(f"/section/{quote_plus(section)}/option/{quote_plus(option)}")

        if not response_ok(r, allowed_status=[200, 404]):
            raise RestApiResponseError(f"Received unexpected {r.status_code} response from API:\n{r.text}.")

        if r.status_code == 404:
            # This is either fine, or a Response error.
            try:
                message = r.json()['message']
            except Exception as e:
                raise RestApiResponseError("Problem with response received from API: " + str(e))
            if message in ['no such section', 'no such option']:
                if fallback == UNSET:
                    raise KeyError(f"No such option {option} in section {section}.")
                else:
                    return fallback
            else:
                raise RestApiResponseError("Problem with response received from API: " + r.json()['message'])
        return r.json()['data']['option']

    def items(self, section: str = None) -> list[tuple]:
        return super().items(section)

    def defaults(self) -> dict:
        return super().defaults()


class ConfigParserConnection(Connection):
    """Adapts a specified RawConfigParser to a Connection."""

    def __init__(self, _config: RawConfigParser):
        self.config = _config

    def sections(self) -> list[str]:
        return list(self.config.sections())

    def has_section(self, name: str) -> bool:
        return self.config.has_section(name)

    def options(self, section: str) -> list[str]:
        return list(self.config.options(section))

    def has_option(self, section: str, option: str) -> bool:
        return self.config.has_option(section, option)

    def get_option(self, section: str, option: str, fallback: object = UNSET) -> str:
        if fallback == UNSET:
            return self.config.get(section, option)
        else:
            return self.config.get(section, option, fallback=fallback)

    def items(self, section: str = UNSET) -> list[tuple]:
        if section == UNSET:
            return list(self.config.items())
        else:
            list(self.config.items(section=section))

    def defaults(self) -> dict:
        return dict(self.config.defaults())