from otree.api import *
from datetime import datetime

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
    data_publication = models.BooleanField(widget=widgets.CheckboxInput)
    future_research_use = models.BooleanField(widget=widgets.CheckboxInput)
    agree_to_participate = models.BooleanField(widget=widgets.CheckboxInput)

    comp_request_cost = models.IntegerField(
        label="Assume you make 2 requests of which 1 is successful and 1 is not successful. How many ECU did it cost to make these 2 requests?")
    comp_inventory_cost = models.IntegerField(
        label="Assume you hold 2 units in inventory for 2 seconds. How many ECU did it cost to hold this inventory?")
    comp_revenue = models.IntegerField(
        label="Assume you have 1 unit in your inventory. Your successor requests 1 unit from you. How many ECU do you earn from the transfer?")


# FUNCTIONS
# Functions
def comp_request_cost_error_message(player, value):
    actual_cost = player.session.config.get('cost_per_click', 0) * 2
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


def consent_given_error_message(player, value):
    if not value:
        return "You must agree to participate in the experiment. If you do not agree, please contact the experimenter."
    return None

# PAGES
    
class ConsentRadboud(Page):
    form_model = 'player'
    form_fields = [
        'confirm_read_understood',
        'voluntary_participation',
        'data_publication',
        'future_research_use',
        'agree_to_participate',
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



page_sequence = [
    ConsentRadboud
]
