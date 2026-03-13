from otree.api import *
from datetime import datetime
from otree.settings import DEBUG, REAL_WORLD_CURRENCY_CODE

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
    confirm_read_understood = models.BooleanField(widget=widgets.CheckboxInput)
    voluntary_participation = models.BooleanField(widget=widgets.CheckboxInput)
    data_publication = models.BooleanField(widget=widgets.CheckboxInput)
    future_research_use = models.BooleanField(widget=widgets.CheckboxInput)
    agree_to_participate = models.BooleanField(widget=widgets.CheckboxInput)

    comp_request_cost = models.IntegerField(label="Assume you make 5 requests of which 3 are successful and 2 are not successful. How many ECU did it cost to make these 5 requests?")
    comp_inventory_cost = models.IntegerField(label="Assume you hold 2 units in inventory for 2 seconds. How many ECU did it cost to hold this inventory?")
    comp_revenue = models.IntegerField(label="Assume you have 1 unit in your inventory. Your successor requests 1 unit from you. How many ECU do you earn from the transfer?")

# Functions
def comp_request_cost_error_message(player, value):
    actual_cost = player.session.config.get('cost_per_click', 0) * 5
    if value < actual_cost:
        return "Check your calculation! The request cost you entered is too low."
    if value > actual_cost:
        return "Check your calculation! The request cost you entered is too high."
    return None

def comp_inventory_cost_error_message(player, value):
    actual_cost = player.session.config.get('cost_per_second', 0) * 2 * 2  # 2 units times 2 seconds
    if value < actual_cost:
        return "Check your calculation! The inventory cost you entered is too low."
    if value > actual_cost:
        return "Check your calculation! The inventory cost you entered is too high."
    return None

def comp_revenue_error_message(player, value):
    actual_revenue = player.session.config.get('price_per_unit', 0)
    if value < actual_revenue:
        return "Check your calculation! The revenue you entered is too low."
    if value > actual_revenue:
        return "Check your calculation! The revenue you entered is too high."
    return None

# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = [
        'confirm_read_understood',
        'voluntary_participation',
        'data_publication',
        'future_research_use',
        'agree_to_participate'
    ]
    
    def error_message(self, values):
        required_checks = [
            'confirm_read_understood',
            'voluntary_participation',
            'data_publication',
            'future_research_use',
            'agree_to_participate',
        ]
        unchecked = [field for field in required_checks if not values.get(field)]
        if unchecked:
            return "You must check all boxes to continue."
        return None
    
    def vars_for_template(player):
        return {
            'participation_fee': player.session.config.get('participation_fee', '0.00 EUR')
        }


class GameInstructions(Page):
    form_model = 'player'

    def get_form_fields(player):
        sess = player.session
        cost_per_click = sess.config.get('cost_per_click', 2)
        if cost_per_click == 0:
            return ['comp_inventory_cost', 'comp_revenue']
        return ['comp_request_cost', 'comp_inventory_cost', 'comp_revenue']

    def vars_for_template(player):
        sess = player.session
        rwc_pp = sess.config.get('real_world_currency_per_point', 0.01)
        hundred_ecu = 100 * rwc_pp
        players_per_group = sess.config.get('players_per_group', 5)
        show_chain = sess.config.get('show_chain', False)
        half = players_per_group // 2
        middle_pos = half if players_per_group % 2 == 0 else half + 1
        
        initial_cash = sess.config.get('initial_cash', None)

        ecu_earn = sess.config.get('price_per_unit', 10)
        ecu_inventory_cost = sess.config.get('cost_per_second', 5)
        ecu_request_cost = sess.config.get('cost_per_click', 2)

        round_seconds = sess.config.get('round_seconds', 30)
        round_minutes = round_seconds/60

        return {
            'exchange_rate': f"100 ECU = {hundred_ecu:.2f} {REAL_WORLD_CURRENCY_CODE}",
            'num_participants': players_per_group if show_chain else "several",
            'show_chain': show_chain,
            'DEBUG': DEBUG,
            'own_id_in_group': middle_pos,
            'ecu_endowment': initial_cash ,
            'ecu_earn': ecu_earn,
            'ecu_inventory_cost': ecu_inventory_cost,
            'ecu_request_cost': ecu_request_cost,
            'round_seconds': round_seconds,
            'round_minutes': round_minutes
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
    Consent, 
    GameInstructions
]
