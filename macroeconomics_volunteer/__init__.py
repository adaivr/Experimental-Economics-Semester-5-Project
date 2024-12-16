from otree.api import *

c = cu

doc = ""


class C(BaseConstants):
    NAME_IN_URL = "macroeconomics_volunteer"
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 1
    GENERAL_BENEFIT = cu(1)
    NEEDED_PLAYERS = 3
    TOTAL_PLAYERS = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    num_volunteers = models.FloatField()
    num_int = models.IntegerField()


def set_payoffs(group: Group):
    players = group.get_players()
    group.num_volunteers = sum([p.volunteer == True for p in players])
    group.num_int = sum([p.volunteer == True for p in players])
    for p in players:
        if p.volunteer:
            p.good = (
                4.5 * ((group.num_volunteers - 1) * (C.TOTAL_PLAYERS - group.num_volunteers)
                ) / ((C.TOTAL_PLAYERS - 2) * (C.TOTAL_PLAYERS - 1))
            )
        else:
            p.good = 1


class Player(BasePlayer):
    volunteer = models.BooleanField(
        doc="Whether player volunteers", label="Вложимся в экономику?"
    )
    good = models.FloatField()


class Rules(Page):
    form_model = "player"


class Decision(Page):
    form_model = "player"
    form_fields = ["volunteer"]


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    form_model = "player"


page_sequence = [Rules, Decision, ResultsWaitPage, Results]
