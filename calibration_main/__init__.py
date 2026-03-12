from otree.api import *
from otree.settings import DEBUG

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
        

class Subsession(BaseSubsession):
    players_per_group = models.IntegerField()
    initial_stock = models.IntegerField()
    initial_cash = models.FloatField()
    cost_per_second = models.FloatField()
    price_per_unit = models.FloatField()
    cost_per_click = models.FloatField()
    maximum_units = models.IntegerField()
    show_chain = models.BooleanField(initial=False)
    transfer_probability = models.FloatField()

    start_delay_seconds = models.IntegerField()
    leave_seconds = models.IntegerField()
    round_seconds = models.IntegerField()
    total_seconds = models.IntegerField()
    request_timeout_seconds = models.IntegerField()
    info_highlight_timeout_seconds = models.IntegerField()

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    inventory = models.IntegerField()
    balance = models.CurrencyField()

    last_inventory_update = models.FloatField()

    total_inventory_cost = models.CurrencyField(initial=0)
    total_request_cost = models.CurrencyField(initial=0)
    total_cost = models.CurrencyField(initial=0)
    total_revenue = models.CurrencyField(initial=0)
    total_profit = models.CurrencyField(initial=0)
    total_items_sold = models.IntegerField(initial=0)
    ecu_earnings = models.CurrencyField(initial=0)
    
    refreshed_page = models.BooleanField(initial=False)


# FUNCTIONS
def creating_session(subsession):
    sess = subsession.session
    players_per_group = sess.config.get('players_per_group', None)
    initial_stock = sess.config.get('initial_stock', None)
    initial_cash = sess.config.get('initial_cash', None)
    cost_per_second = sess.config.get('cost_per_second', None)
    price_per_unit = sess.config.get('price_per_unit', None)
    cost_per_click = sess.config.get('cost_per_click', None)
    maximum_units = sess.config.get('maximum_units_in_play', None)
    show_chain = sess.config.get('show_chain', False)

    start_delay_seconds = sess.config.get('start_delay_seconds', None)
    leave_seconds = sess.config.get('leave_seconds', None)
    round_seconds = sess.config.get('round_seconds', None)
    request_timeout_seconds = sess.config.get('request_timeout_seconds', None)
    info_highlight_timeout_seconds = sess.config.get('info_highlight_timeout_seconds', None)
    total_seconds = start_delay_seconds + round_seconds

    if any(var is None for var in
           [players_per_group, initial_stock, initial_cash, cost_per_second, price_per_unit, cost_per_click, maximum_units,
            show_chain, start_delay_seconds, leave_seconds, round_seconds, request_timeout_seconds,info_highlight_timeout_seconds]):
        raise ValueError("session not configured correctly")

    subsession.players_per_group = players_per_group
    subsession.initial_stock = initial_stock
    subsession.initial_cash = initial_cash
    subsession.cost_per_second = cost_per_second
    subsession.price_per_unit = price_per_unit
    subsession.cost_per_click = cost_per_click
    subsession.maximum_units = maximum_units
    subsession.show_chain = show_chain

    subsession.round_seconds = round_seconds
    subsession.start_delay_seconds = start_delay_seconds
    subsession.leave_seconds = leave_seconds
    subsession.request_timeout_seconds = request_timeout_seconds
    subsession.info_highlight_timeout_seconds = info_highlight_timeout_seconds
    subsession.total_seconds = total_seconds

    player_list = subsession.get_players()

    # assign endowments to players
    for player in player_list:
        player.inventory = initial_stock
        player.balance = initial_cash

# custom export of bonus payments for prolific.
def custom_export_prolific(players):
    sess = players[0].session
    for p in players:
        part = p.participant
        if part.vars.get("finished", False) and part.label:
            bonus_payment = round(int(part.payoff) * sess.config['real_world_currency_per_point'], 2)
            if bonus_payment > 0:
                yield [part.label, bonus_payment]

def common_vars_for_template(player):
    subs = player.subsession
    return {
        'balance': player.balance,
        'inventory': int(player.inventory),
        'total_request_cost': player.total_request_cost,
        'total_inventory_cost': player.total_inventory_cost,
        'total_cost': player.total_cost,
        'total_revenue': player.total_revenue,
        'total_profit': player.total_profit,
        'total_items_sold': player.total_items_sold,
        'num_players': subs.players_per_group,
        'show_chain': subs.show_chain,
        'info_highlight_timeout_seconds': subs.info_highlight_timeout_seconds,
        'training_start_delay_seconds': subs.start_delay_seconds,
        'training_seconds': subs.round_seconds,
        'allow_training_leave_seconds': subs.leave_seconds,
        'DEBUG': DEBUG
    }


# PAGES
class Preface(Page):
    @staticmethod
    def js_vars(player):
        return {
            "player_id": player.id_in_group,
            "current_page_name": player.participant._current_page_name
        }
    
    
class Task(Page):
    form_model = 'player'
    form_fields = [
        'total_revenue',
        'total_request_cost',
        'total_inventory_cost',
        'total_items_sold'
    ]
    
    def get_timeout_seconds(player):
        return player.subsession.total_seconds

    @staticmethod
    def js_vars(player):
        subs = player.subsession
        return {
            'own_id_in_group': player.id_in_group,
            'request_button_timeout_seconds': subs.request_timeout_seconds,
            'inventory_unit_cost_per_second': subs.cost_per_second,
            'inventory_unit_price': subs.price_per_unit,
            'inventory_click_price': subs.cost_per_click,
            'maximum_units': subs.maximum_units,
            **common_vars_for_template(player),
        }

    @staticmethod
    def vars_for_template(player):
        if not player.refreshed_page:
            player.refreshed_page = True
            
        return {
            **common_vars_for_template(player),
        }
    
    def before_next_page(player, timeout_happened):
        player.ecu_earnings = player.subsession.initial_cash + player.total_revenue - player.total_inventory_cost - player.total_request_cost
        player.participant.ecu_earnings = player.ecu_earnings
    
class Summary(Page):
    pass

page_sequence = [
    Preface,
    Task,
    Summary
]
