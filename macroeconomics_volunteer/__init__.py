from otree.api import *

doc = ""


class C(BaseConstants):
    NAME_IN_URL = "macroeconomics_volunteer"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    LOG = {}


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    chose_labor = models.IntegerField()
    chose_capital = models.IntegerField()
    total_players = models.IntegerField()


def set_payoffs(group: Group):
    players = group.get_players()
    group.chose_labor = sum([p.chose_labor == True for p in players])
    group.chose_capital = sum([p.chose_labor == False for p in players])
    group.total_players = group.chose_labor + group.chose_capital
    for p in players:
        if p.chose_labor:
            p.resources = (
                4.5
                * (group.chose_labor - 1)
                * (group.chose_capital)
                / (group.total_players - 1)
                / (group.total_players - 2)
            )
        else:
            p.resources = 1
        if p.id_in_group not in C.LOG:
            C.LOG[p.id_in_group] = {"name": p.name, "chose_labor": [], "resources": []}
        C.LOG[p.id_in_group]["resources"].append(p.resources)
        C.LOG[p.id_in_group]["chose_labor"].append(p.chose_labor)


class Player(BasePlayer):
    chose_labor = models.BooleanField(
        label="Куда потратить ресурсы?",
        choices=[
            [False, "Капитал"],
            [True, "Труд"],
        ],
    )
    name = models.StringField(label="Фамилия Имя:")
    resources = models.FloatField()

    def results(self):
        results = []
        for id in C.LOG:
            name = C.LOG[id]["name"]
            resources = sum(C.LOG[id]["resources"])
            chose_labor = sum(C.LOG[id]["chose_labor"])
            chose_capital = C.NUM_ROUNDS - chose_labor
            results.append({
                "name": name,
                "resources": resources,
                "chose_labor": chose_labor,
                "chose_capital": chose_capital,
            })
        return results
    def str_choice(self):
        return "труд" if self.chose_labor else "капитал"


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


class Round(Page):
    form_model = "player"
    form_fields = ["chose_labor"]


class RoundWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class RoundResults(Page):
    pass


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    form_model = "player"


class End(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    pass


page_sequence = [Registration, Rules, Round, RoundWaitPage, RoundResults, Results, End]
