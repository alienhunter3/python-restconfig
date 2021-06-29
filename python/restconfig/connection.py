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

    def __iter__(self):
        return self.sections().__iter__()

    def __getitem__(self, item):
        return set(self.get_section(item))

    def default_section(self):
        return "DEFAULT"

    def keys(self) -> set:
        return set(self.sections())

    def values(self) -> list:
        s = []
        for key in self.keys():
            s.append({key: self.get_section(key)})
        return s

    def sections(self) -> list[str]:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_section(self, name: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def get_section(self, section: str) -> list:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def has_option(self, section: str, option: str) -> bool:
        raise AbstractClassError("Calling not-implemented abstract class method.")

    def get_option(self, section: str, option: str) -> str:
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

    def default_section(self) -> list[str]:
        res = self.get("")
        if res.status_code != 200:
            raise RestApiResponseError(f"Received code {res.status_code}")
        return self.get("").json()['data']['default_section']

    def has_section(self, name: str) -> bool:
        json_data = self.get("").json()['data']
        if name in json_data['sections']:
            return True
        if name == json_data['default_section']:
            return True
        return False

    def get_section(self, section: str) -> list:
        r = self.get(f"/section/{quote_plus(section)}")
        if not response_ok(r, allowed_status=[200]):
            raise RestApiResponseError(f"Received unexpected {r.status_code} response from API:\n{r.text}.")
        try:
            return r.json()['data']['options']
        except Exception as e:
            raise RestApiResponseError("Problem with response received from API: " + str(e))

    def has_option(self, section: str, option: str) -> bool:
        try:
            self.get_option(section, option)
            return True
        except KeyError:
            return False

    def get_option(self, section: str, option: str) -> str:

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
                raise KeyError(f"No such option {option} in section {section}.")
            else:
                raise RestApiResponseError("Problem with response received from API: " + r.json()['message'])
        return r.json()['data']['option']

    def defaults(self) -> dict:
        r = self.get("/defaults")
        if not response_ok(r, allowed_status=[200]):
            raise RestApiResponseError(f"Received unexpected {r.status_code} response from API:\n{r.text}.")
        try:
            return dict(r.json()['data'])
        except Exception as e:
            raise RestApiResponseError("Problem with response received from API: " + str(e))


class ConfigParserConnection(Connection):
    """Adapts a specified RawConfigParser to a Connection."""

    def __init__(self, _config: RawConfigParser):
        self.config = _config

    def default_section(self):
        return self.config.default_section

    def sections(self) -> list[str]:
        return list(self.config.sections())

    def has_section(self, name: str) -> bool:
        if name == self.default_section():
            return True
        return self.config.has_section(name)

    def get_section(self, section: str) -> list:
        return list(self.config[section].keys())

    def has_option(self, section: str, option: str) -> bool:
        return self.config.has_option(section, option)

    def get_option(self, section: str, option: str) -> str:
        return self.config.get(section, option)

    def defaults(self) -> dict:
        return dict(self.config.defaults())
