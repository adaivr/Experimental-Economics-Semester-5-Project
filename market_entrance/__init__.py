from otree.api import *

doc = ""


class C(BaseConstants):
    NAME_IN_URL = "market_entrance"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    MAX_PRODUCTION = 100
    BIG_MARKET_CAPACITY = 150
    SMALL_MARKET_CAPACITY = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    big_market_production = models.FloatField()
    small_market_production = models.FloatField()
    big_market_price = models.CurrencyField()
    small_market_price = models.CurrencyField()


def set_other(group: Group):
    players = group.get_players()
    for i in range(C.PLAYERS_PER_GROUP):
        players[i].other_production = players[i - 1].production


def set_payoff(group: Group):
    players = group.get_players()
    group.big_market_production = 0
    group.small_market_production = 0
    for i in range(C.PLAYERS_PER_GROUP):
        players[i].other_chose_big = players[i - 1].chose_big
    for p in players:
        if p.chose_big:
            group.big_market_production += p.production
        else:
            group.small_market_production += p.production
    group.big_market_price = C.BIG_MARKET_CAPACITY - group.big_market_production
    group.small_market_price = C.SMALL_MARKET_CAPACITY - group.small_market_production
    for p in players:
        if p.chose_big:
            p.payoff = p.production * group.big_market_price
        else:
            p.payoff = p.production * group.small_market_price


class Player(BasePlayer):
    production = models.FloatField(
        label="Сколько бананов вы хотите произвести?", max=C.MAX_PRODUCTION, min=0
    )
    chose_big = models.BooleanField(
        label="На какой рынок вы хотите поставить свои бананы?",
        choices=[
            [True, "На большой"],
            [False, "На маленький"],
        ],
    )
    name = models.StringField(label="Фамилия Имя:")
    other_production = models.FloatField()
    other_chose_big = models.BooleanField()

    def market_str(self):
        return "большой" if self.chose_big else "маленький"

    def other_market_str(self):
        return "большой" if self.other_chose_big else "маленький"

    def results(self):
        players = self.get_others_in_subsession()
        players.append(self)
        results = []
        for p in players:
            name = p.in_round(1).name
            payoff = []
            chose_big = []
            production = []
            for r in range(C.NUM_ROUNDS):
                data = p.in_round(r + 1)
                payoff.append(data.payoff)
                chose_big.append(data.chose_big)
                production.append(data.production)
            results.append(
                {
                    "name": name,
                    "payoff": sum(payoff),
                    "production": sum(production),
                    "chose_big": sum(chose_big),
                    "chose_small": C.NUM_ROUNDS - sum(chose_big),
                }
            )
        return results


class Registration(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    form_model = "player"
    form_fields = ["name"]


class Rules(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    pass


class Production(Page):
    form_model = "player"
    form_fields = ["production"]


class ProductionWaitPage(WaitPage):
    after_all_players_arrive = set_other


class Market(Page):
    form_model = "player"
    form_fields = ["chose_big"]


class MarketWaitPage(WaitPage):
    after_all_players_arrive = set_payoff


class RoundResults(Page):
    pass


class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.group_randomly()


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    pass


class End(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    pass


page_sequence = [
    Registration,
    Rules,
    Production,
    ProductionWaitPage,
    Market,
    MarketWaitPage,
    RoundResults,
    ResultsWaitPage,
    Results,
    End,
]
