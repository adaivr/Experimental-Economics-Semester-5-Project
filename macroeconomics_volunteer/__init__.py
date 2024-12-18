from otree.api import *

doc = ""


class C(BaseConstants):
    NAME_IN_URL = "macroeconomics_volunteer"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    chose_labor = models.IntegerField()
    chose_capital = models.IntegerField()
    total_players = models.IntegerField()


def set_resources(group: Group):
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
        players = self.get_others_in_subsession()
        players.append(self)
        results = []
        for p in players:
            name = p.in_round(1).name
            chose_labor = []
            resources = []
            for r in range(C.NUM_ROUNDS):
                data = p.in_round(r + 1)
                chose_labor.append(data.chose_labor)
                resources.append(data.resources)
            results.append(
                {
                    "name": name,
                    "resources": sum(resources),
                    "chose_labor": sum(chose_labor),
                    "chose_capital": C.NUM_ROUNDS - sum(chose_labor),
                }
            )
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
    after_all_players_arrive = set_resources


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
