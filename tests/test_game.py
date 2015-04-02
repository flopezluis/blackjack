import pytest
import unittest
import settings
from participants import Player, Hand
from game import Game, Deck, SingleDeck
import __builtin__
from mock import Mock
from mock import ANY
from mock import patch

#This allows us to monkeypatch the builtin input
original_input = __builtin__.input
def back_to_normal_input():
    __builtin__.input = original_input

class CardTest(unittest.TestCase):

    def test_shuffle(self):
        deck = Deck.create(1)
        cards = list(deck.deck)
        deck.shuffle()
        assert cards[0] != deck.deck[0]

    def test_is_empty(self):
        deck = Deck.create(1)
        cards = list(deck.deck)
        assert not deck.is_empty()
        try:
            while True:
                deck.get_card()
        except:
            assert deck.is_empty()

class GameTest(unittest.TestCase):

    def test_default_dealer(self):
        player = Player("Foo", 100)
        game = Game([player])
        assert game.dealer

    def test_init_game(self):
        player = Player("Foo", 100)
        game = SingleDeck([player])
        def fake_input(a):
            return 40
        __builtin__.input = fake_input
        game.init_game()
        game.set_current_player(player)
        assert player in game.players
        assert len(game.players[0].hands[0].cards) == 2
        assert len(game.dealer.hands[0].cards) == 2

    def test_ask_bet(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 40
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        assert game.players[0].hands[0].bet == 40
        back_to_normal_input()

    def test_game_is_over(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 100
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        assert game.is_over()
        back_to_normal_input()

    def test_process_turn(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 100
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        def fake_input2(a):
            return 1
        __builtin__.input = fake_input2
        player.turn = Mock()
        game.process_turn(game.players[0])
        player.turn.assert_called_with(game)
        back_to_normal_input()

    def test_blackjack_or_busted(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 40
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        player.hands[0].cards[0]._value = 10
        player.hands[0].cards[1]._value = 11
        player.win_bet = Mock()
        assert player == game.blackjack_or_busted(player, game.dealer)
        player.win_bet.assert_called_with(None)

        player.hands[0].cards[0]._value = 11
        assert game.dealer == game.blackjack_or_busted(player, game.dealer)

    def test_process_hand_player_busted(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 40
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        player.hands[0].cards[0]._value = 10
        player.hands[0].cards[1]._value = 9

        def fake_input_option_hit(a):
            if game.players[0].get_score() < 21:
                return 0
            else:
                return 1
        __builtin__.input = fake_input_option_hit
        game.renderer.render_busted = Mock()
        game.set_current_player(player)
        game.process_hand()
        game.renderer.render_busted.assert_called_with(game)
        assert game.winner == game.dealer

    def test_process_hand_dealer_busted(self):
        player = Player("Foo", 100)
        def fake_input(a):
            return 40
        __builtin__.input = fake_input
        game = SingleDeck([player])
        game.init_game()
        game.set_current_player(player)
        player.hands[0].cards[0]._value = 10
        player.hands[0].cards[1]._value = 9

        def fake_input_option_hit(a):
            return 1
        __builtin__.input = fake_input_option_hit

        settings.DEALER_MIN_SCORE = 22
        game.renderer.render_busted = Mock()
        game.set_current_player(player)
        game.process_hand()
        game.renderer.render_busted.assert_called_with(game)
        assert game.winner == player
