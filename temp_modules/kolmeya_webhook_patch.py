# Patch para adicionar webhook_url ao send_sms da Kolmeya

# Substituir o método send_sms em kolmeya_api.py

def send_sms(self, phone, message, reference=None, webhook_url=None):
    """
    Send single SMS

    Args:
        phone (str): Phone number (digits only, with country code)
        message (str): SMS message text
        reference (str): Custom reference ID (optional)
        webhook_url (str): URL for webhook callbacks (optional)

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

    # NOVO: Adiciona webhook_url se fornecido
    if webhook_url:
        payload['webhook_url'] = webhook_url

    payload['segment'] = self.segment_id
    return self._make_request('/sms/store', payload=payload)
