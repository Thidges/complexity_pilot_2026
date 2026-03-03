from otree.api import *
from datetime import datetime
from otree.settings import DEBUG
import os
import json

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent_given = models.BooleanField(
        label="I have read the information above and I want to participate in this experiment.",
        choices=[
            [True, "Yes"],
            [False, "No"],
        ],
        widget=widgets.RadioSelect,
    )

    confirm_read_understood = models.BooleanField(widget=widgets.CheckboxInput)
    voluntary_participation = models.BooleanField(widget=widgets.CheckboxInput)
    data_access_by_authorities = models.BooleanField(widget=widgets.CheckboxInput)
    data_anonymity = models.BooleanField(widget=widgets.CheckboxInput)
    data_publication = models.BooleanField(widget=widgets.CheckboxInput)
    future_research_use = models.BooleanField(widget=widgets.CheckboxInput)
    agree_to_participate = models.BooleanField(widget=widgets.CheckboxInput)
    confirm_info_reviewed_again = models.BooleanField(widget=widgets.CheckboxInput)


# FUNCTIONS



def consent_given_error_message(player, value):
    if not value:
        return "You must agree to participate in the experiment. If you do not agree, please contact the experimenter."
    return None

# PAGES

# Not currently used, but can be used to show a demo of the supply chain figure
class FigureDemo(Page):
    def js_vars(player):
        return {
            "own_id_in_group": player.id_in_group,
        }
    
class Welcome(Page):
    def vars_for_template(player):
        return {
            'participation_fee': player.session.config.get('participation_fee', '0.00 EUR')
        }
    
class ConsentRadboud(Page):
    form_model = 'player'
    form_fields = [
        'confirm_read_understood',
        'voluntary_participation',
        'data_access_by_authorities',
        'data_anonymity',
        'data_publication',
        'future_research_use',
        'agree_to_participate',
        'confirm_info_reviewed_again',
    ]
    
    def error_message(self, values):
        required_checks = [
            'confirm_read_understood',
            'voluntary_participation',
            'data_access_by_authorities',
            'data_anonymity',
            'data_publication',
            'future_research_use',
            'agree_to_participate',
            'confirm_info_reviewed_again'
        ]
        unchecked = [field for field in required_checks if not values.get(field)]
        if unchecked:
            return "You must check all boxes to continue."
        return None
    
    def vars_for_template(player):
        return {
            'consent_date': datetime.now().strftime("%Y-%m-%d"),
            'participation_fee': player.session.config.get('participation_fee', '0.00 EUR')
        }


class GameInstructions(Page):  
    def vars_for_template(player):
        sess = player.session
        rwc_pp = sess.config.get('real_world_currency_per_point', 0.01)
        hundred_ecu = 100 * rwc_pp
        players_per_group = sess.config.get('players_per_group', 5)
        show_chain = sess.config.get('show_chain', False)
        half = players_per_group // 2
        middle_pos = half if players_per_group % 2 == 0 else half + 1
        
        initial_cash_rounds = sess.config.get('initial_cash', None)
        initial_cash_rounds = [[int(x.strip()) for x in blocks.split(',')] for blocks in initial_cash_rounds.split(';')] if initial_cash_rounds else [[0]]
        initial_cash = initial_cash_rounds[0][0]

        ecu_earn = sess.config.get('price_per_unit', "10").split(';')[0]
        ecu_inventory_cost = sess.config.get('cost_per_second', "5").split(';')[0]
        
        return {
            'exchange_rate': f"100 ECU = {hundred_ecu:.2f} €",
            'num_participants': players_per_group if show_chain else "several",
            'show_chain': show_chain,
            'DEBUG': DEBUG,
            'own_id_in_group': middle_pos,
            'ecu_endowment': initial_cash ,
            'ecu_earn': ecu_earn,
            'ecu_inventory_cost': ecu_inventory_cost,
            'round_seconds': sess.config.get('round_seconds', 30),
            'num_rounds': sess.config.get('num_rounds', 1),
            'training_round_seconds': sess.config.get('training_round_seconds', 30),
        }
    
    
    @staticmethod
    def js_vars(player):
        players_per_group = player.session.config.get('players_per_group', 5)
        half = players_per_group // 2
        middle_pos = half if players_per_group % 2 == 0 else half + 1
        return {
            'own_id_in_group': middle_pos,
            'players_per_group': players_per_group,
            "player_id": player.id_in_group,
            "current_page_name": player.participant._current_page_name
        }

page_sequence = [
    # FigureDemo, 
    Welcome,
    ConsentRadboud, 
    GameInstructions
]
