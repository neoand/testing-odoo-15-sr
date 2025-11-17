import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from itertools import groupby
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


class KolmeyaCampaigns(models.Model):
    _name = 'kolmeya.campaigns'
    _description = 'Campanhas'

    name = fields.Char('Nome campanha', required=True,)
    campaign_id = fields.Char('id campanha')

    @api.model
    def find_campaign(self, job_value):
        # Buscar el registro basándose en el valor de "job"
        campaign = self.search([('campaign_id', '=', job_value)], limit=1)

        if campaign:
            # Si se encuentra el registro, devolver sus valores
            return {
                'name': campaign.name,
                'campaign_id': campaign.campaign_id,
            }
        else:
            # Si no se encuentra, devolver un valor predeterminado (por ejemplo, "NA")
            return {
                'name': '..',
                'campaign_id': '..',
            }
