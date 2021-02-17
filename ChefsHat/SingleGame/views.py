from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# from .models import User, Game, Actions

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from SingleGame.GameController.ChefsHatOnlineController import exportDB, getExperimentByName, getPerformanceScore, savePerformanceScore, dealCards, newGame, getPossibleActions, doPlayerAction, doPizza, simulateActions, createNewExperiment, changeRoles, changeRolesOthers
from SingleGame.GameController.ChefsHatOnlineRenderer import renderCurrentDataset

from django.utils.translation import gettext

from django.utils import translation
from django.utils.translation import ugettext as _

import numpy

import random

# Create your views here.

def createDB(request):
    exportDB()
    response = render(request, 'SingleGame/dbCreated.html')
    return response

def getRuleBook(request):
    language = request.session.get('CHLang', False)["lang"]
    translation.activate(translation.get_language())

    ruleBookPage1 =_('ruleBook_page1Link')
    ruleBooKPage2 = _('ruleBook_page2Link')
    context = {'page1': ruleBookPage1, 'page2': ruleBooKPage2}

    response = render(request, 'SingleGame/ruleBook.html', context)
    return response

def getPerformanceScoreRank(request):


    scores = getPerformanceScore()
    context = {"scores": scores}

    response = render(request, 'SingleGame/performanceRank.html', context)

    return response


def continueDisclaimer(request):
    language = request.session.get('CHLang', False)["lang"]

    print ("Language:" + str(language))
    translation.activate(language)
    response = render(request, 'SingleGame/disclaimer.html')

    return response

def startExperiment(request):
    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    response = render(request, 'SingleGame/startExperiment.html')

    return response

def changeLanguage(request, language):
    session = {'lang': language}

    request.session['CHLang'] = session


    translation.activate(language)
    settings.LANGUAGE_CODE = language
    videoLink = _('video_link')
    context = {'videoLink': videoLink}

    response = render(request, 'SingleGame/disclaimerVideo.html', context)

    print ("Settings langauge code:" + str(settings.LANGUAGE_CODE))

    return response

def webGL(request):
    return render(request,'SingleGame/webglatasetronic.html')

def finishGame(request):

    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    performanceScore = request.session.get('CHGameDirectory', False)["performanceScore"]
    agentNames = request.session.get('CHGameDirectory', False)["playerNames"]

    context = {"performanceScore": performanceScore[0]}

    # saveDataset(dataFrame,expName)
    savePerformanceScore(performanceScore[0],agentNames[0])

    return render(request, 'SingleGame/gameFinished.html', context)

def index(request):

    return render(request, 'SingleGame/index.html')

def startGame(request):

    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    print("---------------------------------")
    print("!!!!START GAME Request!!!!")
    print("---------------------------------")
    expName = request.session.get('CHGameDirectory', None)["directory"]
    agentNames = request.session.get('CHGameDirectory', False)["playerNames"]
    pointsScore = request.session.get('CHGameDirectory', False)["pointsScore"]
    currentGame = request.session.get('CHGameDirectory', False)["currentGame"]
    gameStyle = request.session.get('CHGameDirectory', False)["gameStyle"]
    avatars = request.session.get('CHGameDirectory', False)["avatars"]
    playerRole = request.session.get('CHGameDirectory', False)["playerRole"]
    startingPlayer = request.session.get('CHGameDirectory', False)["startingPlayer"]
    humanScore = request.session.get('CHGameDirectory', False)["humanScore"]
    cardsChef = request.session.get('CHGameDirectory', False)["cardsChef"]
    cardsSousChef = request.session.get('CHGameDirectory', False)["cardsSousChef"]
    cardsWaiter = request.session.get('CHGameDirectory', False)["cardsWaiter"]
    cardsDishwasher = request.session.get('CHGameDirectory', False)["cardsDishwasher"]
    receivedCard = request.session.get('CHGameDirectory', False)["receivedCard"]
    receivedFrom = request.session.get('CHGameDirectory', False)["receivedFrom"]
    specialActionUsed = request.session.get('CHGameDirectory', False)["specialActionUsed"]
    trialGame = request.session.get('CHGameDirectory', False)["trialGame"]
    performanceScore = request.session.get('CHGameDirectory', False)["performanceScore"]

    playerHasToChoose = request.POST.get('playerHasToChoose', False);
    action = request.POST.getlist('selectedAction', [])

    #If there are cards selected, it means there is a card exchange happening:

    expModel = getExperimentByName(expName)
    if playerHasToChoose == "1":

        error, iswrong, startingPlayer, hasSpecialCard, specialCard, newRole, receivedFrom = changeRoles(expModel, action, playerRole, settings.ALLOW_CHEATING_CARD_EXCHANGE, cardsChef, cardsSousChef,
                                     cardsWaiter, cardsDishwasher, receivedFrom)

        # Create the received cards
        receivedCardsIndex = range(len(receivedCard))

        receivedCardContext = zip(receivedCardsIndex, receivedCard)

        rolesList = ["CHEF", "SOUSCHEF", "WAITER", "DISHWASHER"]
        thisPlayerRole = rolesList[newRole[0]]

        PHRASES = {"CHEF": gettext('ChefMessage'),
                   "SOUSCHEF": gettext('SousChefMessage'),
                   "WAITER": gettext('WaiterMessage'),
                   "DISHWASHER": gettext('DishwasherMessage')
                   }

        phraseRole = PHRASES[thisPlayerRole]

        thisPlayerPreviousRole = rolesList[playerRole[0]]


        if iswrong:
            # Obtain PLayer0 Cards
            player0Cards, _, _, _ = renderCurrentDataset(expModel, drawBoard=False,
                                                         withSpecialCards=not(specialActionUsed))

            # Create the possible actions
            player0CardsIndex = range(len(player0Cards))
            player0Cards = zip(player0CardsIndex, player0Cards)

            translatedRoleNames = [gettext('Chef'), gettext('SousChef'), gettext('Waiter'), gettext('Dishwasher')]

            # receivedFrom = int(receivedFrom)
            # receivedFrom = str(translatedRoleNames[receivedFrom]) + " (" + str(
            #     agentNames[playerRole.index(receivedFrom)]) + ")"

            context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
                       "humanScore": humanScore, "gameOver":False, "firstRound":False, "playerHasARole": True, "thisPlayerRole": thisPlayerRole, "player0Cards":player0Cards, "phraseRole":phraseRole,
                       "error":iswrong, "errorMessage":error, "receivedCard":receivedCardContext, "receivedFrom":receivedFrom, "dinnerServed":False,
                       "foodFight": False,
                       "thisPlayerPreviousRole": "",
                       "trialGame": False
                       }

            return render(request, 'SingleGame/startNewGame.html', context)

        dinnerServed = False
        foodFight = False


        if hasSpecialCard:
            specialActionUsed = True

            if specialCard == "Dinner":
                dinnerServed = True
            if specialCard == "Fight":

                cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher, receivedCard, playerDidAction, receivedFrom, hasSpecialCard, specialCard, newRoles = \
                    changeRolesOthers(
                    expModel, newRole)


                nextPlayer = request.session.get('CHGameDirectory', False)["playerTurn"]
                firstAction = request.session.get('CHGameDirectory', False)["firstAction"]
                newRound = request.session.get('CHGameDirectory', False)["currentRound"]
                avatarRoles = request.session.get('CHGameDirectory', False)["avatarRoles"]
                lastPlayer = request.session.get('CHGameDirectory', False)["lastPlayer"]


                session = { 'directory': expName, "playerTurn": nextPlayer, "playerNames": agentNames,
                           "pointsScore": pointsScore,
                           "currentGame": currentGame, "firstAction": firstAction, "currentRound": newRound,
                           "lastPlayer": lastPlayer, "gameStyle": gameStyle,
                           "avatars": avatars, "playerRole": newRoles, "avatarRoles": avatarRoles,
                           "nextPlayer": nextPlayer,
                           "startingPlayer": startingPlayer, "humanScore": humanScore, "cardsChef": cardsChef,
                           "cardsSousChef": cardsSousChef, "cardsWaiter": cardsWaiter,
                           "cardsDishwasher": cardsDishwasher, "receivedCard": receivedCard,
                           "receivedFrom": receivedFrom,
                           "specialActionUsed":specialActionUsed,
                           "trialGame":trialGame,
                           "performanceScore":performanceScore}

                request.session['CHGameDirectory'] = session

                foodFight = True

            translatedRoleNames = [gettext('Chef'), gettext('SousChef'), gettext('Waiter'), gettext('Dishwasher')]

            playerDidAction = str(translatedRoleNames[playerDidAction]) + " (" + str(
                agentNames[playerRole.index(playerDidAction)]) + ")"

            receivedFrom = str(translatedRoleNames[receivedFrom]) + " (" + str(
                agentNames[newRoles.index(receivedFrom)]) + ")"

            # Obtain PLayer0 Cards
            player0Cards, _, _, _ = renderCurrentDataset(expModel, drawBoard=False,
                                                         withSpecialCards=not(specialActionUsed))

            # Create the possible actions
            player0CardsIndex = range(len(player0Cards))
            player0Cards = zip(player0CardsIndex, player0Cards)

            # Create the received cards
            receivedCardsIndex = range(len(receivedCard))

            receivedCardContext = zip(receivedCardsIndex, receivedCard)

            print("New Role" + str(newRoles))

            context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
                       "humanScore": humanScore, "gameOver":False, "firstRound":False, "playerHasARole": True, "thisPlayerRole": thisPlayerRole, "player0Cards":player0Cards, "phraseRole":phraseRole,
                       "error":iswrong, "errorMessage":error, "receivedCard":receivedCardContext, "receivedFrom":receivedFrom, "dinnerServed":dinnerServed,
                       "foodFight": foodFight,
                       "thisPlayerPreviousRole": thisPlayerPreviousRole, "playerActiveAction":playerDidAction,
                       "trialGame":False
                       }

            return render(request, 'SingleGame/startNewGame.html', context)


    #Get possible actions
    player1AllowedActions = []
    playerAction = False
    if startingPlayer == 0:
        # possibleActions, player1AllowedActions, highLevelActions = getPossibleActions(expName=expName, player=startingPlayer,
        #                                                                              firstAction=True, dataFrame=dataFrame)
        playerAction = True

    #Gamestate
    gameRound = 0
    playerTurn = int(startingPlayer)
    oponentsAction = not playerTurn == 0

    # Render dataset
    player0Cards, player1Cards, player2Cards, player3Cards = renderCurrentDataset(expModel)
    player1Cards = range(len(player1Cards))
    player2Cards = range(len(player2Cards))
    player3Cards = range(len(player3Cards))
    player0CardsLength = len(player0Cards)


    #Create the possible actions
    player0CardsIndex = range(len(player0Cards))

    player0Cards = zip(player0CardsIndex, player0Cards)

    #AvatarRoles
    avatarRoles = []
    avatarDirectories = ["symbolChef.png", "symbolSChef.png","symbolWait.png","symbolDish.png"]
    if len(playerRole) > 0:
        for pIndex in playerRole:
            avatarRoles.append("/static/images/"+avatarDirectories[pIndex])


    hasAvatarRole = len(avatarRoles)>0
    #Update session
    session = {'directory': expName, "playerTurn":playerTurn, "playerNames": agentNames, "pointsScore": pointsScore,
               "currentGame": currentGame, "firstAction":True, "currentRound": gameRound, "lastPlayer":0, "gameStyle":gameStyle,
               "avatars": avatars, "playerRole": playerRole, "avatarRoles":avatarRoles, "nextPlayer":0, "simulateNextActions":False,
               "trialGame":trialGame,
               "performanceScore":performanceScore, "finishedRound":[0,0,0,0]}

    request.session['CHGameDirectory'] = session

    context = {'expDirectory': expName, "playerNames": agentNames, "currentRound":gameRound,
               "playerTurn":playerTurn, "playerTurnName":"Player "+str(playerTurn+1)+"-"+agentNames[playerTurn],
                "currentGame":currentGame, "pointsScore": pointsScore, "oponentsAction":oponentsAction,
               "playerAction" : playerAction, "player1Cards":player1Cards, "player2Cards":player2Cards,
               "player3Cards":player3Cards, "player0Cards":player0Cards, "ErrorMessage":"", "hasErrorMessage":False,
               "avatars":avatars, "hasAvatarRole":hasAvatarRole, "avatarRoles":avatarRoles, "player0CardsLength": player0CardsLength,
               "actionDone": False, "actionSelected":[]}

    return render(request, 'SingleGame/game.html', context)

def selectAdversaries(request):

    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    nickname = request.POST.get('userName', 'RandomPlayer')

    DQL = 'DQL'
    PPO = 'PPO'
    A2C = 'A2C'
    AIRL = 'AIRL'
    Random = "RANDOM"

    oponentChoices = [DQL, PPO, A2C, AIRL, Random ]
    context = {'nickname': nickname, "oponentChoices": oponentChoices}

    # Update session
    session = {'directory': "", "playerTurn": "", "playerNames": "", "pointsScore": "",
               "currentGame": "", "firstAction": "", "currentRound": "", "lastPlayer": 0,
               "gameStyle": ""}

    request.session['CHGameDirectory'] = session
    request.session['CHGameDirectory'] = session
    request.session['CHNickname'] = nickname

    return render(request, 'SingleGame/selectAdversaries.html', context)

def startNewExperiment(request):

    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    nickname = request.session.get('CHNickname', None)

    avatars = []

    """ Changes for the IVA Experiments with fixed agents: Random, DQL, PPO"""
    op1 = "Random"
    op2 = "PPO"
    op3 = "DQL"
    gameStyle = "15Points"

    avatarTypes = ["Avery", "Beck", "Cass"]
    rangePosition = list(range(3))
    random.shuffle(rangePosition)

    rangeIndex = list(range(3))
    random.shuffle(rangeIndex)

    agentNames =  [nickname, avatarTypes[rangeIndex[0]], avatarTypes[rangeIndex[1]], avatarTypes[rangeIndex[2]]]

    avatars.append("/static/images/playerAgent.png")
    avatars.append("/static/images/playerAgent.png")
    avatars.append("/static/images/playerAgent.png")
    avatars.append("/static/images/playerAgent.png")

    """ Original one"""
    # op1 = request.POST.get('oponent1', False)
    # op2 = request.POST.get('oponent2', False)
    # op3 = request.POST.get('oponent3', False)
    # gameStyle = request.POST.get('gameStyle', False)
    # agentNames =  [user.name, op1+"_1", op2+"_2", op3+"_3"]
    # for a in [op1, op2, op3]:
    #     if a == "Random":
    #         avatars.append("/static/images/randomAgent.png")
    #     elif a == "A2C":
    #         avatars.append("/static/images/A2CAgent.png")
    #     elif a == "PPO":
    #          avatars.append("/static/images/PPOAgent.png")
    #     elif a == "DQL":
    #         avatars.append("/static/images/DQLAgent.png")
    #     elif a == "DJ":
    #         avatars.append("/static/images/DJAgent.png")

    currentGame = -1

    expName, expModel = createNewExperiment(agentNames, gameStyle, translation.get_language())

    # Start New Game
    newGame(expModel, agentNames, currentGame, [], [0,0,0,0])

    # deal cards
    startingPlayer = dealCards(expModel, currentGame)

    points = [0,0,0,0]
    humanScore = []
    if gameStyle == "Single":
        humanScore = [0, 0, 0, 0]
    else:
            for a in range(4):
               humanScore.append("0/9")

    playerRoles = []
    playerHasARole = False
    thisPlayerRole = ""

    performanceScore = [0,0,0,0]
    trialGame = True
    context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
               "humanScore": humanScore, "gameOver":False, "firstRound":True, "playerHasARole":playerHasARole,"thisPlayerRole":thisPlayerRole, "player0Cards":[],
               "dinnerServed":False,
               "foodFight": False,
               "thisPlayerPreviousRole": "",
               "trialGame": True
               }

    session = {"directory": expName, "playerTurn": "", "playerNames": agentNames, "pointsScore": points,
               "currentGame": currentGame, "firstAction": "", "currentRound": "",
               "lastPlayer": "", "gameStyle": gameStyle, "avatars":avatars, "playerRole":playerRoles, "simulateNextActions":False,
               "startingPlayer":startingPlayer, "humanScore":[0,0,0,0],
               "cardsChef":[], "cardsSousChef":[], "cardsWaiter":[], "cardsDishwasher":[], "receivedCard":[], "receivedFrom": "",
               "specialActionUsed":False, "trialGame":trialGame, "performanceScore":performanceScore}

    request.session['CHGameDirectory'] = session

    return render(request, 'SingleGame/startNewGame.html', context)


def doAction(request):

    print("---------------------------------")
    print("!!!!Another Request!!!!")
    print("---------------------------------")

    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    expName = request.session.get('CHGameDirectory', None)["directory"]
    firstAction = request.session.get('CHGameDirectory', False)["firstAction"]
    agentNames = request.session.get('CHGameDirectory', False)["playerNames"]
    pointsScore = request.session.get('CHGameDirectory', False)["pointsScore"]
    currentGame = request.session.get('CHGameDirectory', False)["currentGame"]
    currentRound = request.session.get('CHGameDirectory', False)["currentRound"]
    lastPlayer = request.session.get('CHGameDirectory', False)["lastPlayer"]
    gameStyle = request.session.get('CHGameDirectory', False)["gameStyle"]
    avatars = request.session.get('CHGameDirectory', False)["avatars"]
    playerRole = request.session.get('CHGameDirectory', False)["playerRole"]
    avatarRoles = request.session.get('CHGameDirectory', False)["avatarRoles"]
    nextPlayer = request.session.get('CHGameDirectory', False)["nextPlayer"]
    trialGame = request.session.get('CHGameDirectory', False)["trialGame"]
    performanceScore = request.session.get('CHGameDirectory', False)["performanceScore"]
    finishedRound = request.session.get('CHGameDirectory', False)["finishedRound"]

    simulateNextActions = bool(request.session.get('CHGameDirectory', False)["simulateNextActions"])

    pizzaForm = request.POST.get('pizzaButton', False)
    player = int(request.POST.get('playerID', False))
    nextAction = str(request.POST.get('nextActionButton', False))

    cardsDiscarded = []

    gameFinished = False
    # simulateNextActions = False
    error = ""

    expModel = getExperimentByName(expName)
    # print("nextAction:" + str(nextAction=="nextAction"), file=sys.stderr)
    # print("agentNames:" + str(agentNames), file=sys.stderr)
    # # print("dataFrame:" + str(dataFrame), file=sys.stderr)
    # print("---------", file=sys.stderr)


    if simulateNextActions:
        score, finishedRound = simulateActions(expModel, nextPlayer, firstAction, currentRound, agentNames, finishedRound)
        gameFinished = True

    simulateNextActions = False

    # if nextAction=="nextAction":
    #     print("Simulating actions:" + str(nextAction), file=sys.stderr)

        # gameFinished = True
    #     print("score:" + str(score),  file=sys.stderr)
    #     print("---------", file=sys.stderr)

    if not gameFinished:
        # print ("Pizzaform:" + str(pizzaForm))
        if pizzaForm == "pizza":
            newRound = doPizza(expModel, currentRound)
            pizza = False
            nextPlayer = lastPlayer

        elif not gameFinished:
            if player == 0:
                action = request.POST.getlist('selectedAction', [])
                isHuman = True
            else:
                isHuman = False
                action = []
            # print ("---------------------------------")
            # print ("Calling do player action!")
            # print ("---------------------------------")
            # print ("isHuman: " + str(action))
            # print ("isHuman:" + str(isHuman))


            # threadRepeat = True
            # totalTimeSlept = 0
            # thread = multiprocessing.Process(target=doPlayerAction, args=(
            # expName, player, action, firstAction, currentRound, agentNames, dataFrame, [], isHuman, Q))
            # thread.start()
            #
            # while threadRepeat:
            #     print ("Starting the thread")
            #     print("Sleeping")
            #     time.sleep(1)
            #     totalTimeSlept +=1
            #     print("after sleep")
            #     if thread.is_alive():
            #         print ("thread is still alive!")
            #         if totalTimeSlept >= 5:
            #             thread.terminate()
            #             print ("re-starting!")
            #             totalTimeSlept = 0
            #             thread = multiprocessing.Process(target=doPlayerAction, args=(
            #             expName, player, action, firstAction, currentRound, agentNames, dataFrame, [], isHuman, Q))
            #             thread.start()
            #     else:
            #         print("threadOK")
            #         threadRepeat = False
            #
            # print ("out of the thread. Waiting the Q.")
            # gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score, cardsDiscarded, dataFrame = Q.get()

            gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score, cardsDiscarded = doPlayerAction(expModel, player, action, firstAction, currentRound, agentNames, [], isHuman)
            simulateNextActions = False
            print ("action finished!")

            if hasPlayerFinished and player == 0:
                simulateNextActions = True
                finishedRound[0] = newRound+1
                # score, dataFrame = simulateActions(expName, nextPlayer, firstAction, currentRound, agentNames, dataFrame)
                # gameFinished = True

        hasErrorMessage = False
        if not error == "":
            hasErrorMessage = True

    if gameFinished:
        #Roles and points
        playerRoles = []

        # if not trialGame:
        #     playerRoles = [0, 0, 0, 0]
        #     for playerIndex in range(4):
        #         points = 3 - score.index(playerIndex)
        #         pointsScore[playerIndex] += points
        #         playerRoles[score.index(playerIndex)] = playerIndex
        #         if finishedRound[playerIndex] == 0:
        #             rnd = 0.00001
        #         else:
        #             rnd = finishedRound[playerIndex]
        #         performanceScore[playerIndex] += float((points*10)/rnd) #Change performance score



        if not trialGame:
            playerRoles = [0, 0, 0, 0]
            print ("score:" + str(score))
            for playerIndex in range(4):
                points = 3 - score.index(playerIndex)
                pointsScore[playerIndex] += points
                print ("Player:" + str(playerIndex) + " - should be score:" + str(score.index(playerIndex)))
                playerRoles[playerIndex] = score.index(playerIndex)

        # print ("Final playerRoles:" + str(playerRoles))
        gameOver = False
        if gameStyle =="Single":
            gameOver = True
        else:
            for a in (pointsScore):
                if a >= 9:
                    gameOver= True
                    break

        if not trialGame:
            for playerIndex in range(4):
                points = 3 - score.index(playerIndex)

                if finishedRound[playerIndex] == 0:
                    rnd = 0.00001
                else:
                    rnd = finishedRound[playerIndex]

                ps = performanceScore[playerIndex]

                ps += float((points * 10) / rnd)  # Change performance score

                if gameOver:
                    ps = float(ps / int(currentGame+1))
                print("Points:" + str(points))
                print("Rounds:" + str(rnd))
                print("Current ps:" + str(ps))
                performanceScore[playerIndex] = ps
                # input("here")

        humanScore = []
        for a in pointsScore:
            humanScore.append(str(a)+"/9")

        currentGame = currentGame + 1

        newRound = 0

        # Start New Game
        newGame(expModel, agentNames, currentGame, playerRoles, performanceScore)

        # deal cards
        startingPlayer = dealCards(expModel, currentGame)

        # Collecte the cards exchanged by the otherss

        dinnerServed = False
        foodFight = False
        if not trialGame:
            # expModel = getExperimentByName(expName)
            print ("Score:" + str(score))
            print("Player roles:" + str(playerRoles))
            cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher, receivedCard, playerDidAction, receivedFrom, hasSpecialCard, specialCard, newRoles = changeRolesOthers(expModel, playerRoles)
            playerHasARole = True

            print ("New roles:" + str(newRoles))


            if hasSpecialCard:
                if specialCard == "Dinner":
                    dinnerServed = True
                if specialCard == "Fight":
                    foodFight = True

            receivedCardContext = []
            if not dinnerServed:
                # Create the received cards
                receivedCardsIndex = range(len(receivedCard))

                receivedCardContext = zip(receivedCardsIndex, receivedCard)

            translatedRoleNames = [gettext('Chef'), gettext('SousChef'), gettext('Waiter'), gettext('Dishwasher')]

            playerDidAction = str(translatedRoleNames[playerDidAction]) + " ("+str(agentNames[playerRoles.index(playerDidAction)])+")"

            receivedFrom = int(receivedFrom)
            # print ("Received from:" + str(receivedFrom))
            # print ("Trnaslated:" + str(translatedRoleNames[receivedFrom]))
            # print ("agentNames:" + str(agentNames[receivedFrom]))
            # print("newRoles:" + str(newRoles))
            receivedFrom = str(translatedRoleNames[receivedFrom]) + " ("+str(agentNames[newRoles.index(receivedFrom)])+")"

            #Setting player Role
            if len(newRoles) == 0:
                newRoles = playerRoles

            rolesList = ["CHEF", "SOUSCHEF", "WAITER", "DISHWASHER"]
            thisPlayerRole = rolesList[newRoles[0]]

            PHRASES = {"CHEF": gettext('ChefMessage'),
                       "SOUSCHEF": gettext('SousChefMessage'),
                       "WAITER": gettext('WaiterMessage'),
                       "DISHWASHER": gettext('DishwasherMessage')
                       }

            phraseRole = PHRASES[thisPlayerRole]

            # print ("player roles:" + str(playerRoles))
            # print ("Player role:" + str(playerRole))
            thisPlayerPreviousRole = rolesList[playerRoles[0]]

            # Obtain PLayer0 Cards
            player0Cards, _, _, _ = renderCurrentDataset(expModel,  drawBoard=False, withSpecialCards=not(hasSpecialCard))
            # Create the possible actions
            player0CardsIndex = range(len(player0Cards))

            player0Cards = zip(player0CardsIndex, player0Cards)

        else:
            cardsChef, cardsSousChef, cardsWaiter, cardsDishwasher, receivedCard, playerDidAction, receivedFrom, hasSpecialCard, specialCard, newRoles = [],[],[],[],[],0,0,False,"",playerRoles
            playerHasARole = False
            player0Cards = []
            thisPlayerPreviousRole = ""
            playerDidAction = 0
            receivedFrom = ""
            thisPlayerRole = ""
            phraseRole = ""
            receivedCardContext = []

        # receivedFrom = translatedRoleNames + ("( "+agentNames[playerRoles.index(receivedFrom)]+" )")

        context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
                   "humanScore": humanScore, "gameOver":gameOver, "firstRound":False, "playerHasARole": playerHasARole, "thisPlayerRole": thisPlayerRole, "player0Cards":player0Cards, "phraseRole":phraseRole,
                   "error":False, "receivedCard":receivedCardContext, "receivedFrom": receivedFrom, "dinnerServed":dinnerServed, "foodFight":foodFight,
                   "thisPlayerPreviousRole":thisPlayerPreviousRole, "playerActiveAction":playerDidAction, "trialGame":False}

        session = {'directory': expName, "playerTurn": nextPlayer, "playerNames": agentNames,
                   "pointsScore": pointsScore,
                   "currentGame": currentGame, "firstAction": firstAction, "currentRound": newRound,
                   "lastPlayer": lastPlayer, "gameStyle": gameStyle,
                   "avatars": avatars, "playerRole": newRoles, "avatarRoles":avatarRoles, "nextPlayer":nextPlayer,
                   "startingPlayer":startingPlayer, "humanScore":humanScore, "cardsChef":cardsChef, "cardsSousChef":cardsSousChef, "cardsWaiter":cardsWaiter, "cardsDishwasher":cardsDishwasher, "receivedCard":receivedCard,
                   "receivedFrom": receivedFrom, "specialActionUsed":hasSpecialCard, "trialGame":False, "performanceScore":performanceScore,
                   "finishedRound":finishedRound}

        request.session['CHGameDirectory'] = session

        return render(request, 'SingleGame/startNewGame.html', context)


        # return render(request, 'SingleGame/gameFinished.html')

    # Get possible actions
    firstAction = False
    # player1AllowedActions = []
    # if nextPlayer == 0:
    #     possibleActions, player1AllowedActions, highLevelActions  = getPossibleActions(expName=expName, player=nextPlayer, firstAction=firstAction)

    oponentsAction = not nextPlayer == 0

    playerAction = False
    if nextPlayer == 0:
        playerAction = True

    if pizza:
        playerAction = False
        oponentsAction = False

    # Render dataset
    player0Cards, player1Cards, player2Cards, player3Cards = renderCurrentDataset(expModel)

    player1Cards = range(len(player1Cards))
    player2Cards = range(len(player2Cards))
    player3Cards = range(len(player3Cards))

    player0CardsLength = len(player0Cards)

    #Create the possible actions
    player0CardsIndex = range(len(player0Cards))

    player0Cards = zip(player0CardsIndex, player0Cards)

    #Has Avatar Roles
    hasAvatarRole = len(avatarRoles) > 0

    # input("here")
    print ("Last player:" + str(lastPlayer))
    print ("NExt player:" + str(nextPlayer))
    print ("Cards Discarded:" + str(cardsDiscarded))

    session = {'directory': expName, "playerTurn":nextPlayer, "playerNames": agentNames, "pointsScore": pointsScore,
               "currentGame": currentGame, "firstAction":firstAction, "currentRound": newRound, "lastPlayer":lastPlayer, "gameStyle": gameStyle,
               "avatars":avatars, "playerRole":playerRole, "avatarRoles":avatarRoles, "nextPlayer":nextPlayer, "simulateNextActions":simulateNextActions,
               "trialGame":trialGame,"performanceScore": performanceScore, "finishedRound":finishedRound}

    request.session['CHGameDirectory'] = session

    # if pizza and nextPlayer==0:
    #     nextPlayer = 3
    # print ("Sending context Pizza:" + str(pizza))

    actionDone = True
    if len(cardsDiscarded) == 0:
        actionDone = False

    print ("Discard:" + str(cardsDiscarded))
    discardedCardsList = []
    for a in cardsDiscarded:
        print ("A"+str(a))
        if "pass" in str(a):
            discardedCardsList.append("actionCards/"+"pass.png")
        else:
            discardedCardsList.append("deck/"+str(a)+".png")

    # Create the list of discarded cards
    discardedCardsList = zip(range(len(discardedCardsList)), discardedCardsList)

    context = {'expDirectory': expName, "playerNames": agentNames, "currentRound": newRound,
               "playerTurn": nextPlayer,
               "playerTurnName": "Player " + str(nextPlayer + 1) + "-" + agentNames[nextPlayer],
               "currentGame": currentGame, "pointsScore": pointsScore, "oponentsAction":oponentsAction,
               "playerAction":playerAction, "isPizza": pizza,
               "player1Cards":player1Cards, "player2Cards": player2Cards,
               "player3Cards": player3Cards, "player0Cards": player0Cards, "player0CardsLength": player0CardsLength, "ErrorMessage":error, "hasErrorMessage":hasErrorMessage,
               "avatars":avatars, "hasAvatarRole":hasAvatarRole, "avatarRoles":avatarRoles, "simulateNextActions": simulateNextActions,
               "nextPlayerName":agentNames[nextPlayer], "lastPlayerName":agentNames[player],
               "actionDone": actionDone, "actionSelected":discardedCardsList
               }

    return render(request, 'SingleGame/game.html', context)


def showRules(request):


    language = request.session.get('CHLang', False)["lang"]
    print("Language:" + str(language))
    translation.activate(language)

    nickname = request.session.get('CHNickname', False)

    ruleBookPage1 =_('ruleBook_page1Link')
    ruleBooKPage2 = _('ruleBook_page2Link')

    context = {'nickname': nickname, 'page1': ruleBookPage1, 'page2': ruleBooKPage2}

    return render(request, 'SingleGame/rules.html', context)