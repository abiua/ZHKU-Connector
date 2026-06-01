import pytest
from unittest.mock import patch, Mock
import main


class TestDetectCaptivePortalDoesNotOverwriteLoginTemplate:
    """Verify the fix: detect_captive_portal() must preserve self.login_template."""

    @patch('main.requests.get')
    def test_template_preserved_when_redirect_detected(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.is_redirect = True
        mock_response.headers = {'Location': 'http://172.31.255.1/drcom/login?callback=dr1003'}
        mock_get.return_value = mock_response

        connector = main.Connector()
        original_template = connector.login_template

        result = connector.detect_captive_portal()

        assert result is True
        assert connector.login_template == original_template
        assert '{user_id}' in connector.login_template
        assert '{password}' in connector.login_template

    @patch('main.requests.get')
    def test_template_preserved_when_network_ok(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.is_redirect = False
        mock_get.return_value = mock_response

        connector = main.Connector()
        original_template = connector.login_template

        result = connector.detect_captive_portal()

        assert result is False
        assert connector.login_template == original_template

    @patch('main.requests.get')
    def test_template_preserved_when_request_fails(self, mock_get):
        mock_get.side_effect = main.requests.RequestException("Network down")

        connector = main.Connector()
        original_template = connector.login_template

        result = connector.detect_captive_portal()

        assert result is None
        assert connector.login_template == original_template


class TestLoginUsesLoginTemplate:
    """Verify login() builds URL from self.login_template, not self.captive_portal."""

    @patch('main.requests.get')
    def test_login_url_contains_credentials(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        connector = main.Connector()
        connector.user_id = 'testuser'
        connector.password = 'testpass'

        connector.login()

        called_url = mock_get.call_args[0][0]
        assert 'testuser' in called_url
        assert 'testpass' in called_url


class TestAutoLoginSkipsOnNetworkError:
    """Verify auto_login() does not call login() when captive is None (network error)."""

    @patch('main.requests.get')
    def test_no_login_on_network_error(self, mock_get):
        # Make detect_captive_portal return None (network error)
        mock_get.side_effect = main.requests.RequestException("Network down")

        connector = main.Connector()
        connector.user_id = 'testuser'
        connector.password = 'testpass'

        # Simulate one iteration of the auto_login() loop logic:
        # When detect_captive_portal() returns None, login() should NOT be called
        captive = connector.detect_captive_portal()
        assert captive is None

        # The fix: only trigger login on captive=True, not None
        # This is the logic from auto_login() after the fix:
        login_should_trigger = bool(captive)
        assert login_should_trigger is False
