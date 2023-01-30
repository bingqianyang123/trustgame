from otree.api import *
import random
c = cu

doc = '\nThis is a standard 2-player trust game where the amount sent by player 1 gets\ntripled. The trust game was first proposed by\n<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">\n    Berg, Dickhaut, and McCabe (1995)\n</a>.\n'

class C(BaseConstants):
    NAME_IN_URL = 'trust'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    INSTRUCTIONS_TEMPLATE = 'trust/instructions.html'

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        doc='Amount sent by P1', 
        label='Please enter an amount from 0 to 10', 
        max=C.ENDOWMENT, 
        min=0
        )
    sent_back_amount = models.CurrencyField(
        doc='Amount sent back by P2', 
        min=0
        )

class Player(BasePlayer):
    pass

# FUNCTIONS

def sent_back_amount_max(group: Group):
    return group.sent_amount * C.MULTIPLIER

def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = C.ENDOWMENT - group.sent_amount + group.sent_back_amount
    p2.payoff = group.sent_amount * C.MULTIPLIER - group.sent_back_amount

#PAGES

class Introduction(Page):
    form_model = 'player'
    timeout_seconds = 60

class Send(Page):
    form_model = 'group'
    form_fields = ['sent_amount']
    timeout_seconds = 10
    
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 1
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if timeout_happened:
          group.sent_amount = random.randint(0,10)

class SendBackWaitPage(WaitPage):
    pass

class SendBack(Page):
    form_model = 'group'
    form_fields = ['sent_back_amount']
    timeout_seconds = 10

    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        tripled_amount = group.sent_amount * C.MULTIPLIER
        return dict(tripled_amount=tripled_amount)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if timeout_happened:
          group.sent_back_amount = random.randint(0,10)

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class Results(Page):
    form_model = 'player'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
    
        return dict(tripled_amount=group.sent_amount * C.MULTIPLIER)

page_sequence = [Introduction, Send, SendBackWaitPage, SendBack, ResultsWaitPage, Results]