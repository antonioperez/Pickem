#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from models import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

teams_global = [
        'Redskins', 'Bucs','Buccaneers',
        'Ravens'  ,   'Jets' ,
        'Falcons'  ,  'Bears' ,
        'Bengals' ,   'Texans', 
        'Lions'    ,'Vikings' ,
        'Jaguars'   , 'Panthers' ,
        'Seahawks'   , 'Eagles' ,
        'Chiefs'  ,  'Chargers' ,
        'Bills' ,   'Raiders' ,
        'Titans' ,   'Steelers', 
        'Broncos' ,   'Browns' ,
        'Giants'  ,  'Patriots' ,
        'Cowboys'  ,  'Cardinals' ,
        'Rams'   ,  '49ers' ,
        'Saints'  ,  'Packers', 
        'Dolphins' ,   'Colts' ,         
            ]
    
class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class VotingPoll(BaseHandler):
    def get(self,league,year,week):
        tally = {}
        corrects = {}
        records = {}
        streaks = {}
        reddit_names = {}
        winners = []
        curr_week = None
        
        for team in teams_global:
            records[team] = '0-0'
            streaks[team] = 0
            tally[team] = 0
            corrects[team] = 0
            
        league = str(league)
        year = int(year)
        week = int(week)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        if league_info:
            curr_week = league_info.weeks.filter('num =',week).get()
            if curr_week:
                winners = curr_week.winner_list()
                teams = league_info.teams
                for team in teams:
                    records[team.team] = '%s-%s' % (team.wins,team.losses)
                    reddit_names[team.team] = team.reddit_user
                    streaks[team.team] = team.streak
                    if not curr_week.open_poll:
                        for vote in team.choices:
                            if (int(vote.week) == week) and (vote.choice in tally.keys()):
                                tally[vote.choice] += 1
                            if (int(vote.week) == week) and vote.choice in winners:
                                corrects[team.team] += 1
        
        self.render('voting.html', streaks = streaks,curr_week = curr_week, league_info = league_info,
                                week_url = week, tally = tally, records = records, teams = sorted(reddit_names.iterkeys()),
                                corrects = sorted(corrects.items(), key= lambda x: x[1], reverse=True),
                                reddit_names = reddit_names,winners = winners, all_weeks = sorted(league_info.weeks, key=lambda week: week.num,))   
         
    def post(self,league,year,week):
        message = 'Thanks for voting!'
        league = str(league)
        year = int(year)
        week = int(week)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        
        choices = [self.request.get('choice'+str(x),None) for x in xrange(0,25) ]
        user_team = str(self.request.get('userteam')).lower().capitalize()
        
        curr_week = league_info.weeks.filter('num =',week).get()
        winners = curr_week.winner_list()
        if (user_team in teams_global) and curr_week.open_poll:
            team = league_info.teams.filter('team =',user_team).get()
            
            for choice in choices:
                check_dup = team.choices.filter('choice =',choice).filter('week =',week).get()
                if (choice in teams_global) and (not check_dup):
                    if choice not in winners:
                        Vote(team = team, choice = choice,week = week).put()
                    else:
                        message += 'A choice you picked has already been selected as a winner. Ignored. \n'
        else:
            message = 'Whoops, the voting poll might be closed.'
        
        url = "/%s/year/%s/week/%s/" % (league,year,week)
                
        self.render('thanks.html',url = url, message = message)
  
    
class AddLeague(BaseHandler):
    def get(self):
        self.render('management/league_add.html')
    def post(self):
        league = str(self.request.get('league')).lower()
        year = int(self.request.get('year'))
        if league and year:
            league_db = League( name = league,year=year)
            league_db.put()
            for team in teams_global:
                Team(league = league_db,team = team).put()
        url = "/%s/year/%s/manage/" %(league,year)
        self.redirect(url)

class AddMatches(BaseHandler):
    def get(self,league,year,):
        self.render('management/add_matches.html')
    def post(self,league,year): 
        message = ''
        matches = {}
        try:
            matches = eval(str(self.request.get('matches')).strip()) #find better solution for converting string to dictionary
            league = str(league)
            year = int(year)
            week = int(self.request.get('week'))
            league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        except:
            self.render('whoops.html')
        
        if matches and league_info:
            curr_week = Week(league = league_info,num = week).put()
            if curr_week:
                for away,home in matches.iteritems():
                    Matchup(week = curr_week,away = away,home = home).put()
                message = 'sucess'
                
                url = "/%s/year/%s/week/%s/" %(league,year,week)
                self.redirect(url)
        

class ChooseWinner(BaseHandler):
    def get(self,league,year,week):
        records = {}
        reddit_names = {}
        team_ids = {}
        for team in teams_global:
            records[team] = '0-0'
        league = str(league)
        year = int(year)
        week = int(week)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        if league_info:
            curr_week = league_info.weeks.filter('num =',week).get()
            teams = league_info.teams
            for team in teams:
                records[team.team] = '%s-%s' % (team.wins,team.losses)
                reddit_names[team.team] = team.reddit_user
                team_ids[team.team] = team.key()

        self.render('management/winners.html', team_ids = team_ids,curr_week = curr_week, league_info = league_info,
                    week_url = week, records = records, reddit_names = reddit_names,all_weeks = sorted(league_info.weeks, key=lambda week: week.num,),)
    
    def post(self,league,year,week):
        league = str(league)
        year = int(year)
        week = int(week)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        
        #choices = [self.request.get('choice'+str(x),None) for x in xrange(0,25)]
        choices = {}
        home_choices = {}
        away_choices = {}
            
        for x in xrange(0,25):
            choice = self.request.get('choice'+str(x),None)
            key = self.request.get('match_key'+str(x),None)
            
            home_team = self.request.get('home_team'+str(x),None)
            away_team = self.request.get('away_team'+str(x),None)
            
            home_key = self.request.get('home_team_key'+str(x),None)
            away_key = self.request.get('away_team_key'+str(x),None)
            choices[choice] = key
            
            home_choices[home_team] = [home_key,away_key]
            away_choices[away_team] = [away_key,home_key]
        
        if 'winner_sub' in self.request.POST:
            if league_info and choices:
                curr_week = league_info.weeks.filter('num =',week).get()
                if curr_week:  
                    for choice in choices:
                        if choice in teams_global:
                            update_matchup = Matchup.get(choices[choice])
                            
                            if choice in home_choices:
                                update_matchup.update_record(home_choices[choice][0],home_choices[choice][1])
                                
                            if choice in away_choices:
                                update_matchup.update_record(away_choices[choice][0],away_choices[choice][1])  
                                     
                            update_matchup.winner = choice
                            update_matchup.put()
                            
        if 'voting_change' in self.request.POST:
            key = self.request.POST.get('voting_change')
            poll_switch = self.request.POST.get('poll_switch')
            update_week = Week.get(key)
            if poll_switch == 'open':
                update_week.open_poll = True
            if poll_switch == 'close':
                update_week.open_poll = False
            update_week.put()
            
            
        
        url = "/%s/year/%s/week/%s/winners/" %(league,year,week)
                
        self.redirect(url)
        
class Management(BaseHandler):
    def get(self,league,year):
        success = {} 
        teams = {}
        league = str(league)
        year = int(year)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        if league_info:
            teams = league_info.teams
                    
        self.render('management/management.html',teams = teams,league_info = league_info, success = success)
        
    def post(self,league,year): 
        success = {}           
        league = str(league)
        year = int(year)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        
        wins = int(self.request.get('wins'))
        losses = int(self.request.get('losses'))
        reddit_user = str(self.request.get('reddit_name'))
        team_id = self.request.get('id')
        if league_info:
            teams = league_info.teams
            update_team = Team.get(team_id)
            update_team.wins = wins
            update_team.losses = losses
            update_team.reddit_user = reddit_user
            success[update_team.team] = 'Success!'
            update_team.put()
                    
        self.render('management/management.html',teams = teams, league_info = league_info, success = success)

class LeagueSearch(BaseHandler):
    def get(self):

        self.render('search.html')

class AllVotesTest(BaseHandler):
    def check_equal(self,iterator):
        return len(set(iterator)) <= 1
    
    def get(self,league,year):
        corrects = {}
        reddit_names = {}
        weeks_parti = {}
        vote_percent = {} # percent based on total votes
        total_votes = {}
        weeks_played= {} #weeks participated
        weekly_correct = {}
        games = 0 # 
        
        for team in teams_global:
            corrects[team] = 0
            weeks_parti[team] = 0
            weeks_played[team] = []
            weekly_correct[team] = {}
            vote_percent[team] = 0.0
            total_votes[team] = 0
            
            
            
        league = str(league)
        year = int(year)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        if league_info:
            all_weeks = league_info.weeks
            teams = league_info.teams
            weeks_info = {}
            for week in all_weeks:
                winners = week.winner_list()
                if not self.check_equal(winners):
                    weeks_info[week.num] = winners
                    for i in winners:
                        if i != None: games += 1
                    
            for team in teams:
                team_name = team.team
                reddit_names[team_name] = team.reddit_user
                tgv = 0.0 #total games voted
                for vote in team.choices:                   
                    if weeks_info.get(vote.week) > 0:
                        tgv += 1
                    if weeks_info.get(vote.week) > 0 and vote.choice in weeks_info.get(vote.week):
                        week_num = vote.week
                        corrects[team_name] += 1
                        if weekly_correct[team_name].get(int(week_num)) < 0:
                            weekly_correct[team_name][int(week_num)] = 1
                        else:
                            weekly_correct[team_name][int(week_num)] += 1
                            
                    if vote.week not in weeks_played[team.team]:
                        weeks_played[team_name].append(int(vote.week))
                                
                
                weeks_parti[team_name] = len(weeks_played[team_name])
                weeks_played[team_name]= sorted(weeks_played[team_name])
                if tgv > 0:
                    vote_percent[team_name] = round((corrects[team_name]/tgv)*100,2)
                total_votes[team_name]= int(tgv)

        self.render('season_tally_test.html', totals = total_votes, corrects = corrects, 
                                reddit_names = reddit_names,games = games, weeks_parti = weeks_parti, 
                                vote_percent=sorted(vote_percent.items(), key= lambda x: x[1], reverse=True), w = weeks_played,
                                weeks_info=weeks_info,weekly_correct=weekly_correct)
        
class AddMatchesMD(BaseHandler):
    def parse_matchups(self,matches):
        team_data = []
        for m in matches.split():
            m = m.lower().capitalize()
            if m in teams_global:
                if m == 'Buccaneers':
                    team_data.append('Bucs')
                else:
                    team_data.append(m)
        week_matches = {}
        for i in xrange(0,len(team_data),2):
            week_matches[team_data[i]] = team_data[i+1]
        return week_matches
    
    def get(self,league,year,):
        self.render('management/add_matches.html')
    def post(self,league,year): 
        message = ''
        matches = {}
        try:
            matches = self.parse_matchups(self.request.get('matches')) #find better solution for converting string to dictionary
            league = str(league)
            year = int(year)
            week = int(self.request.get('week'))
            league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        except:
            self.render('whoops.html',matches=matches)
        
        if matches and league_info:
            curr_week = Week(league = league_info,num = week).put()
            if curr_week:
                for away,home in matches.iteritems():
                    Matchup(week = curr_week,away = away,home = home).put()
                message = 'sucess'
                
                url = "/%s/year/%s/week/%s/" %(league,year,week)
                self.redirect(url)

class Upsets(BaseHandler):
    
    def get(self,league,year,week):
        tally = {}
        records = {}
        streaks = {}
        reddit_names = {}
        winners = []
        curr_week = None
        
        for team in teams_global:
            records[team] = '0-0'
            streaks[team] = 0
            tally[team] = 0
            
        league = str(league)
        year = int(year)
        week = int(week)
        league_info = db.Query(League).filter('name =',league).filter('year =',year).get()
        if league_info:
            curr_week = league_info.weeks.filter('num =',week).get()
            if curr_week:
                winners = curr_week.winner_list()
                teams = league_info.teams
                for team in teams:
                    records[team.team] = '%s-%s' % (team.wins,team.losses)
                    reddit_names[team.team] = team.reddit_user
                    streaks[team.team] = team.streak
                    if not curr_week.open_poll:
                        for vote in team.choices:
                            if (int(vote.week) == week) and (vote.choice in tally.keys()):
                                tally[vote.choice] += 1
                                
                all_matches = curr_week.matchups
                upsets = []
                for match in all_matches:
                    if match.away in winners and  tally[match.away] <= tally[match.home]:
                        upsets.append(match)
                        
                    elif match.home in winners and  tally[match.home] <= tally[match.away]:
                        upsets.append(match)
                        
                reddit_table_code = """
**UPSET ALERT Week 17**

| Votes   |Name    | Record   | Score | Record   |Name    | Votes   |
|:-----------|------------:|:------------:|------------:|:------------:|------------:|:------------:|
|3    |[](//#Cardinals) gamma42 **W**|7-9  |    26-21 |    10-6    | Jmffn[](//#Redskins)|     5|
|1    |[](//#Lions) bigpops    **W** |9-7|    42-26  |     10-6    | Biosin [](//#Steelers)|     7|
|2    |[](//#Ravens) spidermanjka2k **W**|9-7  |    31-17 |    8-8    | cantstopboston[](//#Vikings)|     6|
|2    |[](//#Panthers) Indycolt87**W**|5-11  |35-28 |    7-9    | JFay82[](//#Jets)|     6|
|2    |[](//#Broncos) Salvania **W**|2-14  |    31-10 |    6-10    | SkeadLegend[](//#Jaguars)|     6|
|2    |[](//#49ers) Midgetmoose **W**|8-8  |    33-14 |    13-3    | Chaz[](//#Texans)|     7|
|4    |[](//#Raiders) Kalashnikova **W**|8-8  |    28-24 |    10-6    | Karmali[](//#Chiefs)|     5|
"""
                                
        self.render('management/upsets.html', reddit_table_code=reddit_table_code,streaks = streaks,upsets = upsets, league_info = league_info,
                                week_url = week, tally = tally, records = records, teams = sorted(reddit_names.iterkeys()),
                                reddit_names = reddit_names,winners = winners, all_weeks = sorted(league_info.weeks, key=lambda week: week.num,))   
         
        

app = webapp2.WSGIApplication([ (r'^/',LeagueSearch),
                               (r'^/([a-z]+)/year/([0-9]+)/week/([0-9]+)/',VotingPoll),
                               (r'^/add/league/',AddLeague),
                              # (r'^/([a-z]+)/year/([0-9]+)/add/matches/',AddMatches),
                               (r'^/([a-z]+)/year/([0-9]+)/add/matches/',AddMatchesMD),
                               (r'^/([a-z]+)/year/([0-9]+)/week/([0-9]+)/winners/',ChooseWinner),
                               (r'^/([a-z]+)/year/([0-9]+)/week/([0-9]+)/upsets/',Upsets),
                                (r'^/([a-z]+)/year/([0-9]+)/manage/',Management),
                                 (r'^/([a-z]+)/year/([0-9]+)/all/',AllVotesTest),
                               ],
                              debug=True)