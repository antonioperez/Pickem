
Unfortunately I haven't got around to correctly mapping the website with an admin interface, so you will have to remember the urls to use the website. Also, user auth was next on my list as anybody can know the management urls and mess with the information.
The bulk of this project was done in a span of two days, which lead to some funky code. I was a bit inexperienced and making the code functional was my priority.  


ADDING LEAGUE
'/add/league/' 



Fill out form by adding the league name and the current year. You will be redirected to the management page. 
ADDING TEAM INFORMATION
'<league name>/year/<year number>/manage/' 

Take note of the url here. Your league name and year will be included in the url, so that you know you are editing your league. On this management page you will be able to add W/L information and Reddit names to each team. You can only add one at a time right now. So add the information and press enter or the ride side submit button. You should get a 'success' on the far right column.

There are 'Bucs' and 'Buccaneers', ignore the 'Buccaneers'. 

ADDING WEEK MATCHUPS
<league name>/year/<year number>/add/matches/ 

Take note of the URL again. Every page will have /<leaguename>/year/<number>/<direction>

To add a week to the league, you add the week number in top text field where it says 'Week'.
On the text area field (the big box under the week field),  you simply paste the schedule from the madden daddy weekly schedule page. 
Control-C and Control-V. You should be redirected to the weekly pick em. 

WEEKLY PICK'EM
<league name>/year/<year number>/week/<week number>/

This is the page you will be linking people to do their picks. When you choose the winner, people won't be able to select the winner. The program will ignore their vote. Also, to see the total amount of votes for each team, you will have to shutdown the voting poll. Once you close the polling, you can simply link it back to see the total amount of picks for each team. 


SELECTING WINNER/CLOSING POLL
'<league name>/year/<year number>/week/<week number>/winners/'


Again, take note of the URL. By adding '/winners/' to the end of the url of the weekly pick 'em. 
Close the voting, by selecting 'OFF' on the voting dropdown. 
Select the winner exactly as picking a pick 'em. You should see the logo of the winner you selected on the right side and a blue 'W' on the pick 'em voting page.  

RESULTS 
'<league name>/year/<year number>/week/<week number>/all/'


This url will give you a results table of all the weeks that were voted on and where the voting was turned off in the /winners/ page. It is ordered by percentages. This is crucial, you should take a screenshot of the results table. The server I am hosting on the website isn't going to take much load, so DO NOT link people to this page. Take a screenshot and upload to imgur. 

LINK SUMMERY 


   * '/add/league/'
   * 
      * add  league
   * '/<league name>/year/<year number>/add/matches/  
   * 
      * add matches
   * '/<league name>/year/<year number>/manage/' 
   * 
      * add W/L, names
   * /<league name>/year/<year number>/week/<week number>/' 

   * 
      * pick 'em page
   * '/<league name>/year/<year number>/week/<week number>/winners/'

   * 
      * pick weekly winners, close poll
   * '/<league name>/year/<year number>/week/<week number>/all/'

   * 
      * Show results. 


