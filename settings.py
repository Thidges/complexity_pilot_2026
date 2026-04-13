from os import environ

GAME_CONFIG = dict(
    request_timeout_seconds=0,
    info_highlight_timeout_seconds=1,
    countdown_seconds=5,
    training_round_seconds=60,
    round_seconds=180, # 300
    start_delay_seconds=1,
    leave_seconds=65,
    cost_per_second=5,
    cost_per_click=25,
    price_per_unit=100,
    maximum_units_in_play=10,
    show_chain=False,
    payment_link="https://fmru.az1.qualtrics.com/jfe/form/SV_0U6FdR5Qwaux0RE",
)


TREATMENTS = dict(
    NI_5 = dict(
        treatment="NI_5",
        players_per_group=5,
        initial_stock=2,
        initial_cash=300,
        show_info=False
    ),
    NI_10 = dict(
        treatment="NI_10",
        players_per_group=10,
        initial_stock=2,
        initial_cash=300,
        show_info=False
    ),
    AI_5 = dict(
        treatment="AI_5",
        players_per_group=5,
        initial_stock=2,
        initial_cash=300,
        show_info=True
    )
)


SESSION_CONFIGS = [
    dict(
        name="intro",
        display_name="Introduction",
        app_sequence=["intro"],
        num_demo_participants=5,
        **GAME_CONFIG
    ),
    dict(
        name="questionnaire",
        display_name="Final Questionnaire + Payments",
        app_sequence=["questionnaires"],
        num_demo_participants=1,
        **GAME_CONFIG
    ),
    dict(
        name="full_experiment",
        display_name="Full Experiment, 10 demo participants",
        app_sequence=[
            "intro",
            "ringsupplychain",
            "questionnaires"
        ],
        num_demo_participants=10,
        **GAME_CONFIG
    ),
    dict(
        name="full_experiment_20",
        display_name="Full Experiment, 20 demo participants",
        app_sequence=[
            "intro",
            "ringsupplychain",
            "questionnaires"
        ],
        num_demo_participants=20,
        **GAME_CONFIG
    )
]

# Rooms
ROOMS = [
    dict(
        name='room1',
        display_name='Room 1',
        participant_label_file='_rooms/room1.txt',
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.0005, participation_fee=5.00, doc=""
)

PARTICIPANT_FIELDS = ['finished']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'ECU'

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7220483092201'

BROWSER_COMMAND = "/Users/christian/chrome.sh"
