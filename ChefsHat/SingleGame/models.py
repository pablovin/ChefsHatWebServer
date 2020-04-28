from django.db import models
# from SingleGame.ChefsHatGYM.KEF.DataSetManager import actionFinish, actionDiscard, actionPass, actionDeal, actionInvalid, actionNewGame, actionChangeRole, actionPizzaReady

class User(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, blank=False, null=False)

class Game(models.Model):
    DQL = 'DQL'
    PPO = 'PPO'
    A2C = 'A2C'
    AIRL = 'AIRL'
    Random = "RANDOM"

    OPONNETS = [
        (DQL, 'DQL'),
        (PPO, 'PPO'),
        (A2C, 'A2C'),
        (AIRL, 'AIRL'),
        (Random, 'RAN'),
    ]


    def __str__(self):
        players = [self.user.name, self.oponent1, self.oponent2, self.oponent3]
        return str(self.date) + "_"+str(players)


    date = models.DateTimeField(auto_now = True)
    previousGame = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    oponent1 = models.CharField(
        max_length=6,
        choices=OPONNETS,
        default=Random,
    )
    oponent2 = models.CharField(
        max_length=6,
        choices=OPONNETS,
        default=Random,
    )
    oponent3 = models.CharField(
        max_length=6,
        choices=OPONNETS,
        default=Random,
    )

class Actions(models.Model):

    # ACTIONTYPE = [actionFinish, actionDiscard, actionPass, actionDeal, actionInvalid, actionNewGame, actionChangeRole, actionPizzaReady]

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now = True)
    gameNumber = models.CharField(max_length= 50)
    roundNumber = models.CharField(max_length= 50)
    player = models.CharField(max_length= 50)
    actionType = models.CharField(max_length= 50)
    playerHand = models.CharField(max_length= 400)
    board = models.CharField(max_length= 400)
    possibleActions = models.CharField(max_length= 400)
    cardAction = models.CharField(max_length= 400)
    reward = models.CharField(max_length= 400, default="")
    qValues = models.CharField(max_length= 400, default="")
    loss = models.CharField(max_length= 400)
    wrongActions = models.CharField(max_length= 400)
    totalActions = models.CharField(max_length= 400)
    scores = models.CharField(max_length= 400)
    roles = models.CharField(max_length= 400)
    playerStatus =models.CharField(max_length= 400)
    agentNames = models.CharField(max_length= 400)

# Create your models here.
