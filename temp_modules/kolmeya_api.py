# -*- coding: utf-8 -*-
import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class KolmeyaAPI:
    """
    Kolmeya SMS API Wrapper

    Complete implementation of Kolmeya REST API v1
    Documentation: https://kolmeya.com.br/docs/api/
    """

    BASE_URL = "https://kolmeya.com.br/api/v1"

    def __init__(self, token, segment_id=109):
        """
        Initialize Kolmeya API client

        Args:
            token (str): Bearer token (e.g., "Bearer xxxxx...")
            segment_id (int): Segment/cost center ID (default: 109 - CORPORATIVO)
        """
        if not token:
            raise ValueError("API token is required")

        # Ensure token has "Bearer " prefix
        self.token = token if token.startswith('Bearer ') else f'Bearer {token}'
        self.segment_id = segment_id
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }

    def _make_request(self, endpoint, method='POST', payload=None, timeout=30):
        """
        Make HTTP request to Kolmeya API

        Args:
            endpoint (str): API endpoint (e.g., '/sms/store')
            method (str): HTTP method (POST, GET)
            payload (dict): Request payload
            timeout (int): Request timeout in seconds

        Returns:
            dict: JSON response from API

        Raises:
            UserError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method == 'POST':
                response = requests.post(url, json=payload, headers=self.headers, timeout=timeout)
            elif method == 'GET':
                response = requests.get(url, params=payload, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check rate limiting
            rate_remaining = response.headers.get('X-RateLimit-Remaining')
            if rate_remaining and int(rate_remaining) < 50:
                _logger.warning(f"Kolmeya rate limit low: {rate_remaining} requests remaining")

            # Handle HTTP errors
            if response.status_code == 429:
                raise UserError("Rate limit exceeded. Please wait a few minutes.")
            elif response.status_code >= 400:
                error_msg = response.json().get('errors', [response.text]) if response.text else 'Unknown error'
                raise UserError(f"Kolmeya API error ({response.status_code}): {error_msg}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise UserError("Request to Kolmeya API timed out")
        except requests.exceptions.RequestException as e:
            _logger.error(f"Kolmeya API request failed: {e}")
            raise UserError(f"Failed to communicate with Kolmeya: {str(e)}")

    # ========== SMS Sending ==========

    def send_sms(self, phone, message, reference=None):
        """
        Send single SMS

        Args:
            phone (str): Phone number (digits only, with country code)
            message (str): SMS message text
            reference (str): Custom reference ID (optional)

        Returns:
            dict: Response with 'id' (job ID), 'valids', 'invalids', etc.
        """
        payload = {
            'messages': [{
                'phone': phone,
                'message': message,
            }]
        }

        if reference:
            payload['messages'][0]['reference'] = reference

        return self._make_request('/sms/store', payload=payload)

    def send_batch(self, messages_list, max_batch_size=1000):
        """
        Send batch of SMS messages

        Args:
            messages_list (list): List of dicts with 'phone', 'message', 'reference'
            max_batch_size (int): Maximum messages per batch (Kolmeya limit: 1000)

        Returns:
            list: List of responses (one per batch)
        """
        results = []

        for i in range(0, len(messages_list), max_batch_size):
            batch = messages_list[i:i+max_batch_size]
            payload = {'messages': batch}

            result = self._make_request('/sms/store', payload=payload)
            results.append(result)

            _logger.info(f"Batch {i//max_batch_size + 1} sent: {len(batch)} messages, Job ID: {result.get('id')}")

        return results if len(results) > 1 else results[0]

    # ========== Status Checking ==========

    def check_job_status(self, job_id):
        """
        Check status of a job (batch of messages)

        Args:
            job_id (str): Job ID from send response

        Returns:
            dict: Job status with 'id', 'status', 'status_code', 'messages'
        """
        payload = {'id': job_id}
        return self._make_request('/sms/status/request', payload=payload)

    def check_message_status(self, message_id):
        """
        Check status of a single message

        Args:
            message_id (str): Message ID from send response

        Returns:
            dict: Message status
        """
        payload = {'id': message_id}
        return self._make_request('/sms/status/message', payload=payload)

    # ========== Balance & Account ==========

    def get_balance(self):
        """
        Get account balance

        Returns:
            dict: Balance information with 'saldo' (balance in R$)
        """
        return self._make_request('/sms/balance')

    # ========== Templates ==========

    def get_templates(self):
        """
        Get SMS templates configured in Kolmeya

        Returns:
            dict: Templates data
        """
        return self._make_request('/sms/modelos')

    # ========== Blacklist ==========

    def add_to_blacklist(self, phones_list):
        """
        Add phone numbers to blacklist

        Args:
            phones_list (list): List of phone numbers (strings)

        Returns:
            dict: Response
        """
        payload = {
            'phones': [{'phone': phone} for phone in phones_list]
        }
        return self._make_request('/sms/blacklist/adicionar', payload=payload)

    def remove_from_blacklist(self, phones_list):
        """
        Remove phone numbers from blacklist

        Args:
            phones_list (list): List of phone numbers (strings)

        Returns:
            dict: Response
        """
        payload = {
            'phones': [{'phone': phone} for phone in phones_list]
        }
        return self._make_request('/sms/blacklist/remover', payload=payload)

    def get_blacklist(self):
        """
        Get blacklist

        Returns:
            dict: Blacklist data
        """
        return self._make_request('/sms/blacklist')

    # ========== Replies ==========

    def get_replies(self, page=1):
        """
        Get SMS replies (last 7 days)

        Args:
            page (int): Page number for pagination

        Returns:
            dict: Replies data
        """
        payload = {'page': page}
        return self._make_request('/sms/respostas', payload=payload)

    # ========== Reports ==========

    def get_report(self, start_date, end_date, page=1):
        """
        Get SMS report for date range

        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            page (int): Page number

        Returns:
            dict: Report data
        """
        payload = {
            'data_inicio': start_date,
            'data_fim': end_date,
            'page': page
        }
        return self._make_request('/sms/relatorio', payload=payload)
