from os import environ

GAME_CONFIG = dict(
    request_timeout_seconds=0,
    info_highlight_timeout_seconds=1,
    countdown_seconds=5,
    round_seconds=240,
    cost_per_second=5,
    price_per_unit=100,
    initial_stock=2,
    initial_cash=300,
    maximum_units_in_play=10, # should be 5 * training_initial_stock
    start_delay_seconds=1,
    leave_seconds=15,
    show_chain=False,
    players_per_group=1
)

SESSION_CONFIGS = [
    dict(
        name="calibration_intro",
        display_name="Introduction",
        app_sequence=["calibration_intro"],
        num_demo_participants=1,
        **GAME_CONFIG
    ),
    dict(
        name="calibration_main",
        display_name="Main Task",
        app_sequence=["calibration_main"],
        num_demo_participants=1,
        price_per_click=1,
        **GAME_CONFIG,
    ),
    dict(
        name="calibration_questionnaires",
        display_name="Final Questionnaire / Payments",
        app_sequence=["calibration_questionnaires"],
        num_demo_participants=1,
        **GAME_CONFIG
    ),
    dict(
        name="req00",
        display_name="Setting 1: Request Cost 0",
        app_sequence=["calibration_intro", "calibration_main", "calibration_questionnaires"],
        num_demo_participants=1,
        price_per_click=0,
        **GAME_CONFIG
    ),
    dict(
        name="req01",
        display_name="Setting 2: Request Cost 1",
        app_sequence=["calibration_intro", "calibration_main", "calibration_questionnaires"],
        num_demo_participants=1,
        price_per_click=1,
        **GAME_CONFIG
    ),
dict(
        name="req25",
        display_name="Setting 3: Request Cost 25",
        app_sequence=["calibration_intro", "calibration_main", "calibration_questionnaires"],
        num_demo_participants=1,
        price_per_click=25,
        **GAME_CONFIG
    ),
    dict(
        name="req50",
        display_name="Setting 4: Request Cost 50",
        app_sequence=["calibration_intro", "calibration_main", "calibration_questionnaires"],
        num_demo_participants=1,
        price_per_click=50,
        **GAME_CONFIG
    ),
]

# Rooms
ROOMS = []

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.0005, participation_fee=5.00, doc="", prolific_completion_url=""
)

PARTICIPANT_FIELDS = ['finished', 'ecu_earnings']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'ECU'

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7220483092201'
