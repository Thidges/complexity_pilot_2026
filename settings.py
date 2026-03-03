from os import environ

GAME_CONFIG = dict(
    request_timeout_seconds=0,
    info_highlight_timeout_seconds=1,
    countdown_seconds=5,
    round_seconds=600, # 300
    payment_link="https://fmru.az1.qualtrics.com/jfe/form/SV_4ZXrz1uGVKevsrA",
)

TRAINING_CONFIG = dict(
    training_cost_per_second=5,
    training_price_per_unit=100,
    training_initial_stock=2,
    training_initial_cash=300,
    training_round_seconds=90,
    training_transfer_probability=0.5,
    training_start_delay_seconds=15,
    training_leave_seconds=15,
    training_request_timeout_seconds=0,
    training_info_highlight_timeout_seconds=1,
)

COMPETITION_TRAINING_CONFIG = dict(
    training_cost_per_second=5,
    training_price_per_unit=100,
    training_initial_stock=2,
    training_initial_cash=300,
    training_round_seconds=900,
    training_transfer_probability=0.5,
    training_start_delay_seconds=2,
    training_leave_seconds=1,
    training_request_timeout_seconds=0,
    training_info_highlight_timeout_seconds=1,
)

S_10_T = dict(
    treatment="S_10_T",
    players_per_group=5,
    initial_stock="2, 2, 2, 2, 2",
    initial_cash="300, 300, 300, 300, 300",
    cost_per_second="5",
    price_per_unit="100",
    show_chain="True"
)

COMP_DEMO = dict(
    treatment="comp",
    players_per_group=4,
    initial_stock="2, 2, 2, 2",
    initial_cash="300, 300, 300, 300",
    cost_per_second="5",
    price_per_unit="100",
    show_chain="False"
)


SESSION_CONFIGS = [
    dict(
        name="intro",
        display_name="Introduction",
        app_sequence=["intro"],
        num_demo_participants=1,
        players_per_group=5,
        initial_cash="30, 30, 30, 30, 30",
        initial_stock="2, 2, 2, 2, 2",
        show_chain=False,
        **GAME_CONFIG,
        **TRAINING_CONFIG
    ),
    dict(
        name="training",
        display_name="Training Round",
        app_sequence=["training"],
        num_demo_participants=1,
        players_per_group=1,
        **TRAINING_CONFIG
    ),
    dict(
        name="competition_training",
        display_name="Competition Training Round",
        app_sequence=["competition_training"],
        num_demo_participants=1,
        players_per_group=1,
        **COMPETITION_TRAINING_CONFIG
    ),
    dict(
        name="S_10_T_demo",
        app_sequence=["ringsupplychain"],
        display_name="S_10_T Demo",
        num_demo_participants=5,
        **GAME_CONFIG,
        **S_10_T
    ),
    dict(
        name="competition",
        app_sequence=["ringsupplychain_comp"],
        display_name="Comp. double ring, Demo",
        num_demo_participants=4,
        **GAME_CONFIG,
        **COMP_DEMO
    ),
    dict(
        name="competition_middleman",
        app_sequence=["ring_comp_middleman"],
        display_name="Comp. jump middleman, Demo",
        num_demo_participants=4,
        **GAME_CONFIG,
        **COMP_DEMO
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
        display_name="Full Experiment",
        app_sequence=[
            "intro",
            "competition_training",
            "ring_comp_middleman",
            "questionnaires"
        ],
        num_demo_participants=4,
        **COMPETITION_TRAINING_CONFIG,
        **GAME_CONFIG,
        **COMP_DEMO
    )
]

# Rooms
ROOMS = [
    dict(
        name='room1',
        display_name='Room 1',
        participant_label_file='_rooms/room1.txt',
    ),
    dict(
        name='room2',
        display_name='Room 2',
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

PARTICIPANT_FIELDS = ['game_rounds', 'pages_completed', 'finished']
SESSION_FIELDS = ['advance_pages']

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

# URL from heroku labs runtime-dyno-metadata
BASE_URL = environ.get('HEROKU_APP_DEFAULT_DOMAIN_NAME', 'localhost:8000')