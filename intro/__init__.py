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


# FUNCTIONS


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
