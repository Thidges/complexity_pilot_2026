import random
import time

from otree.api import *
from otree.settings import DEBUG, TREATMENTS, REAL_WORLD_CURRENCY_CODE

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'ringsupplychain'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1 
    # Safety net only: the Decision page normally submits itself when the
    # shared game clock (group.start_time + round_seconds) runs out. This
    # timeout just makes sure nobody is stranded forever if the group never
    # starts or a browser dies.
    DECISION_BACKSTOP_SECONDS = 360
    # Clients repeat the start handshake every 2 seconds (HANDSHAKE_RETRY_MS
    # in Decision.html) until the game start is decided. A player counts as
    # present only if their last handshake is at most this old.
    HANDSHAKE_FRESH_SECONDS = 5


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
    emphasize_symmetry = models.BooleanField(initial=False)
    package = models.StringField()

class Group(BaseGroup):
    start_time = models.FloatField()
    group_size = models.IntegerField()
    treatment = models.StringField()
    show_info = models.BooleanField(initial=False)
    show_chain = models.BooleanField(initial=False)
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
    auto_play = sess.config.get('auto_play', False)
    welcome_message = sess.config.get('welcome_message', False)
    package = sess.config.get('package', None)
    emphasize_symmetry = sess.config.get('emphasize_symmetry', False)
       
    total_seconds = countdown_seconds + round_seconds
    training_total_seconds = countdown_seconds + training_round_seconds
    
    if any(var is None for var in [cost_per_second, cost_per_click, price_per_unit, round_seconds, request_timeout_seconds, info_highlight_timeout_seconds, countdown_seconds, package]):
        raise ValueError("session not configured correctly")

    if package in TREATMENTS:
        size = TREATMENTS[package]['players_per_group']
        if sess.num_participants % size != 0:
            raise ValueError(f"Treatment {package} needs a multiple of {size} participants")

    # assign variables
    subsession.cost_per_second = cost_per_second
    subsession.cost_per_click = cost_per_click
    subsession.price_per_unit = price_per_unit
    subsession.round_seconds = round_seconds
    subsession.training_round_seconds = training_round_seconds
    subsession.start_delay_seconds = start_delay_seconds
    subsession.leave_seconds = leave_seconds
    subsession.auto_play = auto_play
    subsession.request_timeout_seconds = request_timeout_seconds
    subsession.info_highlight_timeout_seconds = info_highlight_timeout_seconds
    subsession.total_seconds = total_seconds
    subsession.training_total_seconds = training_total_seconds
    subsession.countdown_seconds = countdown_seconds
    subsession.welcome_message = welcome_message
    subsession.maximum_units = 10
    subsession.package = package
    subsession.emphasize_symmetry = emphasize_symmetry
    
def vars_for_admin_report(subsession):
    from otree.models import Session

    treatment_names = list(TREATMENTS.keys())

    # current session
    current = {t: 0 for t in treatment_names}
    unassigned = 0
    for g in subsession.get_groups():
        t = g.field_maybe_none('treatment')
        if t is None:
            unassigned += 1
        else:
            current[t] = current.get(t, 0) + 1

    # whole dataset, excluding demo sessions: one row per session
    sessions = {
        s.id: s for s in Session.objects_filter(is_demo=False).order_by('id')
    }
    per_session = {}
    for g in Group.objects_filter(Group.treatment != None):
        if g.session_id not in sessions:
            continue
        counts = per_session.setdefault(g.session_id, {t: 0 for t in treatment_names})
        counts[g.treatment] = counts.get(g.treatment, 0) + 1

    column_totals = {t: 0 for t in treatment_names}
    session_rows = []
    for sid in sorted(per_session):
        counts = per_session[sid]
        sess = sessions[sid]
        for t in treatment_names:
            column_totals[t] += counts[t]
        session_rows.append(
            dict(
                code=sess.code,
                config_name=sess.config.get('name', ''),
                counts=[counts[t] for t in treatment_names],
                total=sum(counts.values()),
            )
        )

    return dict(
        package=subsession.package,
        treatment_names=treatment_names,
        current_counts=[current[t] for t in treatment_names],
        current_total=sum(current.values()),
        unassigned=unassigned,
        session_rows=session_rows,
        column_totals=[column_totals[t] for t in treatment_names],
        overall_total=sum(column_totals.values()),
    )

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

def game_window(group):
    """Shared (start, end) of the game in server time, or None if not started."""
    start = group.field_maybe_none('start_time')
    if start is None:
        return None
    return start, start + group.subsession.round_seconds


def accrue_holding_cost(player, now):
    """Charge inventory holding cost up to `now`, but only for time inside
    the shared game window, so waiting for the group, the countdown and
    anything after the end are never charged."""
    window = game_window(player.group)
    if window is None:
        return
    start, end = window
    now = min(max(now, start), end)
    last_update = player.field_maybe_none('last_inventory_update')
    if last_update is None or last_update < start:
        last_update = start
    if now > last_update:
        cost = (now - last_update) * player.subsession.cost_per_second * player.inventory
        player.total_inventory_cost += cost
        player.total_cost += cost
        player.balance -= cost
        player.total_profit = player.total_revenue - player.total_cost
        last_update = now
    player.last_inventory_update = last_update


def live_inventory(player):
    accrue_holding_cost(player, time.time())

    # inventories
    predecessor = player.group.get_player_by_id(player.get_predecessor())
    successor = player.group.get_player_by_id(player.get_successor())
    chain_inventory = {p.id_in_group: p.inventory for p in player.group.get_players()}

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
            'suc_inventory': successor.inventory,
            'chain_inventory': chain_inventory,
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

    # Requests only count inside the shared game window, whatever the
    # client's own clock or timers say.
    window = game_window(group)
    if window is None or not (window[0] <= current_time <= window[1]):
        return None

    from_revenue = 0
    transferred = False

    # Accrue inventory holding costs to-date for both players, regardless of
    # whether the transfer succeeds — otherwise the response would report a
    # stale balance and the client display would jump up.
    for p in (take_from_player, give_to_player):
        accrue_holding_cost(p, current_time)

    # charge click cost to requesting player unconditionally
    click_cost = subsession.cost_per_click
    give_to_player.balance -= click_cost
    give_to_player.total_cost += click_cost
    give_to_player.total_request_cost += click_cost

    # Check if the take_from player has enough inventory
    if take_from_player.inventory >= units:
        # update inventory
        take_from_player.inventory -= units
        take_from_player.total_items_sold += units
        give_to_player.inventory += units

        # update balance and revenue
        from_revenue = units * subsession.price_per_unit
        take_from_player.balance += from_revenue
        take_from_player.total_revenue += from_revenue

        transferred = True

    # update profit (always — costs may have changed even on failure)
    take_from_player.total_profit = take_from_player.total_revenue - take_from_player.total_cost
    give_to_player.total_profit = give_to_player.total_revenue - give_to_player.total_cost
        
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
        'show_chain': group.show_chain,
        'auto_play': subs.auto_play,
        'round_seconds': subs.round_seconds,
        'total_seconds': subs.total_seconds,
        'leave_seconds': subs.leave_seconds,
        'start_delay_seconds': subs.start_delay_seconds,
        'training_round_seconds': subs.training_round_seconds,
        'request_button_timeout_seconds': subs.request_timeout_seconds,
        'info_highlight_timeout_seconds': subs.info_highlight_timeout_seconds,
        'countdown_seconds': subs.countdown_seconds,
        'emphasize_symmetry': subs.emphasize_symmetry,
        'DEBUG': DEBUG
    }

def finalize_round(group):
    window = game_window(group)
    for player in group.get_players():
        # charge holding cost for the time between the player's last update
        # and the shared end of the game (no-op if the game never started)
        if window is not None:
            accrue_holding_cost(player, window[1])

        if player.balance > 0:
            player.payoff = player.balance

        # store payment data on the participant
        player.participant.vars['ecu_earnings'] = int(player.total_profit)
        player.participant.vars['final_balance'] = player.balance

        

def start_time_message(group, current_time):
    start, end = game_window(group)
    return {
        'type': 'start_time_decision',
        'delay_ms': max(0, int((start - current_time) * 1000)),
        'end_ms': max(0, int((end - current_time) * 1000)),
    }


def start_time_check(player: Player, data):
    """Handshake: clients keep sending 'start_time_proposal' until they get a
    'start_time_decision'. The game starts only once every group member has
    reported in; start and end are decided in server time and sent as delays,
    so client clocks do not matter."""
    current_time = time.time()
    # proposed_start_time is the time of this player's most recent handshake,
    # i.e. "last seen on the Decision page with a working connection".
    # (init_time keeps the first arrival.)
    player.proposed_start_time = current_time

    subs = player.subsession
    group = player.group

    if group.field_maybe_none('start_time') is not None:
        # Start already decided (repeated handshake, missed broadcast, reload):
        # answer only this player with the remaining delays.
        return {player.id_in_group: start_time_message(group, current_time)}

    # Start only when every group member is on the page right now: each one
    # must have sent a handshake within the last few seconds. A player who is
    # reloading or whose connection dropped stops sending handshakes, so the
    # start is held back until they are back.
    group_players = group.get_players()
    present_count = sum(
        1 for p in group_players
        if (p.field_maybe_none('proposed_start_time') or 0)
        >= current_time - C.HANDSHAKE_FRESH_SECONDS
    )

    if present_count == group.group_size:
        selected_time = current_time + subs.countdown_seconds
        group.start_time = selected_time

        for p in group_players:
            p.last_inventory_update = selected_time

            Requests.create(
                created=selected_time,
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

        return {0: start_time_message(group, time.time())}
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

        package = subsession.package
        n = len(shuffled_players)

        if package in TREATMENTS:
            size = TREATMENTS[package]['players_per_group']
            treatments = [package] * (n // size)
        elif package == "5":
            n_groups = n // 5
            n_ni = n_groups // 2
            n_ai = n_groups // 2
            treatments = ['NI_5'] * n_ni + ['AI_5'] * n_ai
            if n_groups % 2 == 1:
                treatments.append(random.choice(['NI_5', 'AI_5']))
        elif package == "10":
            n_groups = n // 10
            n_ni = n_groups // 2
            n_ai = n_groups // 2
            treatments = ['NI_10'] * n_ni + ['AI_10'] * n_ai
            if n_groups % 2 == 1:
                treatments.append(random.choice(['NI_10', 'AI_10']))
        elif package in ("NI", "AI"):
            num_10 = n // 10
            remainder = n % 10
            if remainder == 0 and num_10 > 0:
                num_10 -= 1
                remainder = 10
            num_5 = remainder // 5
            treatments = [f'{package}_10'] * num_10 + [f'{package}_5'] * num_5
        else:
            raise ValueError(f"Unknown package: {package}")

        random.shuffle(treatments)

        matrix = []
        idx = 0
        for t in treatments:
            size = TREATMENTS[t]['players_per_group']
            matrix.append(shuffled_players[idx:idx + size])
            idx += size

        subsession.set_group_matrix(matrix)

        groups = subsession.get_groups()
        for g, t in zip(groups, treatments):
            g.treatment = t

        for group in groups:
            group.show_info = TREATMENTS[group.treatment]['show_info']
            group.show_chain = TREATMENTS[group.treatment]['show_chain']
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
        subs = player.subsession
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
            'welcome_message': subs.welcome_message,
            'emphasize_symmetry': subs.emphasize_symmetry,
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
    # custom template: adds a periodic "am I done?" check as a fallback for
    # a lost websocket message
    template_name = 'ringsupplychain/JointStart.html'
    body_text = "The main task begins as soon as all participants have completed the training round. Please wait."
    pass

class Decision(Page):
    def get_timeout_seconds(player):
        return C.DECISION_BACKSTOP_SECONDS
    
    @staticmethod
    def js_vars(player):
        predecessor = player.group.get_player_by_id(player.get_predecessor())
        successor = player.group.get_player_by_id(player.get_successor())
        chain_inventory = {p.id_in_group: p.inventory for p in player.group.get_players()}

        return {
            'own_id_in_group': player.id_in_group,
            'inventory_unit_cost_per_second': player.subsession.cost_per_second,
            'pre_inventory': predecessor.inventory,
            'suc_inventory': successor.inventory,
            'chain_inventory': chain_inventory,
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