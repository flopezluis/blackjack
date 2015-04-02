#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 2.7
__author__ = "Felix"
__version__ = "0.8"
__email__ = "hola@flopezluis"

import settings
from participants import Player
from game import Game, SingleDeck

def game_logic(players):
    game = SingleDeck(players)

    while not game.is_over():
        print "\n ======= New Game ======= \n"
        game.init_game()
        for player in players:
            game.set_current_player(player)
            game.process_hand()

def ask_players():
    players = []
    num = input("How many players?\n")
    for _ in range(num):
        name = raw_input("What's the name of the new player?\n")
        players.append(Player(str(name), settings.PLAYER_CHIPS))
    return players

if __name__ == '__main__':
    game_logic(ask_players())
