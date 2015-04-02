#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 2.7
__author__ = "Felix"
__version__ = "0.8"
__email__ = "hola@flopezluis"

import settings
import random
from participants import Dealer, Player
from renderers import CardTextRender, DeckTextRender, GameTextRender

class Card(object):
    """It represents a card of a suit.
        A card can be hidden, which means that the user can't see either
        the value or the representation."""

    def __init__(self, suit, representation, value, renderer = None):
        """
        :param suit: suit to what it belongs.
        :param representaion: how to depict the card.
        :param value: real.
        """
        self.suit = suit
        self._value = value
        self.representation = representation
        self._hidden = False
        self.renderer = renderer or CardTextRender()

    def render(self):
        self.renderer.render(self)

    @property
    def hidden(self):
        """This method returns whether the card is visible or not."""
        return self._hidden

    @hidden.setter
    def hidden(self, value):
        self._hidden = value

    @property
    def value(self):
        """This method returns the card's value."""
        if self.hidden:
            return 0
        return self._value

class Deck(object):
    """ It represents a deck. The type of deck is set by conf"""

    @classmethod
    def create(cls, decks = 1):
        deck = Deck()
        for _ in range(decks):
            deck.__create_deck()
        return deck

    def __init__(self, renderer = None):
        self.deck = []
        self.renderer = renderer or DeckTextRender()

    def __create_deck(self):
        for _, repre in settings.DECK_CONF['suits'].iteritems():
            self.deck.extend([Card(repre, *conf) for conf in settings.DECK_CONF['cards'].items()])

    def shuffle(self):
        random.shuffle(self.deck)

    def get_card(self):
        return self.deck.pop()

    def is_empty(self):
        return len(self.deck) == 0

    def render(self):
        self.renderer.render(self)

class Game(object):

    def __init__(self, players, renderer=None):
        self.players = players
        self.dealer = Dealer(settings.DEALER_NAME, settings.DEALER_CHIPS)
        self.winner = None
        self.renderer = renderer or GameTextRender()

    def set_current_player(self, player):
        self.current_player = player

    def ask_bet(self, player):
        valid_bet = False
        print "Player %s has %d chips" % (player, player.money)
        while not valid_bet:
            bet = int(input("How much do you want to bet? \n"))
            valid_bet = player.make_bet(bet)

    def init_game(self):
        for player in self.players:
            self.ask_bet(player)
            player.hit(self)
            player.hit(self)

        self.dealer.new_hand()
        self.dealer.hit(self)
        self.dealer.hit(self)

    def get_card(self):
        return self.deck.get_card()

    def is_over(self):
        return all([player.is_bankrupt() for player in self.players])

    def process_turn(self, player):
        if player == self.dealer:
            self.set_state(settings.STATE_DEALER_TURN)
        else:
            self.set_state(settings.STATE_PLAYER_TURN)
        player.turn(self)
        self.set_state(settings.STATE_NEXT_TURN)

    def process_hand(self):
        #the player can have blackjack with the initial cards
        if not self.blackjack_or_busted(self.current_player, self.dealer):
            finished_hands = []
            for hand in self.current_player.hands:
                self.set_active_hand(hand)
                while (not hand.is_stand()):
                    self.process_turn(self.current_player)
                    if self.blackjack_or_busted(self.current_player, self.dealer, hand):
                        finished_hands.append(hand)
                        break
            if finished_hands:
                self.current_player.clean_hands(finished_hands)
            while (not self.dealer.is_stand() and self.current_player.get_active_hand()):
                self.process_turn(self.dealer)
                if self.blackjack_or_busted(self.dealer, self.current_player):
                    break
            if self.dealer.is_stand():
                self.check_winner(self.current_player)

    def blackjack_or_busted(self, opponent, opponent_two, hand=None):
        self.winner = None
        if Game.is_busted(opponent):
            self.winner = opponent_two
            self.set_state(settings.STATE_BUSTED)
        if Game.is_blackjack(opponent):
            self.winner = opponent
            self.set_state(settings.STATE_BLACKJACK)
        if isinstance(self.winner, Player):
            self.winner.win_bet(hand)
        return self.winner

    @staticmethod
    def is_blackjack(player):
        return player.get_score() == settings.BLACKJACK and \
             player.get_number_of_cards() == settings.CARDS_FOR_BLACKJACK

    @staticmethod
    def is_busted(player):
        return player.get_score() > settings.BLACKJACK

    def check_winner(self, player):
        for hand in player.hands:
            if player.get_score() >= self.dealer.get_score():
                player.win_bet(hand)
                self.set_winner_bigger_score(player)
            else:
                self.set_winner_bigger_score(self.dealer)

    def set_winner_bigger_score(self, player):
        self.winner = player
        self.set_state(settings.STATE_WINNER_BIGGER_SCORE)

    def set_active_hand(self, hand):
        self.current_player.set_active_hand(hand)
        self.set_state(settings.STATE_ACTIVE_HAND)

    def set_state(self, new_state):
        self.state = new_state
        self.renderer.render(self)

class SingleDeck(Game):

    def __init__(self, users):
        super(SingleDeck, self).__init__(users)
        self.deck = None

    def init_game(self):
        self.deck = Deck.create(1)
        self.deck.shuffle()
        for player in self.players:
            player.clean_hands()
        self.dealer.clean_hands()
        super(SingleDeck, self).init_game()
