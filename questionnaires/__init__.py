from otree.api import *

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
    gender = models.StringField(label="What is your gender?", widget=widgets.RadioSelect, choices=[
        ('female', 'female'),
        ('male', 'male'),
        ('other', 'other'),
        ('prefer_not_to_say', 'prefer not to tell')])
    birth_year = models.IntegerField(
        label="In which year are you born?",
        choices=list(range(2005, 1900, -1)))
    # age = models.IntegerField(label="How old are you?", min=16)
    #student_or_working = models.StringField(label="Are you currently a student or working?", widget=widgets.RadioSelect, choices=[
        #('student', 'student'),
        #('working', 'working')])
    # education_level = models.StringField(label="What is your highest level of education?", widget=widgets.RadioSelect, choices=[
    #     ('high_school', 'High School Diploma'),
    #     ('bachelor', "Bachelor's Degree"),
    #     ('master', "Master's Degree"),
    #     ('phd', "PhD or equivalent"),
    #     ('other', 'other')])
    risk_general = models.IntegerField(label="How would you rate your willingness to take risks generally in life? (1 – never, 7 – always)”", widget=widgets.RadioSelectHorizontal, choices=[i for i in range(1, 8)])
    instructions_understood = models.IntegerField(label="How well did you understand the instructions in the experiment? (1 – not at all, 5 – everything was clear)", widget=widgets.RadioSelectHorizontal, choices=[i for i in range(1, 6)])
    # specific_strategy = models.BooleanField(label="Did you follow any specific strategy in this experiment?", widget=widgets.RadioSelect, choices=[(True, 'Yes'), (False, 'No')])
    strategy_text = models.LongStringField(label="Briefly describe this strategy you applied in this study.")
    comments = models.LongStringField(label="Is there anything you like to share about the experiment (suggestions, remaining questions, other feedback)?", blank=True)


# FUNCTIONS

    
# PAGES
class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['gender',
                   'birth_year',
                   'risk_general',
                   'instructions_understood', 
                   'strategy_text',
                   'comments'
    ]


    def before_next_page(player, timeout_happened):
        player.participant.finished = True
            

class FinalScreen(Page):
    def vars_for_template(player):
        sess = player.session
        pppf = player.participant.payoff_plus_participation_fee()
        ecu_earnings = player.participant.vars.get('ecu_earnings', 0)
        final_balance = player.participant.vars.get('final_balance', 0)
        if final_balance > 0:
            rwc_earnings = round(int(final_balance) * sess.config['real_world_currency_per_point'], 2)
        else:
            rwc_earnings = 0

        base_payment_link = sess.config.get('payment_link', 'https://example.com')
        payment_link = f"{base_payment_link}?CodeA={player.participant.code}&Amount={float(pppf):.2f}"
        return {
            'participation_fee': sess.config['participation_fee'],
            'final_payment': pppf,
            'final_balance': final_balance,
            'ecu_earnings': ecu_earnings,
            'rwc_earnings': f"€{rwc_earnings:.2f}",
            'payment_link': payment_link,
        }


page_sequence = [Questionnaire, FinalScreen]
