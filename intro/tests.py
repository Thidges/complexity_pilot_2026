from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    def play_round(self):
        yield ConsentRadboud, {
            'confirm_read_understood': True,
            'voluntary_participation': True,
            'data_access_by_authorities': True,
            'data_anonymity': True,
            'data_publication': True,
            'future_research_use': True,
            'agree_to_participate': True,
            'confirm_info_reviewed_again': True
        }
        
        answers = {
            'comp_request_cost': self.session.config.get('cost_per_click', 0) * 2,
            'comp_inventory_cost': self.session.config.get('cost_per_second', 0) * 2 * 2,
        }
        if self.session.config.get('cost_per_click', 2) != 0:
            answers.update({'comp_revenue': self.session.config.get('price_per_unit', 0)})

        yield GameInstructions, answers