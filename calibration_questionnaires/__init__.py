from otree.api import *
from otree.settings import DEBUG

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaires'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    strategy_text = models.LongStringField(label="Briefly describe the strategy that you followed in the interactive task:", blank=True)
    comments = models.LongStringField(label="Is there anything you like to share about the study (suggestions, remaining questions, other feedback)?", blank=True)


# PAGES
def creating_session(subsession):
    if subsession.session.is_demo:
        return
    if not subsession.session.config.get("prolific_completion_url", False):
        raise ValueError("You must set the Prolific Completion URL in the session config!")


class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['strategy_text', 'comments']
    
    def before_next_page(player, timeout_happened):
        participant_ecu_earnings = player.participant.vars.get('ecu_earnings', 0)
        if participant_ecu_earnings > 0:
            player.payoff = participant_ecu_earnings
        else:
            player.payoff = 0


class FinalScreen(Page):
    def vars_for_template(player):
        sess = player.session
        pppf = player.participant.payoff_plus_participation_fee()
        ecu_earnings = player.participant.vars.get('ecu_earnings', 0)
        usd_earnings = int(ecu_earnings) * sess.config['real_world_currency_per_point']
        
        return {
            'participation_fee': sess.config['participation_fee'],
            'final_payment': pppf,
            'ecu_earnings': ecu_earnings,
            'usd_earnings': usd_earnings,
            'prolific_url': sess.config.get('prolific_completion_url', '')
        }
    
    def before_next_page(player, timeout_happened):
        player.participant.finished = True

page_sequence = [Questionnaire, FinalScreen]
