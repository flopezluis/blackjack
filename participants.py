#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
from renderers import ParticipantTextRender, HandTextRender

HITTING = "HITTING"
STAND = "STAND"
SPLIT = "SPLIT"

class Participant(object):
    """Base class for every participant in the blackjack game"""

    def __init__(self, name, money, renderer = None):
        """ A participant has to be created with these parameters
            :param name: the name of the participant.
            :param money: the money to start with.
            :param render (optional): the type of render to draw it."""
        self.name = name
        self.hands = []
        self.renderer = renderer or ParticipantTextRender()
        self.active_hand = None
        self.money = money

    def render(self):
        self.renderer.render(self)

    def render_active_hand(self):
        self.renderer.render_active_hand(self)

    def is_valid_bet(self, bet):
        return bet > 0 and bet <= self.get_money()

    def new_hand(self, bet=None):
        """Add a new hand to the participant and the bet for it.
           :param bet: The bet is optional, the dealer doesn't need to bet"""
        hand = Hand(bet)
        self.hands.append(hand)
        if not self.active_hand:
            self.active_hand = hand

    def get_active_hand(self):
        return self.active_hand

    def set_active_hand(self, hand):
        self.active_hand = hand

    def clean_active_hand(self):
        self.hands.remove(self.get_active_hand())

    def clean_hand(self, hand):
        """Delete the specific hand"""
        self.hands.remove(hand)
        if not self.hands:
            self.active_hand = None
        elif not self.active_hand in self.hands:
            self.active_hand = self.hands[0]

    def clean_hands(self, hands=None):
        """Delete the specific hands or all if none is passed"""
        if not hands:
            hands = list(self.hands)
        for hand in hands:
            self.clean_hand(hand)

    def hit(self, game):
        self.get_active_hand().hit(game)

    def stand(self, game):
        self.get_active_hand().stand(game)

    def is_stand(self):
        return self.get_active_hand().is_stand()

    def turn(self, game):
        """ It must perform the next action for the participant.
         - HIT
         - STAND
         -....
        """
        raise NotImplementedError

    def allowed_actions(self):
        """ It must return a list of the allowrd actions"""
        raise NotImplementedError

    def clean_cards(self):
        self.cards = []

    def add_money(self, money):
        self.money += money

    def get_money(self):
        return self.money

    def get_score(self):
        return self.get_active_hand().get_score()

    def get_number_of_cards(self):
        return self.get_active_hand().get_len()

    def __repr__(self):
        return "%s" % (self.name)

class Player(Participant):

    def allowed_actions(self):
        hand = self.get_active_hand()
        actions = [self.hit, self.stand]
        if hand.can_do_split():
            actions.append(self.split)
        return actions

    def make_bet(self, bet):
        if self.is_valid_bet(bet):
            self.new_hand(bet)
            self.add_money(-bet)
            return True
        return False

    def turn(self, game):
        self.renderer.render_options(self)
        option = int(input(""))
        actions = self.allowed_actions()
        actions[option](game)

    def split(self, game):
        new_hand = self.get_active_hand().split(game)
        self.hands.append(new_hand)
        self.hit(game)

    def is_bankrupt(self):
        return self.money == 0

    def win_bet(self, hand = None):
        hands = [hand] if hand else self.hands
        for h in hands:
            self.add_money(h.bet*2)
            h.reset_bet()

class Dealer(Participant):

    def turn(self, game):
        self.get_active_hand().reveal()
        if self.get_score() < settings.DEALER_MIN_SCORE:
            self.hit(game)
        else:
            self.stand(game)

    def allowed_actions(self):
        return [self.hit, self.stand]

    def hit(self, game):
        hand = self.get_active_hand()
        added_card = hand.hit(game)

        if hand.get_len() == 2:
            added_card.hidden = True

class Hand(object):

    def __init__(self, bet=0, renderer=None):
        self.cards = []
        self._bet = bet
        self.status = None
        self.renderer = renderer or HandTextRender()

    def is_stand(self):
        return self.status == STAND

    def render(self):
        self.renderer.render(self)

    def add_card(self, card):
        self.cards.append(card)

    def reveal(self):
        for card in self.cards:
            card.hidden = False

    def split(self, game):
        card = self.cards.pop()
        self._bet /= 2
        hand = Hand(self._bet)
        hand.add_card(card)
        return hand

    def stand(self, game):
        self.status = STAND

    def can_do_split(self):
        return (len(self.cards) == 2 and \
                all([card.value >= settings.MIN_CARD_TO_SPLIT for card in self.cards]))

    def hit(self, game):
        card = game.get_card()
        self.add_card(card)
        self.status = HITTING
        return card

    @property
    def bet(self):
        return self._bet

    def reset_bet(self):
        self._bet = 0

    def get_len(self):
        return len(self.cards)

    def get_score(self):
        return sum([card.value for card in self.cards])
