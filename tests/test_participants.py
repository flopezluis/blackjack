import pytest
import settings
import unittest
from participants import Participant, Player, Dealer, Hand
from game import Game, Deck, SingleDeck
from renderers import ParticipantTextRender, HandTextRender
from mock import Mock
from mock import ANY
from mock import patch

class ParticipantTest(unittest.TestCase):

    def test_default_render(self):
        player = Participant("Foo", 100)
        assert isinstance(player.renderer, ParticipantTextRender)

    def test_nohand(self):
        player = Participant("Foo", 100)
        assert player.get_active_hand() == None

    def test_new_hand(self):
        player = Participant("Foo", 100)
        player.new_hand(50)
        assert player.hands[0] == player.get_active_hand()
        assert player.get_active_hand().bet == 50

    def test_clean_hand(self):
        player = Participant("Foo", 100)
        player.new_hand(50)
        player.clean_active_hand()
        assert player.hands == []

    def test_clean_hands(self):
        player = Participant("Foo", 100)
        player.new_hand(50)
        player.new_hand(50)
        player.clean_hands()
        assert player.hands == []

    def test_valid_bet(self):
        player = Player("Foo", 100)
        player.new_hand(50)
        assert player.hands[0] == player.get_active_hand()
        assert player.get_active_hand().bet == 50
        assert not player.make_bet(130)

    def test_bet(self):
        player = Player("Foo", 100)
        assert player.money == 100
        player.make_bet(50)
        assert player.money == 50
        assert player.get_active_hand().bet == 50

    def test_win_bet(self):
        player = Player("Foo", 100)
        player.make_bet(60)
        assert player.money == 40
        player.win_bet()
        assert player.money == 160

    def test_win_bet_two_hands(self):
        player = Player("Foo", 100)
        player.make_bet(30)
        assert player.money == 70
        player.make_bet(30)
        assert player.money == 40
        player.win_bet()
        assert player.money == 160
        player.win_bet()
        assert player.money == 160

    def test_actions(self):
        player = Player("Foo", 100)
        game = Game([player])
        player.new_hand(50)
        player.get_active_hand().hit = Mock()
        player.hit(game)
        player.get_active_hand().hit.assert_called_with(game)

        player.get_active_hand().stand = Mock()
        player.stand(game)
        player.get_active_hand().stand.assert_called_with(game)

        assert len(player.hands) == 1
        player.get_active_hand().split = Mock()
        player.split(game)
        player.get_active_hand().split.assert_called_with(game)

        assert len(player.hands) == 2

    def hit_dealer(self):
        player = Player("Foo", 100)
        game = Game(player)
        game.dealer.hit(game)
        game.dealer.hit(game)
        cards = game.dealer.hands[0]
        assert cards[1].hidden

class HandTest(unittest.TestCase):

    def test_default_render(self):
        hand = Hand()
        assert isinstance(hand.renderer, HandTextRender)

    def test_cards(self):
        hand = Hand()
        deck = Deck.create(1)
        card = deck.get_card()
        card.hidden = True
        hand.add_card(card)
        hand.add_card(deck.get_card())
        assert any([card.hidden for card in hand.cards])
        hand.reveal()
        assert all([not card.hidden for card in hand.cards])

    def test_split(self):
        hand = Hand(60)
        assert hand.bet == 60
        deck = Deck.create(1)
        card1 = deck.get_card()
        card2 = deck.get_card()
        hand.add_card(card1)
        hand.add_card(card2)
        player = Player("Foo", 100)
        game = Game([player])
        new_hand = hand.split(game)
        assert len(hand.cards) == 1
        assert hand.cards[0] == card1
        assert hand.bet == 30
        assert len(new_hand.cards) == 1
        assert new_hand.cards[0] == card2
        assert new_hand.bet == 30

    def test_can_do_split(self):
        hand = Hand(60)
        deck = Deck.create(1)
        while (len(hand.cards) < 2 and not deck.is_empty()):
            card = deck.get_card()
            if card.value > 9:
                hand.add_card(card)
        assert hand.can_do_split()

    def test_hand(self):
        hand = Hand(60)
        player = Player("Foo", 100)
        game = Game([player])
        hand.stand(game)
        assert hand.is_stand()

    def test_hit(self):
        hand = Hand(60)
        player = Player("Foo", 100)
        game = SingleDeck([player])
        deck = Deck.create(1)
        game.get_card = Mock(return_value=deck.get_card())
        hand.hit(game)
        assert len(hand.cards) == 1

    def test_get_score(self):
        hand = Hand(60)
        deck = Deck.create(1)
        card1 = deck.get_card()
        card2 = deck.get_card()
        hand.add_card(card1)
        hand.add_card(card2)

        assert hand.get_score() == card1.value + card2.value
