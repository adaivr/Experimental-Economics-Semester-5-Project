from otree.api import *

doc = ""

# Случайное разбиение на пары
# Выбор рынка
# Цена в результатах
# Общие результаты за все раунды
# Выбор самого игрока

class C(BaseConstants):
    NAME_IN_URL = "public_goods_simple2"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    MAX_PRODUCT = 100
    CAPACITY_MARKET_1 = 150
    CAPACITY_MARKET_2 = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.FloatField()
    individual_share = models.FloatField()


def set_payoffs(group: Group):
    players = group.get_players()
    market_produced_1 = C.CAPACITY_MARKET_1
    market_produced_2 = C.CAPACITY_MARKET_2
    for p in players:
        if p.market == 1:
            market_produced_1 -= p.produced
        else:
            market_produced_2 -= p.produced
    for p in players:
        if (
            market_produced_1 == C.CAPACITY_MARKET_1
            or market_produced_2 == C.CAPACITY_MARKET_2
        ):
            p.another_market = p.market
        else:
            p.another_market = 3 - p.market
        if p.market == 1:
            p.payoff = market_produced_1 * p.produced
        else:
            p.payoff = market_produced_2 * p.produced


def other_product(group: Group):
    players = group.get_players()
    sums = [p.produced for p in players]
    total = sum(sums)
    for p in players:
        p.another_produced = total - p.produced


class Player(BasePlayer):
    produced = models.FloatField(
        label="Сколько бананов вы хотите произвести?", max=C.MAX_PRODUCT, min=0
    )
    market = models.IntegerField(
        label="На какой рынок вы хотите поставить свои бананы, на первый или на второй?",
        max=2,
        min=1,
    )
    another_produced = models.FloatField()
    another_market = models.IntegerField()


class Rules(Page):
    pass


class Contribute(Page):
    form_model = "player"
    form_fields = ["produced"]


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = other_product


class MarketChoose(Page):
    form_model = "player"
    form_fields = ["market"]


class WaitingAgain(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    form_model = "player"


page_sequence = [
    Rules,
    Contribute,
    ResultsWaitPage,
    MarketChoose,
    WaitingAgain,
    Results,
]
