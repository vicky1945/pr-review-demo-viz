import pytest
from unittest.mock import patch, MagicMock

from app import divide, is_safe_url, fetch


class TestDivide:
    """Tests for divide function."""

    def test_divide_success(self):
        """divide should return correct result."""
        assert divide(10, 2) == 5
        assert divide(9, 3) == 3
        assert divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        """divide should raise ValueError on zero division."""
        with pytest.raises(ValueError, match="division by zero"):
            divide(10, 0)


class TestIsSafeUrl:
    """Tests for is_safe_url function."""

    def test_allowed_url(self):
        """Should allow api.example.com."""
        assert is_safe_url("https://api.example.com/data") is True
        assert is_safe_url("http://api.example.com/data") is True

    def test_disallowed_host(self):
        """Should reject non-allowlisted hosts."""
        assert is_safe_url("https://evil.com/data") is False
        assert is_safe_url("https://other.com/data") is False

    def test_localhost_blocked(self):
        """Should block localhost/loopback."""
        assert is_safe_url("https://localhost/data") is False
        assert is_safe_url("https://127.0.0.1/data") is False
        assert is_safe_url("https://0.0.0.0/data") is False

    def test_invalid_scheme(self):
        """Should reject non-http(s) schemes."""
        assert is_safe_url("ftp://api.example.com/data") is False
        assert is_safe_url("gopher://api.example.com/data") is False

    def test_malformed_url(self):
        """Should handle malformed URLs."""
        assert is_safe_url("not-a-url") is False
        assert is_safe_url("") is False


class TestFetch:
    """Tests for fetch function."""

    def test_fetch_rejects_unsafe_url(self):
        """fetch should reject unsafe URLs."""
        with pytest.raises(ValueError, match="URL not allowed"):
            fetch("https://evil.com/data")

    @patch("app.requests.get")
    def test_fetch_success(self, mock_get):
        """fetch should return JSON dict from safe URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = fetch("https://api.example.com/data")
        assert result == {"key": "value"}
        mock_get.assert_called_once_with("https://api.example.com/data", timeout=5.0)

    @patch("app.requests.get")
    def test_fetch_with_custom_timeout(self, mock_get):
        """fetch should respect timeout parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_get.return_value = mock_response

        fetch("https://api.example.com/data", timeout=10.0)
        mock_get.assert_called_once_with("https://api.example.com/data", timeout=10.0)

    @patch("app.requests.get")
    def test_fetch_rejects_non_dict_json(self, mock_get):
        """fetch should reject non-dict JSON responses."""
        mock_response = MagicMock()
        mock_response.json.return_value = ["list", "not", "dict"]
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Expected JSON dict"):
            fetch("https://api.example.com/data")

    @patch("app.requests.get")
    def test_fetch_http_error(self, mock_get):
        """fetch should propagate HTTP errors."""
        mock_get.side_effect = Exception("HTTP 404")
        
        with pytest.raises(Exception, match="HTTP 404"):
            fetch("https://api.example.com/data")
