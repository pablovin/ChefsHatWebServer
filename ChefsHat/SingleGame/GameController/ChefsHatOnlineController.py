import numpy
import random
import datetime
from django.utils.translation import ugettext as _

from SingleGame.KEF.DataSetManager import actionFinish, actionNone, actionDiscard, actionPass, actionDeal, actionInvalid, actionNewGame, actionChangeRole, actionPizzaReady, actionSpecialAction

from tensorflow.keras.backend import clear_session
import gc

from django.conf import settings

import sys

import os

import copy

from keras.models import load_model

from SingleGame.KEF.DataSetManager import exportDBToFiles, getRank, saveRank, getexperimentModelDS, getLastEntryDS, startNewExperimentDS, startNewGameDS, dealActionDS, declareSpecialActionDS, exchangeRolesActionDS, doActionActionDS, doActionPizzaReadyDS

import keras.backend as K
import tensorflow as tf

def exportDB():
    savingPath = settings.BASE_DIR + settings.STATIC_URL + "/"
    exportDBToFiles(savingPath)



def getExperimentByName(experimentName):
    expModel = getexperimentModelDS(experimentName)
    return expModel

def getPerformanceScore():

    scores = []
    ranks = getRank()
    for index,rank in enumerate(ranks):
        scores.append([ rank.time, rank.nickName, rank.score])

    if len(scores) > 0:
        scores = sorted(scores, key=lambda a_entry: a_entry[2])
        scores = scores[::-1]

    return scores


def savePerformanceScore(performanceScore, nickName):
    saveRank(nickName, performanceScore)
    # current_time = datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    # filePath = settings.BASE_DIR + settings.STATIC_URL + "/performanceScore_Player.csv"
    # if not os.path.exists(filePath):
    #
    #     with open(filePath, mode='a') as performance:
    #         employee_writer = csv.writer(performance, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #         employee_writer.writerow(['Date', 'Nickname', 'Score'])
    #
    # with open(filePath, mode='a') as performance:
    #     employee_writer = csv.writer(performance, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     employee_writer.writerow([current_time,nickName, performanceScore])


# def saveDataset(dataFrame, expName):
#     dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
#
#     # currentDataset = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
#     dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
#     dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
#     dsManager.loadDataFrame(dataFrame)
#     dsManager.saveFile()

def createNewExperiment(agentsNames, gameStyle, language):

    # expName = str(gameStyle) + "_" + str(agentsNames).replace(" ", "").replace("[", "_").replace("]", "_").replace(",",
    #                                                                                                                "_").replace(
    #     "`", "_") + \
    #           "_" + str(datetime.datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_s")

    current_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    expName = str(language)+"_"+str(current_time).replace(" ", "_").replace(":", "_").replace(".", "_s") + "_"+  str(gameStyle) + str(agentsNames).replace(" ", "").replace("[", "_").replace("]", "_").replace(",","_").replace("`", "_")
    expName = "games/"+expName.replace("'", "")[0:-1]

    # expName ="Testing"

    # dirPath = staticfiles_storage.path(expName)
    dirPath = settings.BASE_DIR + settings.STATIC_URL + expName

    if not os.path.exists(settings.BASE_DIR + settings.STATIC_URL+"/games"):
        os.mkdir(settings.BASE_DIR + settings.STATIC_URL+"/games")

    os.mkdir(dirPath)

    expModel = startNewExperimentDS(expName)

    return expName, expModel

def newGame(expModel, agentsNames, gameNumber, roles, performanceScore):

    startNewGameDS(expModel, gameNumber, agentsNames, roles, performanceScore)


def dealCards(expModel, gameNumber):

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

    newPlayersHand = []
    for i in range(4):
        newPlayersHand.append([])
    #Deal cards
    numberOfCardsPerPlayer = int(len(cards) / len(newPlayersHand))

    # For each player, distribute the amount of cards
    for playerNumber in range(len(newPlayersHand)):
        newPlayersHand[playerNumber] = sorted(cards[
                                                playerNumber * numberOfCardsPerPlayer:playerNumber * numberOfCardsPerPlayer + numberOfCardsPerPlayer])

    if settings.ALLOW_TWO_JOKERS_PLAYER1:
        """Guarantee that player 1 has two jokers"""
        newPlayersHand[0][-1] = maxCardNumber + 1
        newPlayersHand[0][-2] = maxCardNumber + 1
        """Guarantee that player 1 has two jokers"""

    #Define starting player
    startingPlayer = numpy.array(range(4))
    random.shuffle(startingPlayer)
    startingPlayer = startingPlayer[0]

    while not (maxCardNumber in newPlayersHand[startingPlayer]):
      startingPlayer = startingPlayer + 1
      if startingPlayer >= startingPlayer:
        startingPlayer = 0

    currentAction = getLastEntryDS(expModel)

    roles = currentAction.roles

    # print ("Roles:" + str(roles))

    dealActionDS(expModel=expModel, playersHand=newPlayersHand,game=gameNumber, roles=roles)

    return int(startingPlayer)

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
        error=  _('error_SelectIgridient')

    elif actionList[0] == "pass":
        correctAction = "pass"

    else:
        #check is pass is in the action list
        if "pass" in actionList:
            error = _('error_InvalidMove_Pass')
        else:
            #check if all the cards are the same or Joker
            notAllTheSame = False
            previous = actionList[0]
            for a in range(len(actionList)):
                # print(" -- actionList[a]:" + str(actionList[a]), file=sys.stderr)
                # print(" -- previous:" + str(previous), file=sys.stderr)
                # print(" -- jokerCard:" + str(jokerCard), file=sys.stderr)

                if actionList[a] == previous or actionList[a] == jokerCard:
                    notAllTheSame = False
                    previous = actionList[a]
                else:
                    notAllTheSame = True
                    break

            # print(" -- allTheSame:" + str(allTheSame), file=sys.stderr)
            if notAllTheSame:
                # print(" ----- Here!", file=sys.stderr)
                error = _('error_InvalidMove_OneIgridient')
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
                q = q-jokerCount
                correctAction = "C"+str(c)+";Q"+str(q)+";J"+str(jokerCount)

                # print(" -- correctAction:" + str(correctAction), file=sys.stderr)
                if not correctAction in validActions:
                    error = _('error_InvalidMove_CannotDiscard')
    #             print ("Q:" + str(q))
    #             print("C:" + str(c))
    #             print("joker count:" + str(jokerCount))
    # print("correctAction:" + str(correctAction))
    # input("here")
    return correctAction, error

    #    error1 = "Pass Action together with other cards."
    #
    # "CX;QX;JX"

def simulateActions(expModel, player, firstAction, currentRound, agentNames, finishedRounds):

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

    loadedModels = []
    clear_session()
    for agent in agentNames:
        if agent == "Avery":
            # doRandomAction(possibleActions)
            modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_DQL.hd5"
            loadedModels.append(load_model(modelDirectory, custom_objects={'loss': loss}))
            # print("LOADED DQL!", file=sys.stderr)
        elif agent == "Cass":
            modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_PPO.hd5"
            loadedModels.append(load_model(modelDirectory, custom_objects={'loss': loss}))


    gameFinished = False

    while not gameFinished:
        action = numpy.zeros(200)
        # print("--------INSIDE SIMULATE ACTION-----------", file=sys.stderr)
        # print("--- Next player:" + str(agentNames[player]), file=sys.stderr)
        # print("--- Round:" + str(currentRound), file=sys.stderr)
        # print("--- Action:" + str(action), file=sys.stderr)
        # print("player Name:" + str(agentNames[player]), file=sys.stderr)

        gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score, cardsDiscarded = doPlayerAction(
                        expModel, player, action, firstAction, currentRound, agentNames, loadedModels,
                        False)

        if hasPlayerFinished:
            finishedRounds[player] = newRound+1

        # print("After Do Action ROund:" + str(currentRound), file=sys.stderr)
        # print("Player Finished:" + str(hasPlayerFinished), file=sys.stderr)
        # print("Pizza:" + str(pizza), file=sys.stderr)

        if pizza:
            print(" --- PIZZA!!!", file=sys.stderr)
            currentRound = doPizza(expModel, currentRound)
            # print("New Pizza Round:" + str(currentRound), file=sys.stderr)
            player = lastPlayer
        else:
            player = nextPlayer

        firstAction = False


    # dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.loadDataFrame(newDataFrame)
    #
    # currentAction = dsManager.dataFrame.tail(1)
    # print("---Loading the data frame---:", file=sys.stderr)
    # print("score: " + str(currentAction["Scores"].tolist()[0]), file=sys.stderr)
    # print("---Loading the data frame---:", file=sys.stderr)



    return score, finishedRounds


def getPlayerCardFromScreen(playerChosencards):

    playerCards = []
    for card in playerChosencards:
        playerCards.append(int(card.split("/")[2].split(".")[0]))

    return playerCards


def getScreenCardFromPlayer(playerChosencards):

    playerCards = []
    if isinstance (playerChosencards,int):
        playerChosencards = [playerChosencards]

    for card in playerChosencards:
        playerCards.append("/deck" + "/"  + str(card) + ".png")

    return playerCards

def validateChangeRolesCard(playerRole, playerHand, playerChosenCards, allowCheating):

    error = ""
    isWrong = False
    # print ("-------------")
    # print ("Player role:" + str(playerRole))
    # print("-------------")

    playerHand.sort()
    playerChosenCards.sort()

    playerChosenCards = getPlayerCardFromScreen(playerChosenCards)
    if playerRole == 0:

        if not len(playerChosenCards) == 2:
            isWrong = True
            error = _('error_Card_TwoCards')
    elif playerRole == 1:
        if not len(playerChosenCards) == 1:
            isWrong = True
            error = _('error_Card_OneCard')
    elif playerRole == 2:
        if not len(playerChosenCards) == 1:
            isWrong = True
            error = _('error_Card_OneCard_Smallest')
        else:
            if not allowCheating:
                smallerCard = playerHand[0]
                smallerSelectedCard = playerChosenCards[0]
                if not smallerSelectedCard == smallerCard:
                    isWrong = True
                    error = _('error_Card_SmallestCard')

    elif playerRole == 3:
        if not len(playerChosenCards) == 2:
            isWrong = True
            error = _('error_Card_TwoCards_Smallest')
        else:
            if not allowCheating:
                smallerCard = playerHand[0:2]
                smallerSelectedCard = playerChosenCards[0:2]
                if not smallerCard == smallerSelectedCard:
                    isWrong = True
                    error = _('error_Card_TwoSmallestCards')


    return error, isWrong, playerChosenCards


def getPlayerActivatedSpecialCard(playerHand, role):

    hasSpecialCard = False
    card = ""
    if playerHand.count(12) == 2:
        hasSpecialCard = True
        if role == 4:
            card = "Fight"
        else:
            card = "Dinner"

    return hasSpecialCard, card

def getPlayerRoleExchangeCards(playerHand, role):
    cards = []
    if role == 0:
         cards= sorted(playerHand)[-3:-1]

    elif role == 1:
        cards = sorted(playerHand)[-1]

    elif role == 2:
        cards = sorted(playerHand)[0]

    else:
        cards = sorted(playerHand)[0:2]

    return cards

def changeRolesOthers(expModel, playerRole):

    # print ("EXPModel:" + str(expModel))
    currentAction = getLastEntryDS(expModel)

    playersHand = currentAction.playerHand
    roles = currentAction.roles
    gameNumber = currentAction.gameNumber

    chef, souschef, waiter, dishwasher = playerRole.index(0), playerRole.index(1), playerRole.index(2), playerRole.index(3)
    cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher = [], [], [], []

    #Check if any of them invoked a special card
    hasSpecialCard = False
    specialCard = ""
    for index, playerDidAction in enumerate([chef, souschef, waiter, dishwasher]):
        if not playerDidAction == 0:
            hasSpecialCard, specialCard = getPlayerActivatedSpecialCard(playersHand[playerDidAction], index)
            if hasSpecialCard:
                break

    # """Player 2 called for dinner served!"""
    # hasSpecialCard = True
    # specialCard = "Fight"
    # playerDidAction = 2
    # """Player 2 called for dinner served!"""

    newRoles = playerRole


    #If food fight was called, invert all positions
    if hasSpecialCard and specialCard == "Fight":
        newChef = dishwasher
        newSouschef = waiter
        newWaiter = souschef
        newDishwasher = chef

        chef,souschef,waiter,dishwasher = newChef, newSouschef, newWaiter, newDishwasher
        newRoles = []

        for playerNumber in range(4):
            newRoles.append([chef,souschef,waiter,dishwasher].index(playerNumber))

        declareSpecialActionDS(expModel, playerDidAction, playersHand, newRoles, specialCard, gameNumber)


    elif hasSpecialCard and specialCard == "Dinner":

        declareSpecialActionDS(expModel, playerDidAction, playersHand, roles, specialCard, gameNumber)

        return [], [], [], [], None, playerDidAction, 0, hasSpecialCard, specialCard, roles

    # print ("-------------")
    # print ("New Roles:" + str([chef,souschef,waiter,dishwasher]))
    # print ("-------------")

    if not chef == 0:
        cardsChef = getPlayerRoleExchangeCards(playersHand[chef], 0)
    if not souschef == 0:
        cardsSousChef  = getPlayerRoleExchangeCards(playersHand[souschef], 1)
    if not waiter == 0:
        cardsWaiter  = getPlayerRoleExchangeCards(playersHand[waiter], 2)
    if not dishwasher == 0:
        cardsDishwasher  = getPlayerRoleExchangeCards(playersHand[dishwasher], 3)

    if chef == 0:
        receivedCard = cardsDishwasher
        receivedFrom = 3
    elif souschef == 0:
        receivedCard = cardsWaiter
        receivedFrom = 2
    elif waiter == 0:
        receivedCard = cardsSousChef
        receivedFrom = 1
    elif dishwasher == 0:
        receivedCard = cardsChef
        receivedFrom = 0
    #
    # print ("-------------")
    # print ("New Roles out Change Roles:" + str(newRoles))
    # print ("-------------")

    return cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher, getScreenCardFromPlayer(receivedCard), playerDidAction, receivedFrom, hasSpecialCard, specialCard, newRoles

def isSpecialCardSelected(playerChosenCards):

    isWrong = False
    error = ""
    isSpecialCardPresent = False
    specialAction = ""

    # print ("playerChosenCards:" + str(playerChosenCards))
    for card in playerChosenCards:
        if "Dinner" in card:
            specialAction = "Dinner"
            isSpecialCardPresent = True
            break
        elif "Fight" in card:
            specialAction = "Fight"
            isSpecialCardPresent = True
            break

    if len(playerChosenCards) > 1 and isSpecialCardPresent:
        isWrong = True
        error = _('error_Card_OnlySpecialAction')

    return  error, isWrong,isSpecialCardPresent, specialAction

def changeRoles(expModel, playerChosenCards, playerRole, allowCheating, cardsChef, cardsSousChef,
                                     cardsWaiter, cardsDishwasher, receivedFrom):
    # dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.loadDataFrame(dataFrame)


    currentAction = getLastEntryDS(expModel)

    playersHand = currentAction.playerHand
    gameNumber = currentAction.gameNumber
    roles = currentAction.roles

    #Check if there is a special card selected

    error,  isWrong, isSpecialCardPresent, specialAction =  isSpecialCardSelected(playerChosenCards)
    if isWrong:
        return error, isWrong, 0, False, "", roles, receivedFrom

    if isSpecialCardPresent:

        # print("---------------------------------")
        # print ("Change roles: " + str(specialAction))
        # print("---------------------------------")

        if specialAction == "Fight":

            declareSpecialActionDS(expModel, 0, playersHand, roles, specialAction, gameNumber)

            return error, isWrong, 0, isSpecialCardPresent, specialAction, roles, 0

        else:

            chef, souschef, waiter, dishwasher = playerRole.index(0), playerRole.index(1), playerRole.index(
                2), playerRole.index(3)
            newChef = dishwasher
            newSouschef = waiter
            newWaiter = souschef
            newDishwasher = chef

            chef, souschef, waiter, dishwasher = newChef, newSouschef, newWaiter, newDishwasher
            newRoles = []

            for playerNumber in range(4):
                newRoles.append([chef, souschef, waiter, dishwasher].index(playerNumber))

            declareSpecialActionDS(expModel, 0, playersHand, newRoles, specialAction, gameNumber)

            return error, isWrong, 0, isSpecialCardPresent, "Fight", newRoles, 0




    #Validate the actions
    error,isWrong,playerChosenCards = validateChangeRolesCard(playerRole[0], playersHand[0],playerChosenCards,allowCheating)
    if isWrong:
        return error, isWrong, 0, isSpecialCardPresent, specialAction, playerRole, receivedFrom

    if playerRole[0] == 0:
        cardsChef = playerChosenCards
    elif playerRole[0] == 1:
        cardsSousChef = playerChosenCards
    elif playerRole[0] == 2:
        cardsWaiter = playerChosenCards
    elif playerRole[0] == 3:
        cardsDishwasher = playerChosenCards

    chef, souschef, waiter, dishwasher = playerRole.index(0), playerRole.index(1), playerRole.index(
        2), playerRole.index(3)


    if  isinstance(cardsWaiter, list):
        cardsWaiter = cardsWaiter[0]

    if isinstance(cardsSousChef, list):
        cardsSousChef = cardsSousChef[0]

    # print ("Chef:" + str(chef))
    # print ("Chef cards:" + str(playersHand[chef]))
    # print ("Chef receives:" + str(cardsDishwasher))
    # print ("Chef gives:" + str(cardsChef))
    # print("Index chef gives cards :" + str(cardsChef))

    # update the dishwasher cards
    for i in range(len(cardsDishwasher)):
      cardIndex = playersHand[dishwasher].index((int(cardsDishwasher[i])))
      playersHand[dishwasher][cardIndex] = cardsChef[i]

    # update the chef cards
    for i in range(len(cardsChef)):
      cardIndex = playersHand[chef].index((int(cardsChef[i])))
      playersHand[chef][cardIndex] = cardsDishwasher[i]

    # update the waiter cards
    cardIndex = playersHand[waiter].index((int(cardsWaiter)))
    playersHand[waiter][cardIndex] = cardsSousChef

    # update the souschef cards
    cardIndex = playersHand[souschef].index((int(cardsSousChef)))
    playersHand[souschef][cardIndex] = cardsWaiter

    # print("Chef cards After:" + str(playersHand[chef]))

    for player in range(len(playersHand)):
       playersHand[player].sort()


    #Redefine starting player
    startingPlayer = numpy.array(range(4))
    random.shuffle(startingPlayer)
    startingPlayer = startingPlayer[0]

    # Create deck
    maxCardNumber = 11

    while not (maxCardNumber in playersHand[startingPlayer]):
      startingPlayer = startingPlayer + 1
      if startingPlayer >= startingPlayer:
        startingPlayer = 0

    newRoles = []

    for playerNumber in range(4):
        newRoles.append([chef, souschef, waiter, dishwasher].index(playerNumber))

    roles = newRoles
    exchangeRolesActionDS(expModel, playersHand, roles, [cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher],
                                   gameNumber)


    return error, False, startingPlayer, False, "", roles , receivedFrom

def doPlayerAction(expModel, player, action, firstAction, currentRound, agentNames, loadedModels, isHuman):

    # print ("isHuman:" + str(isHuman))
    # print ("expName, player, action, firstAction, currentRound, agentNames, dataFrame, loadedModels=[], isHuman=True" + str([expName, player, action, firstAction, currentRound, agentNames, dataFrame, loadedModels, isHuman]))
    # dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expModel
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.loadDataFrame(dataFrame)

    currentAction = getLastEntryDS(expModel)

    # currentDataset = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.dataFrame = currentDataset
    #
    # currentAction = currentDataset.iloc[-1]

    gameNumber = currentAction.gameNumber
    playersHand = currentAction.playerHand
    board = currentAction.board
    score = currentAction.scores
    roles = currentAction.roles
    rounds = currentAction.roundNumber
    playerStatus = currentAction.playerStatus

    if str(rounds) == "":
        rounds = 0
    else:
        rounds = int(rounds)

    print ("new round:" + str(rounds))
    #
    # input("here")
    # print ("Game Number:" + str(gameNumber))
    # print("playersHand:" + str(playersHand))
    # print("board:" + str(board))
    # print("score:" + str(score))
    # print("roles:" + str(roles))
    # print("rounds:" + str(rounds))
    # print("playerStatus:" + str(playerStatus))
    # playerStatus = numpy.copy(playerStatus).tolist()
    # board = numpy.copy(board)
    # playersHand = numpy.copy(playersHand)
    playerHand = playersHand[player]
    # print("playerHand:" + str(playerHand))
    # input("here")

    if len(board) == 0:
        board = restartBoard()

    newRound = copy.copy(currentRound)

    import sys
    # print("Inside Do Action Round:" + str(newRound), file=sys.stderr)

    #
    if len(playerStatus) == 0:
        playerStatus = []
        for a in range(4):
            playerStatus.append("")

    possibleActions, currentHighLevelActions, highLevelActions = getPossibleActions(currentAction, player, firstAction)

    if isHuman:
        if player == 0:
          action, error = validatePlayerAction(action, currentHighLevelActions)
          if not error =="":
              return False, False, player, newRound, -1, False, error, score, []


        # print("Highlevel action:" + str(highLevelActions))
        # print("Actions:" + str(action))
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

        action = doAgentAction(possibleActions, stateVector, agentNames[player], loadedModels)
        actionIndex = numpy.argmax(action)
        # print("Agent did action:" + str(actionIndex))
        # print (" --- selected action:" + str(actionIndex))

        # import sys
        # print("---------", file=sys.stderr)
        # print("Player:" + str(player), file=sys.stderr)
        # print("action:" + str(action), file=sys.stderr)
        # print("actionIndex:" + str(actionIndex), file=sys.stderr)

    loss = []
    totalActions = 1

    # print("Check pass action")
    #Pass action:
    if actionIndex == 199:
        reward = -0.01
        actionComplete = actionPass + str("_[0]")
        cardsDiscarded = []
    else:
        cardsDiscarded, board, playerHand = discardCards(playerHand,action, highLevelActions)
        reward = -0.01
        actionComplete = actionDiscard +"_"+str(cardsDiscarded)

    # print("Check all cards")
    if numpy.array(playerHand).sum() == 0: # If all the cards of the player hands are gone, he wins the match, maximum reward

            # score = score.tolist()
            if not player in score:
                score.append(player)

            index = score.index(player)
            if index == 0:
                reward = 1
            else:
                reward = -0.1

            actionComplete = actionFinish+"_"+str(cardsDiscarded)

    playersHand[player] = playerHand
    playerHand = playerHand

    hasPlayerFinished = numpy.array(playerHand).sum() == 0

    if settings.ALLOW_AUTOMATIC_SIMULATION:
        """Simulate player 1 finishing in the first round """
        #
        import sys
        # print("rounds:" + str(rounds), file=sys.stderr)
        if rounds == "":
            rounds = 0
            # print("Changing rounds to zero:" + str(rounds), file=sys.stderr)
        if player == 0:
            actionComplete = actionFinish + "_" +str(cardsDiscarded)
            # score = score.tolist()
            if not player in score:
                score.append(player)

            index = score.index(player)
            if index == 0:
                reward = 1
            else:
                reward = -0.1
            hasPlayerFinished = True
            playersHand[player] = numpy.zeros(17).tolist()



    """Simulate player 1 finishing in the first round """


    if len(playerStatus) <= player:
        playerStatus.append(actionComplete)
    else:
        playerStatus[player] = actionComplete
    # import sys
    # print("--------- INSIDE DO ACTION ---------", file=sys.stderr)
    # print("rounds:" + str(rounds), file=sys.stderr)
    # print("currentRound:" + str(currentRound), file=sys.stderr)
    # print("Agent:" + str(player), file=sys.stderr)
    # print("Action:" + str(actionComplete), file=sys.stderr)
    # print("PLayer Hand:" + str(playersHand[player]), file=sys.stderr)
    # print("Board:" + str(board), file=sys.stderr)
    # print("Check if save")
    if not(actionFinish in actionComplete == actionFinish and rounds > currentRound):
        # print("---SAVING THE DATAFRAME---:" + str(board), file=sys.stderr)
        # print("player: " + str(player), file=sys.stderr)
        # print("board: " + str(board), file=sys.stderr)
        # print("actionComplete: " + str(actionComplete[0]), file=sys.stderr)

        doActionActionDS(expModel, gameNumber, player, newRound,
                                                        actionComplete, board,
                                                        0, reward,
                                                        playersHand, roles,
                                                        score, playerStatus,
                                                        action, loss, totalActions, possibleActions)

        # currentAction = dsManager.dataFrame.tail(1)
        # print("---Loading the data frame---:" + str(board), file=sys.stderr)
        # print("player: " + str(currentAction["Player"].tolist()[0]), file=sys.stderr)
        # print("board: " + str(currentAction["Board"].tolist()[0]), file=sys.stderr)
        # print("action: " + str(currentAction["Action Type"].tolist()[0]), file=sys.stderr)


    # dsManager.saveFile()

    # print("Check game finished")
    gameFinished = hasGameFinished(playersHand)

    nextPlayer = player + 1
    if nextPlayer == 4:
        nextPlayer = 0

    lastPlayer = -1
    pizza = False

    # print("if not game finished")
    if not gameFinished:
        if len(playerStatus) == 4 and len(playerStatus[nextPlayer]) > 0:
                for np in range(4):
                    if actionFinish in playerStatus[nextPlayer] == actionFinish or actionPass in playerStatus[nextPlayer]:
                        nextPlayer = nextPlayer + 1
                        if nextPlayer == 4:
                            nextPlayer = 0

                # while playerStatus[nextPlayer][0] == actionFinish:
                #     nextPlayer = nextPlayer + 1
                #     if nextPlayer == 4:
                #         nextPlayer = 0

        playerFinishedCounter = 0
        lastPlayer = player

        for indexStatus, status in enumerate(playerStatus):

            if len(status) > 0 and not status =="":
                if actionDiscard in status:
                    playerFinishedCounter += 1
                    lastPlayer = indexStatus
            else:
                playerFinishedCounter += 2

        if playerFinishedCounter <= 1:
            pizza = True
        # print ("Player finished counter:" + str(playerFinishedCounter))
        # print("Pizza:" + str(pizza))
    error = ""

    # currentAction = dsManager.dataFrame.tail(1)
    # print("---Loading the data frame---:", file=sys.stderr)
    # print("score: " + str(currentAction["Scores"].tolist()[0]), file=sys.stderr)
    # print("---Loading the data frame---:", file=sys.stderr)

    # dataFrameSaved = dsManager.getDataFrame()

    # print("---Loading the data frame---:" + str(board), file=sys.stderr)
    # print("Rounds after loading: " + str(currentAction["Round Number"].tolist()[0]), file=sys.stderr)

    # print("Exiting Do Action Round:" + str(newRound), file=sys.stderr)


    if actionIndex == 199:
        cardsDiscarded = ["pass"]
    # print("ENd1!")
    # Q.put([ gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score, cardsDiscarded, dataFrameSaved])
    # print("ENd2!")
    return gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score, cardsDiscarded

def doPizza(expModel, currentRound):

    # dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.loadDataFrame(dataFrame)

    # currentDataset = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.dataFrame = currentDataset

    currentAction = getLastEntryDS(expModel)

    gameNumber = currentAction.gameNumber
    playersHand = currentAction.playerHand
    score = currentAction.scores
    roles = currentAction.roles
    rounds = currentAction.roundNumber
    playerStatus = currentAction.playerStatus


    board = restartBoard()
    for a in range(len(playerStatus)):
        if not actionFinish in playerStatus[a]:
            playerStatus[a] = ""

    # print ("Player hand pizza:" + str(playersHand))
    # input("here")
    doActionPizzaReadyDS(expModel, rounds, board, playersHand, roles, score, playerStatus, gameNumber)
    # dsManager.saveFile()

    if currentRound == int(rounds):
        currentRound += 1

    return currentRound


def hasGameFinished(playersHand):

  for i in range(len(playersHand)):
      # print("-----------", file=sys.stderr)
      # print("playersHand[i]:" + str(playersHand[i]), file=sys.stderr)
      # print("numpy.array(playersHand[i]).sum():" + str(numpy.array(playersHand[i]).sum()), file=sys.stderr)
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

  playerHand = playerHand

  cardsToDiscard = []
  actionIndex = numpy.argmax(action)
  takenAction = highLevelActions[actionIndex].split(";")
  cardValue = int(takenAction[0][1:])
  cardQuantity = int(takenAction[1][1:])
  jokerQuantity = int(takenAction[2][1:])
  # print ("------------")
  # print ("Action:"+ str(action))
  # print ("ActionIndex:" + str(actionIndex))
  # print("takenAction:" + str(takenAction))
  # print("cardValue:" + str(cardValue))
  # print("cardQuantity:" + str(cardQuantity))
  # print("jokerQuantity:" + str(jokerQuantity))

  for q in range(cardQuantity):
      cardsToDiscard.append(cardValue)
  for j in range(jokerQuantity):
      cardsToDiscard.append(12)

  board = restartBoard()

  originalCardDiscarded = cardsToDiscard.copy()

  # print ("Original cards to discard:" + str(originalCardDiscarded))
  # print ("------------")
  # input("gere")
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


def doAgentAction(possibleActions, state, agent, loadedModels):

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


    """ Changes for the IVA Experiments with fixed agents: Random, DQL, PPO"""

    import sys
    # print("---------", file=sys.stderr)
    # print("Agent name:" + str(agent), file=sys.stderr)

    # if agent == "Avery":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_DQL.hd5"
    #     # print("LOADED DQL!", file=sys.stderr)
    # elif agent == "Cass":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_PPO.hd5"
    #     # print("LOADED PPO!", file=sys.stderr)
    # elif agent == "Beck":
    #     # print("LOADED RANDOM!", file=sys.stderr)
    #     return doRandomAction(possibleActions)

    # import time
    # time.sleep(3)

    # return doRandomAction(possibleActions)


    loadedPosition = 0
    if agent == "Avery":
        loadedPosition = 0
        # doRandomAction(possibleActions)
        modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_DQL.hd5"
        # print("LOADED DQL!", file=sys.stderr)
    elif agent == "Cass":
        loadedPosition = 1
        modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_PPO.hd5"
        # print("LOADED PPO!", file=sys.stderr)
    elif agent == "Beck":
        # print("LOADED RANDOM!", file=sys.stderr)
        return doRandomAction(possibleActions)


    """ Original one"""
    # agentName = agent.split("_")[0]
    # if agentName == "DQL":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_DQL.hd5"
    # elif agentName == "A2C":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_A2C.hd5"
    # elif agentName == "PPO":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL+"/trainedModels/actor_PPO.hd5"
    # elif agentName == "DJ":
    #     modelDirectory = settings.BASE_DIR + settings.STATIC_URL + "/trainedModels/actor_DJ.hd5"
    # elif agentName == "Random":
    #     return doRandomAction(possibleActions)
    # print("---------", file=sys.stderr)
    # print("Agent:" + str(agent), file=sys.stderr)
    # print("Model Directory:" + str(modelDirectory), file=sys.stderr)

    # print ("-------")
    # print("Actor: " + str(agent))
    # print ("Possible actions" + str(possibleActions))
    # print ("State:" + str(state))

    if len(loadedModels) == 0:
        clear_session()
        actor = load_model(modelDirectory, custom_objects={'loss':loss})
    else:
        actor = loadedModels[loadedPosition]

    stateVector = numpy.expand_dims(numpy.array(state), 0)

    # print(" --- Preparing action:")

    possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions), 0)


    a = actor.predict([stateVector, possibleActionsVector])[0]
    action = numpy.argmax(a)
    takenAction= doRandomAction(possibleActions)


    gc.collect()
    del actor

    # print (" --- Action:" + str(action))
    # return takenAction

    # print ("Action:" + str(a))
    # print("Action Number:" + str(action))
    # print ("Possible action[action]: " + str(possibleActions[action]))
    # print("Random Action Number:" + str(numpy.argmax(takenAction)))
    # print("Possible action[random]: " + str(possibleActions[numpy.argmax(takenAction)]))
    # print ("-------")
    # input("Enter for next...")

    if possibleActions[action] == 0:
        # print ("return taken action:" + str(takenAction))
        return takenAction

    # print ("Possible Actions:" + str(possibleActions))
    # print("Avatar:" + str(agent) + " - Action:" + str(action) + " -  Allowed:" + str(possibleActions[action] == 0) + " - Random Action:" + str(numpy.argmax(takenAction)) + " - Random allowed: "+str(possibleActions[numpy.argmax(takenAction)] == 0), file=sys.stderr)

    # if numpy.array(possibleActions).sum() == 1:
    #     a = numpy.zeros(200)
    #     a[199]=1

    # import sys
    # print("---------", file=sys.stderr)
    # print("Agent:" + str(agent), file=sys.stderr)
    # print ("possibleActions2:" + str(possibleActionsVector), file=sys.stderr )
    # print ("stateVector:" + str(stateVector), file=sys.stderr )
    # print("a:" + str(a), file=sys.stderr)
    # print("len(a):" + str(len(a)), file=sys.stderr)

    # print("return a:" + str(a))
    return a

def doRandomAction(possibleActions):

    possibleActions = numpy.copy(possibleActions)

    possibleActions = possibleActions
    # print ("--- Possible actions: " + str(possibleActions))

    itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()
    random.shuffle(itemindex)
    aIndex = itemindex[0]
    a = numpy.zeros(200)
    a[aIndex] = 1
    # print ("--- Doing random action")

    return a

def getPossibleActions(currentAction, player, firstAction):

    # dataSetDirectory = settings.BASE_DIR + settings.STATIC_URL + expName
    # dsManager = DataSetManager(dataSetDirectory=dataSetDirectory)
    # dsManager._currentDataSetFile = dataSetDirectory + "/Dataset.pkl"
    # dsManager.loadDataFrame(dataFrame)
    # #
    # # readFile = pd.read_pickle(dataSetDirectory + "/Dataset.pkl")
    #
    # currentAction = dsManager.dataFrame.tail(1)

    # import sys
    # print("---------", file=sys.stderr)
    # print("Starting New game :" + str(currentAction["Player Hand"].tolist()), file=sys.stderr)

    playerHand = currentAction.playerHand[player]
    board = currentAction.board
    actionType = currentAction.actionType
    playerStatus = currentAction.playerStatus

    highLevelActions = []
    possibleActions = []


    # import sys
    # print("---------------------", file=sys.stderr)
    # print("Player:" + str(player), file=sys.stderr)
    # print("Player Hand:" + str(playerHand), file=sys.stderr)
    # print("Board:" + str(board), file=sys.stderr)
    # print ("First action:" + str(firstAction), file=sys.stderr )

    if actionType == actionDeal or actionType==actionChangeRole or actionType== actionSpecialAction:
        board = numpy.zeros(11)
        board[0] = 13

    if not actionType == "":

        maxCardNumber = 11

        unique, counts = numpy.unique(board, return_counts=True)
        currentBoard = dict(zip(unique, counts))

        unique, counts = numpy.unique(playerHand, return_counts=True)
        currentPlayerHand = dict(zip(unique, counts))

        highestCardOnBoard = 13
        for boardItem in currentBoard:
            if not boardItem == maxCardNumber + 1:
                highestCardOnBoard = boardItem

        jokerQuantityBoard = 0

        if maxCardNumber + 1 in board:
            jokerQuantityBoard = currentBoard[maxCardNumber + 1]

        if maxCardNumber + 1 in currentPlayerHand.keys():
            jokerQuantity = currentPlayerHand[maxCardNumber + 1]
        else:
            jokerQuantity = 0
        #
        # print("Possible actions:", possibleActions)
        # print("current Board:", currentBoard)
        # print("current playerHand:", currentPlayerHand)
        # print("highestCardOnBoard:", highestCardOnBoard)
        # print("jokerQuantityBoard:", jokerQuantityBoard)

        cardDescription = ""
        for cardNumber in range(maxCardNumber):
            for cardQuantity in range(cardNumber + 1):
                isThisCombinationAllowed = 0
                isthisCombinationOneJokerAllowed = 0
                isthisCombinationtwoJokersAllowed = 0

                # print ("Card:" + str(cardNumber+1) + " Quantity:" + str(cardQuantity+1))

                """If this card number is in my hands and the amount of cards in my hands is this amount"""
                if (cardNumber+1) in playerHand and currentPlayerHand[cardNumber+1] >= cardQuantity+1:
                    # print ("-- this combination exists in my hand!")

                    """Check combination without the joker"""
                    """Check if this combination of card and quantity can be discarded given teh cards on the board"""
                    """Check if this cardnumber is smaller than the cards on the board"""
                    """ and check if the cardquantity is equal of higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                    if (cardNumber+1 < highestCardOnBoard) and (cardQuantity+1 >= currentBoard[highestCardOnBoard] +jokerQuantityBoard):

                        """Check if this is the first move"""
                        """If it is the first move, onle 11s are allowed"""
                        if firstAction:
                            if cardNumber+1 == maxCardNumber:
                                isThisCombinationAllowed = 1
                                # print("--- this combination can be put down on the board because it is first action!")
                        else:
                            """If it is not first move, anything on this combination is allowed!"""
                            # print("--- this combination can be put down on the board because and it is not first action!")
                            isThisCombinationAllowed = 1

                    """Check combination with the joker"""

                    if jokerQuantity > 0:

                        """Check for 1 joker at hand"""
                        """Check if this combination of card and quantity + joker can be discarded given the cards on the board"""
                        """Check if this cardnumber is smaller than the cards on the board"""
                        """ and check if the cardquantity + 1 joker is equal or higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                        if (cardNumber + 1 < highestCardOnBoard) and (
                                (cardQuantity + 1 + 1)>= currentBoard[highestCardOnBoard] + jokerQuantityBoard):
                                """Check if this is the first move"""
                                """If it is the first move, onle 11s are allowed"""
                                if firstAction:
                                    if cardNumber + 1 == maxCardNumber:
                                        # print(
                                        #     "--- this combination can be put down on the board because and it is first action and joker!")
                                        isthisCombinationOneJokerAllowed = 1
                                else:
                                    """If it is not first move, anything on this combination is allowed!"""
                                    # print(
                                    #     "--- this combination can be put down on the board because and it is not first action and joker!")
                                    isthisCombinationOneJokerAllowed = 1


                        if jokerQuantity > 1:
                            """Check for 2 jokers at hand"""
                            """Check if this combination of card and quantity + joker can be discarded given the cards on the board"""
                            """Check if this cardnumber is smaller than the cards on the board"""
                            """ and check if the cardquantity + 2 joker is equal or higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                            if (cardNumber + 1 < highestCardOnBoard) and (
                                    (cardQuantity + 1 + 2) >= currentBoard[highestCardOnBoard] + jokerQuantityBoard):
                                """Check if this is the first move"""
                                """If it is the first move, onle 11s are allowed"""
                                if firstAction:
                                    if cardNumber + 1 == maxCardNumber:
                                        # print(
                                        #     "--- this combination can be put down on the board because and it is first action and 2 jokers!")
                                        isthisCombinationtwoJokersAllowed = 1

                                else:
                                    """If it is not first move, anything on this combination is allowed!"""
                                    # print(
                                    #     "--- this combination can be put down on the board because and it is not first action and 2 jokers!")
                                    isthisCombinationtwoJokersAllowed = 2

                possibleActions.append(isThisCombinationAllowed)
                possibleActions.append(isthisCombinationOneJokerAllowed)
                possibleActions.append(isthisCombinationtwoJokersAllowed)

                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2")

        canDiscardOnlyJoker = 0
        highLevelActions.append("C0;Q0;J1")
        if maxCardNumber + 1 in playerHand:  # there is a joker in the hand
            if not firstAction:
                if highestCardOnBoard == maxCardNumber + 2:
                    canDiscardOnlyJoker = 1

        possibleActions.append(canDiscardOnlyJoker)

        #
        # if maxCardNumber + 1 in playerHand:  # there is a joker in the hand
        #     if firstAction:
        #         possibleActions.append(0)
        #     else:
        #         if highestCardOnBoard == maxCardNumber + 2:
        #             possibleActions.append(1)  # I can discard the joker
        #
        #         else:
        #             possibleActions.append(0)  # I cannot discard the joker
        #
        # else:
        #     possibleActions.append(0)  # I can not discard one joker
        #


        if firstAction:
            possibleActions.append(0)
        else:
            possibleActions.append(1)  # the pass action, which is always a valid action when not first action


        highLevelActions.append("pass")

        highLevelActions = highLevelActions

    # print("Possible actions with joker:", possibleActions)
    # print("Possible hl actions with joker:", highLevelActions)
    # print("Possible actions with joker:", len(possibleActions))
    # print("Possible hl actions with joker:", len(highLevelActions))

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


    if len(playerStatus) > 0 and len(playerStatus[player]) > 0 and actionPass in playerStatus[player]:
        currentlyAllowedActions = []
        possibleActions = numpy.zeros(200)
        possibleActions[199] = 1
        currentlyAllowedActions.append("pass")

        return possibleActions, currentlyAllowedActions, highLevelActions

    return possibleActions, currentlyAllowedActions[0], highLevelActions

