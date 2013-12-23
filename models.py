from google.appengine.ext import db

class League(db.Model):
    name = db.StringProperty(required = True)
    year = db.IntegerProperty(required = True)

class Week(db.Model):
    league = db.ReferenceProperty(League, collection_name='weeks')
    num = db.IntegerProperty(required = True)
    open_poll = db.BooleanProperty(required = False, default = True)
    
    def winner_list(self):
        winners = [winner.winner for winner in self.matchups]
        return winners
    
class Matchup(db.Model):
    week = db.ReferenceProperty(Week, collection_name='matchups')
    home = db.StringProperty(required = True)
    away = db.StringProperty(required = True)
    winner = db.StringProperty(required = False)
    
    def update_record(self,winner_key,loser_key):
        if winner_key:
            winner = Team.get(winner_key)
            winner.wins += 1
            
            if winner.streak < 0:
                winner.streak = 0
            winner.streak += 1
            winner.put()
            
        if loser_key:
            loser = Team.get(loser_key)
            loser.losses += 1
            if loser.streak > 0:
                loser.streak = 0
            loser.streak -= 1
            loser.put()
            

    

class Team(db.Model):
    league = db.ReferenceProperty(League, collection_name='teams')
    reddit_user = db.StringProperty(required = False, default = '')
    team = db.StringProperty(required = True)
    wins = db.IntegerProperty(required = True, default = 0)
    losses = db.IntegerProperty(required = True, default = 0)
    streak = db.IntegerProperty(required = True, default = 0)
    vote_total = db.IntegerProperty(default = 0,required = False,)
    
    def votes_num(self):
        return len([team for team in self.choices])
    #the hell?
    def week_picks(self,week_num):
        votes = {}
        for ch in self.choices:
            if week_num == ch.week:
                votes[ch.choice] = ch.choice
        return votes
            

class Vote(db.Model):
    team = db.ReferenceProperty(Team, collection_name='choices')
    week = db.IntegerProperty(required = True)
    choice = db.StringProperty(required = True)
    correct = db.BooleanProperty(required = False, default = False)
    create_date = db.DateTimeProperty(auto_now_add=True)

