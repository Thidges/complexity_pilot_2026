from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    def play_round(self):
        answers = {
            'comp_request_cost': self.session.config.get('cost_per_click', 0) * 2,
            'comp_inventory_cost': self.session.config.get('cost_per_second', 0) * 2 * 2,
        }
        if self.session.config.get('cost_per_click', 2) != 0:
            answers.update({'comp_revenue': self.session.config.get('price_per_unit', 0)})

        report = vars_for_admin_report(self.subsession)
        expect(report['unassigned'], 0)
        expect(report['current_total'], len(self.subsession.get_groups()))
        expect(sum(report['column_totals']), report['overall_total'])

        yield GameInstructions, answers
        yield TrainingRound
        yield RoundPreface
        yield Decision
        yield Results