import os
import pytest
from unittest.mock import patch, MagicMock

from app import divide, is_safe_url, fetch, get_api_key, allowed_fetch_hosts


class TestDivide:
    """Test cases for the divide function."""

    def test_divide_by_zero_raises(self):
        """divide(a, 0) should raise ValueError."""
        with pytest.raises(ValueError, match="division by zero"):
            divide(1, 0)

    def test_divide_ok(self):
        """divide(a, b) should return a/b for non-zero b."""
        assert divide(10, 2) == 5
        assert divide(9, 3) == 3
        assert divide(7, 2) == 3.5

    def test_divide_negative(self):
        """divide should work with negative numbers."""
        assert divide(-10, 2) == -5
        assert divide(10, -2) == -5
        assert divide(-10, -2) == 5


class TestIsSafeUrl:
    """Test cases for the is_safe_url function."""

    @pytest.mark.parametrize(
        "url,expected",
        [
            # Allowed hosts
            ("https://api.example.com/data", True),
            ("http://api.example.com/data", True),
            ("https://api.example.com:8080/data?key=value", True),
            # Disallowed hosts
            ("https://evil.com/data", False),
            ("https://api.evil.com/data", False),
            # Localhost/loopback
            ("https://localhost/data", False),
            ("https://127.0.0.1/data", False),
            ("https://0.0.0.0/data", False),
            # Invalid schemes
            ("ftp://api.example.com/data", False),
            ("gopher://api.example.com/data", False),
            # Malformed URLs
            ("not-a-url", False),
            ("", False),
        ],
    )
    def test_is_safe_url(self, url, expected):
        """is_safe_url should correctly validate URLs."""
        allowed = frozenset(["api.example.com"])
        assert is_safe_url(url, allowed_hosts=allowed) is expected

    def test_is_safe_url_custom_hosts(self):
        """is_safe_url should respect custom allowed_hosts."""
        custom_hosts = frozenset(["api.internal.com", "data.internal.com"])
        assert is_safe_url("https://api.internal.com/test", allowed_hosts=custom_hosts) is True
        assert is_safe_url("https://data.internal.com/test", allowed_hosts=custom_hosts) is True
        assert is_safe_url("https://other.com/test", allowed_hosts=custom_hosts) is False


class TestGetApiKey:
    """Test cases for the get_api_key function."""

    def test_get_api_key_present(self):
        """get_api_key should return the API key when set."""
        with patch.dict(os.environ, {"API_KEY": "sk-test-12345"}):
            assert get_api_key() == "sk-test-12345"

    def test_get_api_key_missing(self):
        """get_api_key should raise RuntimeError when API_KEY is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="API_KEY environment variable is required"):
                get_api_key()


class TestAllowedFetchHosts:
    """Test cases for the allowed_fetch_hosts function."""

    def test_allowed_fetch_hosts_default(self):
        """allowed_fetch_hosts should return default hosts when env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            hosts = allowed_fetch_hosts()
            assert "api.example.com" in hosts

    def test_allowed_fetch_hosts_from_env(self):
        """allowed_fetch_hosts should parse ALLOWED_FETCH_HOSTS env var."""
        with patch.dict(os.environ, {"ALLOWED_FETCH_HOSTS": "api.internal.com,data.internal.com"}):
            hosts = allowed_fetch_hosts()
            assert "api.internal.com" in hosts
            assert "data.internal.com" in hosts

    def test_allowed_fetch_hosts_whitespace_handling(self):
        """allowed_fetch_hosts should handle whitespace in env var."""
        with patch.dict(os.environ, {"ALLOWED_FETCH_HOSTS": "api.internal.com, data.internal.com , other.com"}):
            hosts = allowed_fetch_hosts()
            assert "api.internal.com" in hosts
            assert "data.internal.com" in hosts
            assert "other.com" in hosts


class TestFetch:
    """Test cases for the fetch function."""

    def test_fetch_rejects_unsafe_url(self):
        """fetch should reject URLs that are not safe."""
        with pytest.raises(ValueError, match="URL not allowed"):
            fetch("https://evil.com/data", allowed_hosts=frozenset(["api.example.com"]))

    @patch("app.requests.get")
    def test_fetch_success(self, mock_get):
        """fetch should return JSON response for safe URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = fetch("https://api.example.com/data", allowed_hosts=frozenset(["api.example.com"]))
        assert result == {"key": "value"}
        mock_get.assert_called_once()

    @patch("app.requests.get")
    def test_fetch_http_error(self, mock_get):
        """fetch should propagate HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="HTTP 404"):
            fetch("https://api.example.com/data", allowed_hosts=frozenset(["api.example.com"]))

    @patch("app.requests.get")
    def test_fetch_connection_error(self, mock_get):
        """fetch should propagate connection errors."""
        mock_get.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Connection refused"):
            fetch("https://api.example.com/data", allowed_hosts=frozenset(["api.example.com"]))

    @patch("app.requests.get")
    def test_fetch_timeout(self, mock_get):
        """fetch should respect timeout parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_get.return_value = mock_response

        fetch("https://api.example.com/data", timeout=10.0, allowed_hosts=frozenset(["api.example.com"]))
        mock_get.assert_called_once_with("https://api.example.com/data", timeout=10.0)
