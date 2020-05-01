import numpy
import random
import datetime
from SingleGame.models import User, Game, Actions
from django.conf.urls.static import static

from django.contrib.staticfiles.storage import staticfiles_storage

from SingleGame.KEF.DataSetManager import actionFinish, actionDiscard, actionPass, actionDeal, actionInvalid, actionNewGame, actionChangeRole, actionPizzaReady

from SingleGame.GameController.ChefsHatOnlineRenderer import getHandCardsDirectory
import sys
from django.conf import settings

import pandas as pd

import os

import copy

from keras.models import load_model

from SingleGame.KEF.DataSetManager import DataSetManager

def startNewGame(agentsNames, gameStyle):

    expName = str(gameStyle)+"_"+str(agentsNames).replace(" ","").replace("[","_").replace("]","_").replace(",","_").replace("`","_")+ \
              "_" + str(datetime.datetime.now()).replace(" ", "_").replace(":","_").replace(".","_s")

    # expName ="Testing"

    # dirPath = staticfiles_storage.path(expName)
    dirPath = settings.BASE_DIR+settings.STATIC_URL+expName

    os.mkdir(dirPath)

    dsManager = DataSetManager (dataSetDirectory=dirPath)
    dsManager.startNewExperiment()
    dsManager.startNewGame(0, agentsNames)
    dsManager.saveFile()

    return expName

def dealCards(expName):

    # Create deck
    maxCardNumber = 11
    cards = []
    for i in range(maxCardNumber + 1):
      for a in range(i):
        cards.append(maxCardNumber - a)

    # add joker cards
    cards.append(maxCardNumber + 1)  # add a joker card
    cards.append(maxCardNumber + 1)  # add a joker card

    random.shuffle(cards) # Shuffle the deck

    playersHand = []
    for i in range(4):
        playersHand.append([])
    #Deal cards
    numberOfCardsPerPlayer = int(len(cards) / len(playersHand))

    # For each player, distribute the amount of cards
    for playerNumber in range(len(playersHand)):
        playersHand[playerNumber] = sorted(cards[
                                                playerNumber * numberOfCardsPerPlayer:playerNumber * numberOfCardsPerPlayer + numberOfCardsPerPlayer])

    #Define starting player
    startingPlayer = numpy.array(range(4))
    random.shuffle(startingPlayer)
    startingPlayer = startingPlayer[0]

    while not (maxCardNumber in playersHand[startingPlayer]):
      startingPlayer = startingPlayer + 1
      if startingPlayer >= startingPlayer:
        startingPlayer = 0

    # dataSetDirectory = staticfiles_storage.path(expName)
    dataSetDirectory = settings.BASE_DIR+settings.STATIC_URL+expName

    readFile = pd.read_pickle(dataSetDirectory+"/Dataset.pkl")
    dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    dsManager._currentDataSetFile = dataSetDirectory+"/Dataset.pkl"
    dsManager.dataFrame = readFile

    dsManager.dealAction(playersHand=playersHand,game=0)
    dsManager.saveFile()

    return startingPlayer

def validatePlayerAction(actionList, validActions):
    # import sys
    # print("-----------", file=sys.stderr)
    # print ("Action:" + str(actionList), file=sys.stderr)
    # print("len Action:" + str(len(actionList)), file=sys.stderr)
    # print("validActions:" + str(validActions), file=sys.stderr)

    jokerCard = "/deck/12.png"
    error = ""
    correctAction = ""
    if len(actionList)== 0:
        error= "Please select some igredient cards or the pass card!"

    elif actionList[0] == "pass":
        correctAction = "pass"

    else:
        #check is pass is in the action list
        if "pass" in actionList:
            error = "Invalid move! Pass card can not be together with other cards."
        else:
            #check if all the cards are the same or Joker
            allTheSame = False
            previous = actionList[0]
            for a in range(len(actionList)):
                # print(" -- actionList[a]:" + str(actionList[a]), file=sys.stderr)
                # print(" -- previous:" + str(previous), file=sys.stderr)
                # print(" -- jokerCard:" + str(jokerCard), file=sys.stderr)

                if actionList[a] == previous or actionList[a] == jokerCard:
                    allTheSame = False
                    previous = actionList[a]
                else:
                    allTheSame = True
                    break

            # print(" -- allTheSame:" + str(allTheSame), file=sys.stderr)
            if allTheSame:
                # print(" ----- Here!", file=sys.stderr)
                error = "Invalid move! You can only put one type of ingredient per round!"
            else:
                #obtain Q
                q = len(actionList)
                c = 0
                jokerCount = 0
                for a in range(len(actionList)):
                    if actionList[a]== jokerCard:
                        jokerCount = jokerCount+1
                    else:
                        c = actionList[a].split("/")[-1].split(".")[0]

                correctAction = "C"+str(c)+";Q"+str(q)+";J"+str(jokerCount)

                # print(" -- correctAction:" + str(correctAction), file=sys.stderr)
                if not correctAction in validActions:
                    error = "Invalid move! You cannot discard these igredients right now!"

    return correctAction, error

    #    error1 = "Pass Action together with other cards."
    #
    # "CX;QX;JX"

def simulateActions(expName, player, firstAction, currentRound, agentNames):

    gameFinished = False
    import sys

    while not gameFinished:
        action = numpy.zeros(200)
        gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score = doPlayerAction(expName, player, action, firstAction, currentRound, agentNames, isHuman=False)
        if pizza:
            currentRound = doPizza(expName, currentRound)
            player = lastPlayer
        else:
            player = nextPlayer

        firstAction = False

        #
        # print("-----------", file=sys.stderr)
        # print("Next player:" + str(player), file=sys.stderr)
        # print("player1AllowedActions:" + str(len(player1AllowedActions)), file=sys.stderr)
        # print("newRound:" + str(newRound), file=sys.stderr)


    return score



def doPlayerAction(expName, player, action, firstAction, currentRound, agentNames, isHuman=True):
    dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    currentDataset = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
    dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    dsManager.dataFrame = currentDataset

    currentAction = currentDataset.iloc[-1]

    gameNumber = currentAction["Game Number"]
    playersHand = currentAction["Player Hand"]
    board = currentAction["Board"]
    score = currentAction["Scores"]
    roles = currentAction["Roles"]
    rounds = currentAction["Round Number"]
    playerStatus = currentAction["Players Status"]

    playerStatus = numpy.copy(playerStatus).tolist()
    board = numpy.copy(board)
    playersHand = numpy.copy(playersHand)
    playerHand = numpy.copy(playersHand[player])

    if len(board) == 0:
        board = restartBoard()

    newRound = currentRound
    #
    if len(playerStatus) == 0:
        playerStatus = []
        for a in range(4):
            playerStatus.append([])

    possibleActions, currentHighLevelActions, highLevelActions = getPossibleActions(expName, player, firstAction)

    if isHuman:
        if player == 0:
          action, error = validatePlayerAction(action, currentHighLevelActions)
          if not error =="":
              return False, False, player, newRound, -1, False, error, score


        actionIndex = highLevelActions.index(action)

        action = numpy.zeros(200)
        action[actionIndex] = 1
    else:
        stateVector = []
        for a in playerHand:
            stateVector.append(a)
        for a in board:
            stateVector.append(a)

        stateVector = numpy.array(stateVector) / 13

        action = doAgentAction(possibleActions, stateVector, agentNames[player])
        actionIndex = numpy.argmax(action)

        import sys
        print("---------", file=sys.stderr)
        print("Player:" + str(player), file=sys.stderr)
        print("action:" + str(action), file=sys.stderr)
        print("actionIndex:" + str(actionIndex), file=sys.stderr)

    loss = []
    totalActions = 1

    #Pass action:
    if actionIndex == 199:
        reward = -0.01
        actionComplete = (actionPass, [0])
        cardsDiscarded = []
    else:
        cardsDiscarded, board, playerHand = discardCards(playerHand,action, highLevelActions)
        reward = -0.01
        actionComplete = (actionDiscard, cardsDiscarded)

    if numpy.array(playerHand).sum() == 0: # If all the cards of the player hands are gone, he wins the match, maximum reward

            score = score.tolist()
            if not player in score:
                score.append(player)

            index = score.index(player)
            if index == 0:
                reward = 1
            else:
                reward = -0.1

            actionComplete = (actionFinish, cardsDiscarded)

    if len(playerStatus) <= player:
        playerStatus.append(actionComplete)
    else:
        playerStatus[player] = actionComplete

    playersHand[player] = playerHand
    dsManager.doActionAction(gameNumber, player, newRound,
                                                    actionComplete, board,
                                                    0, reward,
                                                    playersHand, roles,
                                                    score, playerStatus,
                                                    action, loss, totalActions, possibleActions)

    dsManager.saveFile()

    playerHand = numpy.array(playerHand)
    hasPlayerFinished = playerHand.sum() == 0
    gameFinished = hasGameFinished(playersHand)

    nextPlayer = player + 1
    if nextPlayer == 4:
        nextPlayer = 0

    lastPlayer = -1
    pizza = False
    if not gameFinished:
        if len(playerStatus) == 4 and len(playerStatus[nextPlayer]) > 0:
            while playerStatus[nextPlayer][0] == actionFinish or playerStatus[nextPlayer][0] == actionPass:
                nextPlayer = nextPlayer + 1
                if nextPlayer == 4:
                    nextPlayer = 0

        playerFinishedCounter = 0
        lastPlayer = player


        for indexStatus, status in enumerate(playerStatus):

            if len(status) > 0 and not status[0] =="":
                if status[0] == actionDiscard:
                    playerFinishedCounter += 1
                    lastPlayer = indexStatus
            else:
                playerFinishedCounter += 2

        if playerFinishedCounter <= 1:
            pizza = True

    error = ""
    return gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score

def doPizza(expName, currentRound):

    dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    currentDataset = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
    dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    dsManager.dataFrame = currentDataset

    currentAction = currentDataset.iloc[-1]

    gameNumber = currentAction["Game Number"]
    playersHand = currentAction["Player Hand"]
    score = currentAction["Scores"]
    roles = currentAction["Roles"]
    rounds = currentAction["Round Number"]
    playerStatus = currentAction["Players Status"]
    playersHand = numpy.copy(playersHand)

    board = restartBoard()
    for a in range(len(playerStatus)):
        if not playerStatus[a][0] == actionFinish:
            playerStatus[a] = [""]

    dsManager.doActionPizzaReady(rounds, board, playersHand, roles, score, playerStatus, gameNumber)

    dsManager.saveFile()

    if currentRound == rounds:
        currentRound += 1

    return currentRound


def hasGameFinished(playersHand):

  for i in range(len(playersHand)):
      # print ("PLayer:" + str(i) + " : ", str(numpy.array(self.playersHand[i]).sum()))
      if numpy.array(playersHand[i]).sum() > 0:
          return False

  return True

def restartBoard():
    # clean the board
    maxCardNumber = 11
    board = []
    for i in range(maxCardNumber):
        board.append(0)

    # start the game with the highest card
    board[0] = maxCardNumber + 2

    return board
    # input ("Board:" + str(self.board))

def discardCards(playerHand, action, highLevelActions):

  playerHand = numpy.copy(playerHand)

  cardsToDiscard = []
  actionIndex = numpy.argmax(action)
  takenAction = highLevelActions[actionIndex].split(";")
  cardValue = int(takenAction[0][1:])
  cardQuantity = int(takenAction[1][1:])
  jokerQuantity = int(takenAction[2][1:])

  for q in range(cardQuantity):
      cardsToDiscard.append(cardValue)
  for j in range(jokerQuantity):
      cardsToDiscard.append(12)

  board = restartBoard()

  originalCardDiscarded = cardsToDiscard.copy()
  # remove them from the players hand and add them to the board
  boardPosition = 0
  for cardIndex in range(len(playerHand)):
      # print ("Cards to discard:", len(cardsToDiscard))
      for i in cardsToDiscard:
          # print("Card to discard:", i)
          # print("card in player hand:", self.playersHand[player][cardIndex] )
          if playerHand[cardIndex] == i:
              # print ("removing...")

              playerHand[cardIndex] = 0
              # self.playersHand[player].remove(i)
              cardsToDiscard.remove(i)
              board[boardPosition] = i
              boardPosition = boardPosition + 1

  playerHand = sorted(playerHand)
  return originalCardDiscarded, board, playerHand


def doAgentAction(possibleActions, state, agent):

    import keras.backend as K
    def loss(y_true, y_pred):
        LOSS_CLIPPING = 0.2  # Only implemented clipping for the surrogate loss, paper said it was best
        ENTROPY_LOSS = 5e-3
        y_tru_valid = y_true[:, 0:200]
        old_prediction = y_true[:, 200:400]
        advantage = y_true[:, 400][0]

        prob = K.sum(y_tru_valid * y_pred, axis=-1)
        old_prob = K.sum(y_tru_valid * old_prediction, axis=-1)
        r = prob / (old_prob + 1e-10)

        return -K.mean(K.minimum(r * advantage, K.clip(r, min_value=1 - LOSS_CLIPPING,
                                                       max_value=1 + LOSS_CLIPPING) * advantage) + ENTROPY_LOSS * -(
                prob * K.log(prob + 1e-10)))


    agentName = agent.split("_")[0]

    if agentName == "DQL":
        modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_DQL.hd5"
    elif agentName == "A2C":
        modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_A2C.hd5"
    elif agentName == "PPO":
        modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_PPO.hd5"

    elif agentName == "Random":
        return doRandomAction(possibleActions)

    actor = load_model(modelDirectory, custom_objects={'loss':loss})

    stateVector = numpy.expand_dims(numpy.array(state), 0)

    possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions), 0)
    a = actor.predict([stateVector, possibleActionsVector])[0]

    # if numpy.array(possibleActions).sum() == 1:
    #     a = numpy.zeros(200)
    #     a[199]=1

    import sys
    print("---------", file=sys.stderr)
    print("Agent:" + str(agent), file=sys.stderr)
    print ("possibleActions2:" + str(possibleActionsVector), file=sys.stderr )
    print ("stateVector:" + str(stateVector), file=sys.stderr )
    print("a:" + str(a), file=sys.stderr)
    print("len(a):" + str(len(a)), file=sys.stderr)



    return a

def doRandomAction(possibleActions):

    possibleActions = numpy.copy(possibleActions)

    possibleActions = possibleActions

    itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()
    random.shuffle(itemindex)
    aIndex = itemindex[0]
    a = numpy.zeros(200)
    a[aIndex] = 1

    return a

def getPossibleActions(expName, player, firstAction):

    dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    readFile = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")

    currentAction = readFile.iloc[-1]

    playerHand = currentAction["Player Hand"][player]
    board = currentAction["Board"]
    actionType = currentAction["Action Type"]
    playerStatus = currentAction["Players Status"]

    highLevelActions = []
    possibleActions = []


    # import sys
    # print("---------", file=sys.stderr)
    # print("Player:" + str(player), file=sys.stderr)
    # print("Player Hand:" + str(playerHand), file=sys.stderr)
    # print("Board:" + str(board), file=sys.stderr)
    # print ("First action:" + str(firstAction), file=sys.stderr )

    if actionType == actionDeal:
        board = numpy.zeros(11)
        board[0] = 13

    if not actionType == "":

        maxCardNumber = 11

        unique, counts = numpy.unique(board, return_counts=True)
        currentBoard = dict(zip(unique, counts))

        unique, counts = numpy.unique(playerHand, return_counts=True)
        currentPlayerHand = dict(zip(unique, counts))

        highestCardOnBoard = 0
        for boardItem in currentBoard:
            if not boardItem == maxCardNumber + 1:
                highestCardOnBoard = boardItem

        jokerQuantityBoard = 0

        if maxCardNumber + 1 in board:
            jokerQuantityBoard = currentBoard[maxCardNumber + 1]

        #
        # print("Possible actions:", possibleActions)

        cardDescription = ""
        for cardNumber in range(maxCardNumber):
            for cardQuantity in range(cardNumber + 1):

                # if cardQuantity == 0:
                #       print (len(possibleActions))
                if (cardNumber + 1 < highestCardOnBoard) and cardNumber + 1 in playerHand:

                    if currentPlayerHand[cardNumber + 1] >= cardQuantity + 1 and (currentBoard[
                                                                                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # taking into consideration the amount of jokers in the board

                        if firstAction:  # if this is the first move
                            # print("--- First Action:")
                            if cardNumber + 1 == maxCardNumber:  # if this is the highest card
                                # print("----- First Action Added!")
                                possibleActions.append(1)
                            else:
                                possibleActions.append(0)

                        else:

                            possibleActions.append(1)

                    else:

                        possibleActions.append(0)
                else:
                    possibleActions.append(0)

                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2")
                # if cardNumber

                # add the joker possibilities
                if maxCardNumber + 1 in playerHand:  # there is a joker in the hand
                    jokerQuantity = currentPlayerHand[maxCardNumber + 1]

                    if (
                            cardNumber + 1 < highestCardOnBoard) and cardNumber + 1 in playerHand:  # if I have the card in hand and it is lower than the one in the field

                        # for one joker
                        if currentPlayerHand[cardNumber + 1] >= cardQuantity and (currentBoard[
                                                                                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # verify if the amount of cards in the hand + a joker is more than the card quantity and if the cards in the board + possible jokers is more than the card quantity
                            if firstAction:  # if this is the first move
                                if cardNumber + 1 == maxCardNumber:  # if this is the highest card
                                    possibleActions.append(1)  # I can discard one joker

                                else:
                                    possibleActions.append(0)  # I cannot discard one joker


                            else:
                                possibleActions.append(1)  # I can discard one joker

                        else:
                            possibleActions.append(0)  # I cannot discard one joker

                        if jokerQuantity == 2:
                            # for two joker
                            if currentPlayerHand[cardNumber + 1] >= cardQuantity - 1 and (currentBoard[
                                                                                              highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # if the amount of cards in board and in the hand are the same or more than cardNumber quantity

                                if firstAction:  # if this is the first move
                                    if cardNumber + 1 == maxCardNumber:  # if this is the highest card
                                        possibleActions.append(1)  # I can discard two jokers

                                    else:
                                        possibleActions.append(0)  # I can discard two jokers

                                else:
                                    possibleActions.append(1)  # I can discard two jokers

                            else:
                                possibleActions.append(0)  # I cannot discard two jokers


                        else:
                            possibleActions.append(0)  # I cannot discard two jokers


                    else:  # there is no joker in the hand
                        possibleActions.append(0)  # I cannot discard one joker

                        possibleActions.append(0)  # I cannot discard two joker


                else:
                    possibleActions.append(0)  # I cannot discard one joker

                    possibleActions.append(0)  # I cannot discard two joker

        highLevelActions.append("C0;Q0;J1")
        if maxCardNumber + 1 in playerHand:  # there is a joker in the hand
            if firstAction:
                possibleActions.append(0)
            else:
                if highestCardOnBoard == maxCardNumber + 2:
                    possibleActions.append(1)  # I can discard the joker

                else:
                    possibleActions.append(0)  # I cannot discard the joker

        else:
            possibleActions.append(0)  # I can not discard one joker

        if firstAction:
            possibleActions.append(0)
        else:
            possibleActions.append(1)  # the pass action, which is always a valid action when not first action
        highLevelActions.append("pass")

        highLevelActions = highLevelActions

    nonzeroElements = numpy.nonzero(possibleActions)
    currentlyAllowedActions = numpy.copy(numpy.array(highLevelActions)[nonzeroElements, ])

    # print("---------", file=sys.stderr)
    # print("playerStatus:" + str(playerStatus), file=sys.stderr)
    # print("player:" + str(player), file=sys.stderr)
    # print("playerHand:" + str(playerHand), file=sys.stderr)
    # print("board:" + str(board), file=sys.stderr)
    # print("firstAction:" + str(firstAction), file=sys.stderr)
    # print("possibleActions:" + str(possibleActions), file=sys.stderr)
    # print("highLevelActions:" + str(highLevelActions), file=sys.stderr)
    # print("currentlyAllowedActions:" + str(currentlyAllowedActions), file=sys.stderr)
    # print("---------", file=sys.stderr)


    if len(playerStatus) > 0 and len(playerStatus[player]) > 0 and playerStatus[player][0] == actionPass:
        currentlyAllowedActions = []
        possibleActions = numpy.zeros(200)
        possibleActions[199] = 1
        currentlyAllowedActions.append("pass")

        return possibleActions, currentlyAllowedActions, highLevelActions

    return possibleActions, currentlyAllowedActions[0], highLevelActions