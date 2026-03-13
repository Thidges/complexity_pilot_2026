from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    def play_round(self):
        yield Consent, {
            'confirm_read_understood': True,
            'voluntary_participation': True,
            'data_publication': True,
            'future_research_use': True,
            'agree_to_participate': True,
        }
        yield GameInstructions