#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings

class Render(object):

    def render(self):
        raise NotImplementedError

class TextRender(Render):

    def render(self):
        pass

class CardTextRender(TextRender):

    def render(self, card):
        """This method should render the card representation."""
        if card.hidden:
            print "     [X] - hidden"
        else:
            print "     %s - %s" % (card.representation, card.suit)

class DeckTextRender(TextRender):

    def render(self, deck):
        """This method should render the card representation."""
        for card in deck.deck:
            print card.render()

class ParticipantTextRender(TextRender):

    def render(self, player):
        """This method should render the participant representation."""
        hand = player.get_active_hand()
        print "%s cards:" % player.name
        hand.render()
        print "Score %s" % player.get_score()

    def render_active_hand(self, player):
        print "Hand: %d" % player.hands.index(player.get_active_hand())

    def render_options(self, player):
        print "What do you want to do?"
        for i, action in enumerate(player.allowed_actions()):
            print " %d - %s" % (i, action.im_func.__name__)

class HandTextRender(TextRender):

    def render(self, hand):
        """This method should render the hand representation."""
        for card in hand.cards:
            card.render()

class GameTextRender(TextRender):

    def render(self, game):
        """This method should render the game status."""
        state = game.state
        if state == settings.STATE_WINNER_BIGGER_SCORE:
            self.render_winner(game.winner)
        elif state == settings.STATE_BLACKJACK:
            self.render_blackjack(game)
        elif state == settings.STATE_BUSTED:
            self.render_busted(game)
        elif state == settings.STATE_ACTIVE_HAND:
            game.current_player.render_active_hand()
            game.current_player.render()
            game.dealer.render()
        elif state == settings.STATE_NEXT_TURN:
            self.render_status(game)
        elif state == settings.STATE_PLAYER_TURN:
            self.render_turn(game.current_player)
        elif state == settings.STATE_DEALER_TURN:
            self.render_turn(game.dealer)

    def render_status(self, game):
        game.current_player.render()
        game.dealer.render()

    def render_busted(self, game):
        busted = game.dealer
        if game.winner == game.dealer:
            busted = game.current_player
        print "-" * 30
        print "Sorry %s you're Busted!\n" % (busted)
        busted.render()
        print "-" * 30

    def render_blackjack(self, game):
        print "-" * 30
        print "Blackjack for %s!!\n" % (game.winner)
        game.winner.render()
        print "-" * 30

    def render_turn(self, player):
        print "=" * 30
        print " %s is playing" % player.name
        print "=" * 30

    def render_winner(self, player):
        print "-" * 30
        print "Winner => %s\n" % (player)
        player.render()
        print "-" * 30
