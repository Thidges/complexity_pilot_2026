import json
import math
import random
import time
from collections import defaultdict

from otree.api import *
from otree.settings import DEBUG, TREATMENTS, REAL_WORLD_CURRENCY_CODE

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'ringsupplychain'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1 


class Subsession(BaseSubsession):
    cost_per_second = models.FloatField()
    cost_per_click = models.FloatField()
    price_per_unit = models.FloatField()
    start_delay_seconds = models.IntegerField()
    leave_seconds = models.IntegerField()
    round_seconds = models.IntegerField()
    training_round_seconds = models.IntegerField()
    total_seconds = models.IntegerField()
    training_total_seconds = models.IntegerField()
    show_chain = models.BooleanField(initial=False)
    auto_play = models.BooleanField(initial=False)
    request_timeout_seconds = models.IntegerField()
    info_highlight_timeout_seconds = models.IntegerField()
    countdown_seconds = models.IntegerField()
    maximum_units = models.IntegerField()
    welcome_message = models.BooleanField(initial=False)

class Group(BaseGroup):
    start_time = models.FloatField()
    group_size = models.IntegerField()
    treatment = models.StringField()
    show_info = models.BooleanField(initial=False)
    initial_stock = models.IntegerField()
    initial_cash = models.CurrencyField()

class Player(BasePlayer):
    inventory = models.IntegerField()
    balance = models.CurrencyField()
    
    last_inventory_update = models.FloatField()
    init_time = models.FloatField()
    
    total_cost = models.CurrencyField(initial=0)
    total_request_cost = models.CurrencyField(initial=0)
    total_inventory_cost = models.CurrencyField(initial=0)
    total_revenue = models.CurrencyField(initial=0)
    total_profit = models.CurrencyField(initial=0)
    total_items_sold = models.IntegerField(initial=0)

    comp_request_cost = models.IntegerField(
        label="Assume you make 2 requests of which 1 is successful and 1 is not successful. How many ECU did it cost to make these 2 requests?")
    comp_inventory_cost = models.IntegerField(
        label="Assume you hold 2 units in inventory for 2 seconds. How many ECU did it cost to hold this inventory?")
    comp_revenue = models.IntegerField(
        label="Assume you have 1 unit in your inventory. Your successor requests 1 unit from you. How many ECU do you earn from the transfer?")
    
    proposed_start_time = models.FloatField()

    
    def get_predecessor(self):
        if self.id_in_group == 1:
            return self.group.group_size
        else:
            return self.id_in_group - 1

    def get_successor(self):
        if self.id_in_group == self.group.group_size:
            return 1
        else:
            return self.id_in_group + 1
    
class Requests(ExtraModel):
    created = models.FloatField()
    session = models.Link(Subsession)
    group_id = models.IntegerField()
    round = models.IntegerField()
    requested_from_id = models.IntegerField()
    requested_by_id = models.IntegerField()
    units = models.IntegerField()
    transferred = models.BooleanField()
    from_inventory = models.IntegerField()
    from_balance = models.CurrencyField()
    to_inventory = models.IntegerField()
    to_balance = models.CurrencyField()
    kind = models.StringField(choices=['request', 'init'], default='request')

# FUNCTIONS
def shuffled(l):
    random.shuffle(l)
    return l

def creating_session(subsession):
    sess = subsession.session
    request_timeout_seconds = sess.config.get('request_timeout_seconds', None)
    info_highlight_timeout_seconds = sess.config.get('info_highlight_timeout_seconds', None)
    countdown_seconds = sess.config.get('countdown_seconds', 5)
    round_seconds = sess.config.get('round_seconds', None)
    training_round_seconds = sess.config.get('training_round_seconds', None)
    start_delay_seconds = sess.config.get('start_delay_seconds', None)
    leave_seconds = sess.config.get('leave_seconds', None)
    cost_per_second = sess.config.get('cost_per_second', None)
    cost_per_click = sess.config.get('cost_per_click', None)
    price_per_unit = sess.config.get('price_per_unit', None)
    show_chain = sess.config.get('show_chain', False)
    auto_play = sess.config.get('auto_play', False)
    welcome_message = sess.config.get('welcome_message', False)
       
    total_seconds = countdown_seconds + round_seconds
    training_total_seconds = countdown_seconds + training_round_seconds
    
    if any(var is None for var in [cost_per_second, cost_per_click, price_per_unit, round_seconds, show_chain, request_timeout_seconds, info_highlight_timeout_seconds, countdown_seconds]):
        raise ValueError("session not configured correctly")
    
    # assign variables
    subsession.cost_per_second = cost_per_second
    subsession.cost_per_click = cost_per_click
    subsession.price_per_unit = price_per_unit
    subsession.round_seconds = round_seconds
    subsession.training_round_seconds = training_round_seconds
    subsession.start_delay_seconds = start_delay_seconds
    subsession.leave_seconds = leave_seconds
    subsession.show_chain = show_chain
    subsession.auto_play = auto_play
    subsession.request_timeout_seconds = request_timeout_seconds
    subsession.info_highlight_timeout_seconds = info_highlight_timeout_seconds
    subsession.total_seconds = total_seconds
    subsession.training_total_seconds = training_total_seconds
    subsession.countdown_seconds = countdown_seconds
    subsession.welcome_message = welcome_message

    subsession.maximum_units = 10
    
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

def live_inventory(player):
    # get current time
    current_time = time.time()

    # get time delta
    last_inventory_time = player.field_maybe_none('last_inventory_update')
    if last_inventory_time is None:
        last_inventory_time = current_time
    time_delta = current_time - last_inventory_time
    

    # calculate cost
    old_inventory = player.inventory
    inventory_cost = time_delta * player.subsession.cost_per_second * old_inventory

    # update total costs
    player.total_inventory_cost += inventory_cost
    player.total_cost += inventory_cost

    # update balance
    player.balance -= inventory_cost

    # update profit
    player.total_profit = player.total_revenue - player.total_cost

    # update last inventory update time
    player.last_inventory_update = current_time

    # inventories
    predecessor = player.group.get_player_by_id(player.get_predecessor())
    successor = player.group.get_player_by_id(player.get_successor())

    resp = {
        'type': 'init_response',
        'data': {
            'inventory': player.inventory,
            'balance': player.balance,
            'cost': player.total_cost,
            'revenue': player.total_revenue,
            'profit': player.total_profit,
            'items_sold': player.total_items_sold,
            'pre_inventory': predecessor.inventory,
            'suc_inventory': successor.inventory
        }
    }
    
    return {player.id_in_group: resp}

def live_request(player, data):
    take_from = player.get_predecessor()
    units = data['units']

    group = player.group
    subsession = player.subsession
    take_from_player = group.get_player_by_id(take_from)
    give_to_player = player

    # get current time
    current_time = time.time()

    from_revenue = 0
    transferred = False

    # charge click cost to requesting player unconditionally
    click_cost = subsession.cost_per_click
    give_to_player.balance -= click_cost
    give_to_player.total_cost += click_cost
    give_to_player.total_request_cost += click_cost
    give_to_player.total_profit = give_to_player.total_revenue - give_to_player.total_cost

    # Check if the take_from player has enough inventory
    if take_from_player.inventory >= units:
        # transfer from player costs
        from_last_update = take_from_player.last_inventory_update
        from_time_delta = current_time - from_last_update
        from_old_inventory = take_from_player.inventory
        from_cost = from_time_delta * subsession.cost_per_second * from_old_inventory
        take_from_player.total_inventory_cost += from_cost
        take_from_player.total_cost += from_cost
        
        # transfer to player costs
        to_last_update = give_to_player.last_inventory_update
        to_time_delta = current_time - to_last_update
        to_old_inventory = give_to_player.inventory
        to_cost = to_time_delta * subsession.cost_per_second * to_old_inventory
        give_to_player.total_inventory_cost += to_cost
        give_to_player.total_cost += to_cost

        # update inventory 
        take_from_player.inventory -= units
        take_from_player.total_items_sold += units
        give_to_player.inventory += units
        
        # update balance and revenue
        from_revenue = units * subsession.price_per_unit
        from_balance_change = from_revenue - from_cost
        take_from_player.balance += from_balance_change
        take_from_player.total_revenue += from_revenue
        
        to_balance_change = -1 * to_cost
        give_to_player.balance += to_balance_change
        
        # update profit
        take_from_player.total_profit = take_from_player.total_revenue - take_from_player.total_cost
        give_to_player.total_profit = give_to_player.total_revenue - give_to_player.total_cost
        
        # update last inventory update time
        take_from_player.last_inventory_update = current_time
        give_to_player.last_inventory_update = current_time
        
        transferred = True
        
    # request record
    Requests.create(
        created=current_time,
        session=take_from_player.subsession,
        group_id=group.id_in_subsession,
        round=player.round_number,
        requested_from_id=take_from_player.id_in_group,
        requested_by_id=give_to_player.id_in_group,
        units=units,
        transferred=transferred,
        from_inventory=take_from_player.inventory,
        from_balance=take_from_player.balance,
        to_inventory=give_to_player.inventory,
        to_balance=give_to_player.balance,
    )
    
    resp = {
        'type': 'status',
        'data': {
            'to_player': give_to_player.id_in_group,
            'from_player': take_from_player.id_in_group,
            'to_inventory': give_to_player.inventory,
            'to_balance': give_to_player.balance,
            'to_cost': give_to_player.total_cost,
            'to_revenue': give_to_player.total_revenue,
            'to_profit': give_to_player.total_profit,
            'from_inventory': take_from_player.inventory,
            'from_balance': take_from_player.balance,
            'from_cost': take_from_player.total_cost,
            'from_revenue': take_from_player.total_revenue,
            'from_profit': take_from_player.total_profit,
            'units': units,
            'cash': from_revenue,
            'transferred': transferred,
        }
    }
    
    return {0: resp}

def common_vars_for_template(player):
    subs = player.subsession
    group = player.group
    return {
        'balance': player.balance,
        'inventory': int(player.inventory),
        'price_per_unit': subs.price_per_unit,
        'total_cost': player.total_cost,
        'total_revenue': player.total_revenue,
        'total_profit': player.total_profit,
        'total_items_sold': player.total_items_sold,
        'num_players': group.group_size,
        'show_info': group.show_info,
        'treatment': group.treatment,
        'cost_per_click': subs.cost_per_click,
        'show_chain': subs.show_chain,
        'auto_play': subs.auto_play,
        'round_seconds': subs.round_seconds,
        'total_seconds': subs.total_seconds,
        'leave_seconds': subs.leave_seconds,
        'start_delay_seconds': subs.start_delay_seconds,
        'training_round_seconds': subs.training_round_seconds,
        'request_button_timeout_seconds': subs.request_timeout_seconds,
        'info_highlight_timeout_seconds': subs.info_highlight_timeout_seconds,
        'countdown_seconds': subs.countdown_seconds,
        'DEBUG': DEBUG
    }

def finalize_round(group):
    subs = group.subsession
    round_seconds = subs.round_seconds
    cost_per_second = subs.cost_per_second
    for player in group.get_players():
        # first we figure out when the last update of the inventory took place relative to the expected end of round time
        init_time = player.field_maybe_none('init_time')
        if init_time is None:
            init_time = 0
        end_time = init_time + round_seconds
        last_update = player.field_maybe_none('last_inventory_update')
        if last_update is None:
            last_update = 0
        time_to_end_of_round = end_time - last_update
        
        # print('init_time', init_time)
        # print('end_time', end_time)
        # print('last_update', last_update)
        # print('time_to_end_of_round', time_to_end_of_round)
        # if there was time left between last update and the expected end of round, we need to account for costs.
        if time_to_end_of_round > 0:
            # calculate cost
            old_inventory = player.inventory
            cost = time_to_end_of_round * cost_per_second * old_inventory

            # update total cost, balance, and profit
            player.total_inventory_cost += cost
            player.total_cost += cost
            player.balance -= cost
            player.total_profit = player.total_revenue - player.total_cost
            
            # print('old_inventory', old_inventory)
            # print('cost', cost)
            # print('total_cost', player.total_cost)
            # print('balance', player.balance)
            # print('total_profit', player.total_profit)
        
        # store payment data on the participant
        player.participant.vars['ecu_earnings'] = int(player.total_profit)

        

def start_time_check(player: Player, data):
    current_time = time.time()
    player.proposed_start_time = data['start_time']

    subs = player.subsession
    group = player.group
    group_players = group.get_players()
    proposed_start_times = list()
    for p in group_players:
        if p.field_maybe_none('proposed_start_time') is not None:
            proposed_start_times.append(p.proposed_start_time)

    if len(proposed_start_times) == group.group_size:
        if player.group.field_maybe_none('start_time') is not None:
            return {0: {
                'type': 'start_time_decision',
                'start_time': group.start_time
            }}

        decision_candidate = max(proposed_start_times)
        if decision_candidate > current_time + subs.countdown_seconds:
            selected_time = decision_candidate
        else:
            selected_time = current_time + subs.countdown_seconds

        group.start_time = selected_time

        for p in group_players:
            if p.field_maybe_none('last_inventory_update') is None:
                p.last_inventory_update = selected_time

            Requests.create(
                created=selected_time,
                # init is triggered on page load, but the countdown starts after the page is loaded
                session=subs,
                group_id=p.group.id_in_subsession,
                round=p.round_number,
                requested_from_id=p.id_in_group,
                requested_by_id=p.id_in_group,
                units=0,
                transferred=False,
                from_inventory=group.initial_stock,
                from_balance=group.initial_cash,
                to_inventory=group.initial_stock,
                to_balance=group.initial_cash,
                kind='init'
            )

        return {
            0: {
                'type': 'start_time_decision',
                'start_time': selected_time
            }
        }
    return None


def handle_init(player):
    current_time = time.time()
    if player.field_maybe_none('init_time') is None:
        player.init_time = current_time
    return live_inventory(player)



# PAGES
class GroupMatching(WaitPage):
    wait_for_all_groups = True
    
    @staticmethod
    def after_all_players_arrive(subsession):
        players = subsession.get_players()
        shuffled_players = shuffled(players)
        
        first = shuffled_players[0:5]
        second = shuffled_players[5:10]
        third = shuffled_players[10:20]
        subsession.set_group_matrix([first, second, third])

        groups = subsession.get_groups()
        groups[0].treatment = 'NI_5'
        groups[1].treatment = 'PI_5'
        groups[2].treatment = 'NI_10'
        
        for group in groups:
            group.show_info = TREATMENTS[group.treatment]['show_info']
            group.group_size = TREATMENTS[group.treatment]['players_per_group']
            group.initial_stock = TREATMENTS[group.treatment]['initial_stock']
            group.initial_cash = TREATMENTS[group.treatment]['initial_cash']
            
        for player in players:
            player.inventory = TREATMENTS[player.group.treatment]['initial_stock']
            player.balance = TREATMENTS[player.group.treatment]['initial_cash']
            

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
        players_per_group = player.group.group_size

        ecu_earn = sess.config.get('price_per_unit', 10)
        ecu_inventory_cost = sess.config.get('cost_per_second', 5)
        ecu_request_cost = sess.config.get('cost_per_click', 2)

        round_seconds = sess.config.get('round_seconds', 30)
        round_minutes = round_seconds / 60

        return {
            'exchange_rate': f"100 ECU = {hundred_ecu:.2f} {REAL_WORLD_CURRENCY_CODE}",
            'real_world_currency_code': REAL_WORLD_CURRENCY_CODE,
            'group_size': players_per_group,
            'DEBUG': DEBUG,
            'ecu_endowment': player.group.initial_cash,
            'ecu_earn': ecu_earn,
            'ecu_inventory_cost': ecu_inventory_cost,
            'ecu_request_cost': ecu_request_cost,
            'round_minutes': round_minutes,
            'round_seconds': round_seconds,
            'training_round_seconds': sess.config.get('training_round_seconds', 30),
            'participation_fee': sess.config.get('participation_fee', '0.00 EUR'),
            'welcome_message': player.subsession.welcome_message,
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
        }
    
class TrainingRound(Page):
    def get_timeout_seconds(player):
        return player.subsession.training_total_seconds

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
        return {
            **common_vars_for_template(player),
        }


class RoundPreface(Page):
    def vars_for_template(player):
        return common_vars_for_template(player)

class JointStart(WaitPage):
    pass

class Decision(Page):
    def get_timeout_seconds(player):
        return player.subsession.total_seconds
    
    @staticmethod
    def js_vars(player):
        predecessor = player.group.get_player_by_id(player.get_predecessor())
        successor = player.group.get_player_by_id(player.get_successor())

        return {
            'own_id_in_group': player.id_in_group,
            'inventory_unit_cost_per_second': player.subsession.cost_per_second,
            'pre_inventory': predecessor.inventory,
            'suc_inventory': successor.inventory,
            **common_vars_for_template(player),
        }
    
    @staticmethod
    def vars_for_template(player):
        predecessor = player.group.get_player_by_id(player.get_predecessor())
        successor = player.group.get_player_by_id(player.get_successor())

        return {
            'pre_inventory': predecessor.inventory,
            'suc_inventory': successor.inventory,
            **common_vars_for_template(player)
        }

    @staticmethod
    def live_method(player, data):
        if data['type'] == 'init':
            return handle_init(player)

        if data['type'] == 'request':
            return live_request(player, data['data'])

        if data['type'] == 'start_time_proposal':
            return start_time_check(player, data)
        return None
        
class ResultsWait(WaitPage):
    after_all_players_arrive = 'finalize_round'

class Results(Page):
    def vars_for_template(player):
        cv = common_vars_for_template(player)

        subs = player.subsession
        items_delivered = player.total_revenue / subs.price_per_unit if subs.price_per_unit > 0 else 0

        return {
            'initial_balance': player.group.initial_cash,
            'num_items_delivered': int(items_delivered),
            **cv
        }


page_sequence = [
    GroupMatching,
    GameInstructions,
    TrainingRound,
    # TrainingFeedback,
    # TrainingWait,
    RoundPreface,
    JointStart, 
    Decision, 
    ResultsWait, 
    Results
]


# EXPORTS
def custom_export(players):
    yield ['time', 'subsession', 'round', 'group', 'kind', 'requested_from', 'requested_by', 'units', 'transferred', 'from_inventory', 'from_balance', 'to_inventory', 'to_balance']
    for request in Requests.filter():
        yield [request.created, 
               request.session.session.code,
               request.round,
               request.group_id,
               request.kind,
               request.requested_from_id,
               request.requested_by_id,
               request.units,
               request.transferred,
               request.from_inventory,
               request.from_balance,
               request.to_inventory,
               request.to_balance
        ]