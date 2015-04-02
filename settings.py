DEALER_NAME = "Dealer"
DEALER_MIN_SCORE = 17
BLACKJACK = 21
CARDS_FOR_BLACKJACK = 2
MIN_CARD_TO_SPLIT = 10
PLAYER_CHIPS = 100
DEALER_CHIPS = 100000
#key is the representation and value is the real value
DECK_CONF = {
        "cards" : {
        "A": 11,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10,
        },
    "suits": {
        "Spades": u"\u2660 (black)",
        "Hearts": u"\u2665 (red)",
        "Diamond": u"\u2666 (red)",
        "Club": u"\u2663 (black)"
        }
    }

STATE_WINNER_BIGGER_SCORE = 0
STATE_BLACKJACK = 1
STATE_BUSTED = 2
STATE_ACTIVE_HAND = 3
STATE_NEXT_TURN = 4
STATE_PLAYER_TURN = 5
STATE_DEALER_TURN = 6
