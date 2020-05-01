from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import User, Game, Actions

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from SingleGame.GameController.ChefsHatOnlineController import dealCards, startNewGame, getPossibleActions, doPlayerAction, doRandomAction, doPizza, simulateActions
from SingleGame.GameController.ChefsHatOnlineRenderer import renderCurrentDataset

import numpy

# Create your views here.

def finishGame(request):
    return render(request, 'SingleGame/gameFinished.html')

def index(request):
    return render(request, 'SingleGame/index.html')

def startGame(request):

    expName = request.session.get('CHGameDirectory', None)["directory"]
    agentNames = request.session.get('CHGameDirectory', False)["playerNames"]
    pointsScore = request.session.get('CHGameDirectory', False)["pointsScore"]
    currentGame = request.session.get('CHGameDirectory', False)["currentGame"]
    gameStyle = request.session.get('CHGameDirectory', False)["gameStyle"]
    avatars = request.session.get('CHGameDirectory', False)["avatars"]
    playerRole = request.session.get('CHGameDirectory', False)["playerRole"]

    #deal cards
    startingPlayer = dealCards(expName)

    #Get possible actions
    player1AllowedActions = []
    playerAction = False
    if startingPlayer == 0:
        possibleActions, player1AllowedActions, highLevelActions = getPossibleActions(expName=expName, player=startingPlayer,
                                                                                     firstAction=True)
        playerAction = True

    #Gamestate
    gameRound = 0
    playerTurn = int(startingPlayer)
    oponentsAction = not playerTurn == 0

    # Render dataset
    player0Cards, player1Cards, player2Cards, player3Cards = renderCurrentDataset(expName, player1AllowedActions, playerRole)
    player1Cards = range(len(player1Cards))
    player2Cards = range(len(player2Cards))
    player3Cards = range(len(player3Cards))

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
               "avatars": avatars, "playerRole": playerRole, "avatarRoles":avatarRoles, "nextPlayer":0}

    request.session['CHGameDirectory'] = session

    context = {'expDirectory': expName, "playerNames": agentNames, "currentRound":gameRound,
               "playerTurn":playerTurn, "playerTurnName":"Player "+str(playerTurn+1)+"-"+agentNames[playerTurn],
                "currentGame":currentGame, "pointsScore": pointsScore, "oponentsAction":oponentsAction,
               "playerAction" : playerAction, "player1Cards":player1Cards, "player2Cards":player2Cards,
               "player3Cards":player3Cards, "player0Cards":player0Cards, "ErrorMessage":"", "hasErrorMessage":False,
               "avatars":avatars, "hasAvatarRole":hasAvatarRole, "avatarRoles":avatarRoles}


    return render(request, 'SingleGame/game.html', context)

def selectAdversaries(request):
    userName = request.POST.get('userName', False);
    userList = User.objects.filter(name=userName)

    if len(userList) == 1:
        user = userList[0]
    else:
        user = User(name=userName)
        user.save()

    DQL = 'DQL'
    PPO = 'PPO'
    A2C = 'A2C'
    AIRL = 'AIRL'
    Random = "RANDOM"

    oponentChoices = [DQL, PPO, A2C, AIRL, Random ]
    context = {'user': user, "oponentChoices": oponentChoices}

    # Update session
    session = {'directory': "", "playerTurn": "", "playerNames": "", "pointsScore": "",
               "currentGame": "", "firstAction": "", "currentRound": "", "lastPlayer": 0,
               "gameStyle": ""}

    request.session['CHGameDirectory'] = session

    session = {'user': userName}
    request.session['gameSession'] = session

    return render(request, 'SingleGame/selectAdversaries.html', context)

def startNewExperiment(request):

    session = request.session.get('gameSession', None)
    user = User.objects.filter(name=session["user"])[0]

    op1 = request.POST.get('oponent1', False)
    op2 = request.POST.get('oponent2', False)
    op3 = request.POST.get('oponent3', False)
    gameStyle = request.POST.get('gameStyle', False)

    avatars = []

    for a in [op1, op2, op3]:
        if a == "Random":
            avatars.append("/static/images/randomAgent.png")
        elif a == "A2C":
            avatars.append("/static/images/A2CAgent.png")
        elif a == "PPO":
             avatars.append("/static/images/PPOAgent.png")
        elif a == "DQL":
            avatars.append("/static/images/DQLAgent.png")


    agentNames =  [user.name, op1+"_1", op2+"_2", op3+"_3"]
    currentGame = 0

    expName = startNewGame(agentNames, gameStyle)

    points = [0,0,0,0]
    humanScore = []
    if gameStyle == "Single":
        humanScore = [0, 0, 0, 0]
    else:
            for a in range(4):
               humanScore.append("0/15")

    playerRoles = []


    context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
               "humanScore": humanScore, "gameOver":False}

    session = {'directory': expName, "playerTurn": "", "playerNames": agentNames, "pointsScore": points,
               "currentGame": currentGame, "firstAction": "", "currentRound": "",
               "lastPlayer": "", "gameStyle": gameStyle, "avatars":avatars, "playerRole": [], "playerRole":playerRoles}

    request.session['CHGameDirectory'] = session

    return render(request, 'SingleGame/startNewGame.html', context)


def doAction(request):

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

    pizzaForm = request.POST.get('pizzaButton', False)
    player = int(request.POST.get('playerID', False))
    nextAction = str(request.POST.get('nextActionButton', False))

    gameFinished = False
    simulateNextActions = False
    error = ""

    import sys
    print("---------", file=sys.stderr)
    print("nextAction:" + str(nextAction), file=sys.stderr)
    print("nextAction:" + str(nextAction=="nextAction"), file=sys.stderr)
    print("agentNames:" + str(agentNames), file=sys.stderr)
    print("---------", file=sys.stderr)

    # if nextAction=="nextAction":
    #     print("Simulating actions:" + str(nextAction), file=sys.stderr)
    #
    #     gameFinished = True
    #     print("score:" + str(score),  file=sys.stderr)
    #     print("---------", file=sys.stderr)

    if not gameFinished:
        if pizzaForm == "pizza":
            newRound = doPizza(expName, currentRound)
            pizza = False
            nextPlayer = lastPlayer

        elif not gameFinished:
            if player == 0:
                action = request.POST.getlist('selectedAction', [])
                isHuman = True
            else:
                isHuman = False
                action = []

            gameFinished, hasPlayerFinished, nextPlayer, newRound, lastPlayer, pizza, error, score = doPlayerAction(expName, player, action, firstAction, currentRound, agentNames, isHuman=isHuman)

            if hasPlayerFinished and player == 0:
                simulateNextActions = True
                score = simulateActions(expName, nextPlayer, firstAction, currentRound, agentNames)


        hasErrorMessage = False
        if not error == "":
            hasErrorMessage = True

    if gameFinished:
        #Roles and points
        playerRoles = [0, 0 ,0 ,0]
        for playerIndex in range(4):
            points = 3 - score.index(playerIndex)
            pointsScore[playerIndex] += points
            playerRoles[score.index(playerIndex)] = playerIndex

        gameOver = False
        if gameStyle =="15Points":

            for aIndex, a in enumerate(pointsScore):
                if a >= 15:
                    gameOver= True
                    break
        else:
            gameOver = True

        humanScore = []
        for a in pointsScore:
            humanScore.append(str(a)+"/15")

        currentGame = currentGame + 1

        newRound = 0


        import sys
        print("---------", file=sys.stderr)
        print("playerRoles:" + str(playerRoles), file=sys.stderr)
        print("points:" + str(pointsScore), file=sys.stderr)
        print("gameOver:" + str(gameOver), file=sys.stderr)
        print("gameStyle:" + str(gameStyle), file=sys.stderr)

        context = {"playerNames": agentNames, "currentGame": int(currentGame), "nextGameGame": int(currentGame) + 1,
                   "humanScore": humanScore, "gameOver":gameOver}

        session = {'directory': expName, "playerTurn": nextPlayer, "playerNames": agentNames,
                   "pointsScore": pointsScore,
                   "currentGame": currentGame, "firstAction": firstAction, "currentRound": newRound,
                   "lastPlayer": lastPlayer, "gameStyle": gameStyle,
                   "avatars": avatars, "playerRole": playerRoles, "avatarRoles":avatarRoles, "nextPlayer":nextPlayer}

        request.session['CHGameDirectory'] = session


        return render(request, 'SingleGame/startNewGame.html', context)


        # return render(request, 'SingleGame/gameFinished.html')

    # Get possible actions
    firstAction = False
    player1AllowedActions = []
    if nextPlayer == 0:
        possibleActions, player1AllowedActions, highLevelActions  = getPossibleActions(expName=expName, player=nextPlayer, firstAction=firstAction)

    oponentsAction = not nextPlayer == 0

    playerAction = False
    if nextPlayer == 0:
        playerAction = True

    if pizza:
        playerAction = False
        oponentsAction = False

    # Render dataset
    player0Cards, player1Cards, player2Cards, player3Cards = renderCurrentDataset(expName, player1AllowedActions, playerRole)

    player1Cards = range(len(player1Cards))
    player2Cards = range(len(player2Cards))
    player3Cards = range(len(player3Cards))

    #Create the possible actions
    player0CardsIndex = range(len(player0Cards))

    player0Cards = zip(player0CardsIndex, player0Cards)

    #Has Avatar Roles
    hasAvatarRole = len(avatarRoles) > 0


    session = {'directory': expName, "playerTurn":nextPlayer, "playerNames": agentNames, "pointsScore": pointsScore,
               "currentGame": currentGame, "firstAction":firstAction, "currentRound": newRound, "lastPlayer":lastPlayer, "gameStyle": gameStyle,
               "avatars":avatars, "playerRole":playerRole, "avatarRoles":avatarRoles, "nextPlayer":nextPlayer}

    request.session['CHGameDirectory'] = session

    context = {'expDirectory': expName, "playerNames": agentNames, "currentRound": newRound,
               "playerTurn": nextPlayer,
               "playerTurnName": "Player " + str(nextPlayer + 1) + "-" + agentNames[nextPlayer],
               "currentGame": currentGame, "pointsScore": pointsScore, "oponentsAction":oponentsAction,
               "playerAction":playerAction, "isPizza": pizza,
               "player1Cards":player1Cards, "player2Cards": player2Cards,
               "player3Cards": player3Cards, "player0Cards": player0Cards, "ErrorMessage":error, "hasErrorMessage":hasErrorMessage,
               "avatars":avatars, "hasAvatarRole":hasAvatarRole, "avatarRoles":avatarRoles, "simulateNextActions":simulateNextActions}


    return render(request, 'SingleGame/game.html', context)