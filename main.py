import csv
from bokeh.plotting import figure, output_file, show
import pandas
from bokeh.models import ColumnDataSource, HoverTool, WheelZoomTool, Panel
from bokeh.layouts import widgetbox
from bokeh.layouts import column, row, WidgetBox
from bokeh.models.widgets import CheckboxGroup, Tabs, RadioGroup
from bokeh.io import curdoc


#To run server: bokeh serve --show main.py#


playersDict={}          #key:(first name, last name, debut) value: playerID
playersDict_reverse={}  #key: playerID, value: (first and last in one string)

battersAllStats={}      #key is ID, year; definition is all other stats
pitchersAllStats={}     #key is ID, year; definition is all other stats

playersYearToYear={}    #key is ID, year; definition is the year of that player's career

#Used for radio buttons
radio_list_batting=['G', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HBP', 'SH', 'SF', 'GIDB', 'Avg']
radio_list_pitching=['W', 'L', 'G', 'GS', 'CG', 'SHO', 'SV', 'IPouts', 'H', 'ER', 'HR', 'BB', 'SO', 'BAOpp', 'ERA', 'IBB', 'WP', 'HBP', 'BK', 'BFP', 'GF', 'R', 'SH', 'SF', 'GIDP']


#Batter Stats:
#[0]- teamID
#[1]- lgID
#[2]- G
#[3]- AB
#[4]- R
#[5]- H
#[6]- 2B
#[7]- 3B
#[8]- HR
#[9]- RBI
#[10]- SB
#[11]- CS
#[12]- BB
#[13]- SO
#[14]- IBB
#[15]- HBP
#[16]- SH
#[17]- SF
#[18]- GIDP
#[19]- Avg

#Pitcher Stats:
#[0]- teamID
#[1]- lgID
#[2]- W
#[3]- L
#[4]- G
#[5]- GS
#[6]- CG
#[7]- SHO
#[8]- SV
#[9]- IPouts
#[10]- H
#[11]- ER
#[12]- HR
#[13]- BB
#[14]- SO
#[15]- BAOpp
#[16]- ERA
#[17]- IBB
#[18]- WP
#[19]- HBP
#[20]- BK
#[21]- BFP
#[22]- GF
#[23]- R
#[24]- SH
#[25]- SF
#[26]- GIDP







#same as int function but returns 0 if csv field is empty
def iint(x):
  if x == '':
    return 0
  else:
    return int(x)
    
#same as float function but returns 0 if csv field is empty
def ffloat(x):
  if x == '':
    return 0
  else:
    return float(x)

#used for AB in batting average calculation so that divide-by-0 not caused
def noZero(x):
  if x == '0':
    return 1 
  return int(x)


#Returns name of stat that corresponds with the number
#used for graph title, y-axis
def getBattingStat(num):
  if num==0:
    return "teamID"
  if num==1:
    return 'lgID'
  if num==2:
    return 'Games'
  if num==3:
    return 'At-bats'
  if num==4:
    return 'Runs'
  if num==5:
    return 'Hits'
  if num==6:
    return 'Doubles'
  if num==7:
    return 'Triples'
  if num==8:
    return 'Home Runs'
  if num==9:
    return 'Runs Batted In'
  if num==10:
    return 'Stolen Bases'
  if num==11:
    return 'Caught Stealing'
  if num==12:
    return 'Walks'
  if num==13:
    return 'Strikeouts'
  if num==14:
    return "Intentional Walks"
  if num==15:
    return 'Hit by Pitch'
  if num==16:
    return 'Sacrifice Hits'
  if num==17:
    return 'Sacrifice Flies'
  if num==18:
    return 'Grounded Into Double Play'
  if num==19:
    return 'Batting Average'

#Returns name of stat that corresponds with the number
#used for graph title, y-axis
def getPitchingStat(num):
  if num==0:
    return "teamID"
  if num==1:
    return 'lgID'
  if num==2:
    return 'Wins'
  if num==3:
    return 'Losses'
  if num==4:
    return 'Games'
  if num==5:
    return 'Games Started'
  if num==6:
    return 'Complete Games'
  if num==7:
    return 'Shutouts'
  if num==8:
    return 'Saves'
  if num==9:
    return 'IPOuts'
  if num==10:
    return 'Hits'
  if num==11:
    return 'Earned Runs'
  if num==12:
    return 'Home Runs'
  if num==13:
    return 'Walks'
  if num==14:
    return "Strikeouts"
  if num==15:
    return 'Opposing Batting Average'
  if num==16:
    return 'Earned Run Average (ERA)'
  if num==17:
    return 'Intentional Walks'
  if num==18:
    return 'Wild Pitch'
  if num==19:
    return 'Hit by pitch'
  if num == 20:
    return 'Balk'
  if num == 21:
    return 'Batters Faced'
  if num == 22:
    return 'Games Finished'
  if num == 23:
    return 'Runs'
  if num == 24:
    return 'Sacrifice Hits'
  if num == 25:
    return 'Ground into Double Play'
  


#Prints out the list of codes for stat definitions when asking user what to graph
def printBattingStats():
  for i in range(2, 20):
    print(str(i) + " = " + getBattingStat(i))

def printPitchingStats():
  for i in range(2, 26): 
    print(str(i) + " = " + getPitchingStat(i))

  

#input last name and first name
#returns the playerid
#if multiple players with same name, asks user based on debut date
def search_for_player(lastname, firstname):
  lastname=lastname.capitalize()
  firstname=firstname.capitalize()
  potential_match_list=[]
  for akey in playersDict.keys():
    if akey[0] == lastname and akey[1] == firstname:
      potential_match_list.append((playersDict[akey], akey[2]))
  if len(potential_match_list) == 1:
    return potential_match_list[0]
  else:
    for match in potential_match_list:
      inp=input("Was it " + firstname + ' ' + lastname + " who debuted in " + match[1] + "? (y/n)")
      if inp == 'y' or inp == 'Y':
        return match
  return None

 
#Returns a dictionary where key is the year, value is the player's stats in the year in list form 
def get_batter_all_stats(playerID):
  yearlyStat = {}
  for akey in battersAllStats.keys():
    if akey[0] == playerID:
      yearlyStat[iint(akey[1])] = list(battersAllStats[akey]) #gets all the stats from the player's year
      yearlyStat[iint(akey[1])].append(playersYearToYear[akey])
      for i in range(2, 19):
        yearlyStat[iint(akey[1])][i]= iint(yearlyStat[iint(akey[1])][i])
      yearlyStat[iint(akey[1])][19] = yearlyStat[iint(akey[1])][19] #sets batting average
      yearlyStat[iint(akey[1])][20] = yearlyStat[int(akey[1])][20]     
  return yearlyStat  

#Returns a dictionary where key is year, value is player's stats in the year in list form
def get_pitcher_all_stats(playerID):
  yearlyStat = {}
  for akey in pitchersAllStats.keys():
    if akey[0] == playerID:
      yearlyStat[iint(akey[1])] = list(pitchersAllStats[akey]) #gets all the stats from the player's year
      yearlyStat[iint(akey[1])].append(playersYearToYear[akey])
      for i in range(2, 15):
        yearlyStat[iint(akey[1])][i]= iint(yearlyStat[iint(akey[1])][i])
      yearlyStat[iint(akey[1])][15] = yearlyStat[iint(akey[1])][15] #sets BAOpp
      yearlyStat[iint(akey[1])][16] = yearlyStat[iint(akey[1])][16] #sets ERA
      for i in range(17, 27):
        yearlyStat[iint(akey[1])][i]= iint(yearlyStat[iint(akey[1])][i])
      yearlyStat[iint(akey[1])][27] = yearlyStat[int(akey[1])][27]     
  return yearlyStat  
  

#Takes in a dictionary of year:stats, converts it to a ColumnDataSource, each column is year or stat number, rows are years
#Skips the pandas dataframe step
def all_stats_dict_to_src_batter(stats, interest):
  data={}
  data['Year'] = list(stats.keys())
  data['0']=[]
  data['1']=[]
  data['2']=[]
  data['3']=[]
  data['4']=[]
  data['5']=[]
  data['6']=[]
  data['7']=[]
  data['8']=[]
  data['9']=[]
  data['10']=[]
  data['11']=[]
  data['12']=[]
  data['13']=[]
  data['14']=[]
  data['15']=[]
  data['16']=[]
  data['17']=[]
  data['18']=[]
  data['19']=[]
  data['CareerYear'] = []
  data['interest'] = []
  interest_count=0
  for season in stats.values():
    data['0'].append(season[0])
    data['1'].append(season[1])
    data['2'].append(season[2])
    data['3'].append(season[3])
    data['4'].append(season[4])
    data['5'].append(season[5])
    data['6'].append(season[6])
    data['7'].append(season[7])
    data['8'].append(season[8])
    data['9'].append(season[9])
    data['10'].append(season[10])
    data['11'].append(season[11])
    data['12'].append(season[12])
    data['13'].append(season[13])
    data['14'].append(season[14])
    data['15'].append(season[15])
    data['16'].append(season[16])
    data['17'].append(season[17])
    data['18'].append(season[18])
    data['19'].append(season[19])
    data['CareerYear'].append(season[20])
    data['interest'].append(data[str(interest)][interest_count])
    interest_count += 1
    
  src=ColumnDataSource(data)
  return src


#Takes in a dictionary of year:stats, converts it to a ColumnDataSource, each column is year or stat number, rows are years
#Skips the pandas dataframe step
def all_stats_dict_to_src_pitcher(stats, interest):
  data={}
  data['Year'] = list(stats.keys())
  data['0']=[]
  data['1']=[]
  data['2']=[]
  data['3']=[]
  data['4']=[]
  data['5']=[]
  data['6']=[]
  data['7']=[]
  data['8']=[]
  data['9']=[]
  data['10']=[]
  data['11']=[]
  data['12']=[]
  data['13']=[]
  data['14']=[]
  data['15']=[]
  data['16']=[]
  data['17']=[]
  data['18']=[]
  data['19']=[]
  data['20']=[]
  data['21']=[]
  data['22']=[]
  data['23']=[]
  data['24']=[]
  data['25']=[]
  data['26']=[]
  data['CareerYear'] = []
  data['interest'] = []
  interest_count=0
  for season in stats.values():
    data['0'].append(season[0])
    data['1'].append(season[1])
    data['2'].append(season[2])
    data['3'].append(season[3])
    data['4'].append(season[4])
    data['5'].append(season[5])
    data['6'].append(season[6])
    data['7'].append(season[7])
    data['8'].append(season[8])
    data['9'].append(season[9])
    data['10'].append(season[10])
    data['11'].append(season[11])
    data['12'].append(season[12])
    data['13'].append(season[13])
    data['14'].append(season[14])
    data['15'].append(season[15])
    data['16'].append(season[16])
    data['17'].append(season[17])
    data['18'].append(season[18])
    data['19'].append(season[19])
    data['20'].append(season[20])
    data['21'].append(season[21])
    data['22'].append(season[22])
    data['23'].append(season[23])
    data['24'].append(season[24])
    data['25'].append(season[25])
    data['26'].append(season[26])
    data['CareerYear'].append(season[27])
    data['interest'].append(data[str(interest)][interest_count])
    interest_count += 1
  src=ColumnDataSource(data)
  return src

#Plots 1 batter and 1 stat, detailed hover shows year, games, avg, HR, RBI
def plot_1batter_1stat(playerID, stat):
  player_name = playersDict_reverse[playerID]
  stat_name = getBattingStat(stat)
  src = all_stats_dict_to_src_batter(get_batter_all_stats(playerID), stat)
  p=figure(plot_width=800, plot_height=650, title = player_name+' '+stat_name, x_axis_label= "Year", y_axis_label=stat_name)
  circle = p.circle(x='Year', y='interest', source=src, size=8, color='green', alpha=0.8, legend=player_name)
  line = p.line(x='Year', y='interest', source=src, line_width=3, line_color='green')
  
  def update(attr, old, new):
    new_src = all_stats_dict_to_src_batter(get_batter_all_stats(playerID), new+2)
    src.data.update(new_src.data)
    p.title.text=player_name+' '+getBattingStat(new+2)
    p.yaxis.axis_label=getBattingStat(new+2)
    
    if(new+2==2):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))]))
    elif (new+2 == 19):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 9):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))

  stat_selection = RadioGroup(labels=radio_list_batting, active=stat-2)  
  stat_selection.on_change('active', update)

  if(stat==2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))])
  elif (stat == 19):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 9):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])

  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '1 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)

#Plots 1 pitcher and 1 stat, detailed hover shows year, wins, losses, ERA, K's, Saves
def plot_1pitcher_1stat(playerID, stat):
  player_name = playersDict_reverse[playerID]
  stat_name = getPitchingStat(stat)
  src = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID), stat)
  p=figure(plot_width=800, plot_height=650, title = player_name+' '+stat_name, x_axis_label= "Year", y_axis_label=stat_name)
  p.circle(x='Year', y='interest', source=src, size=8, color='green', alpha=0.8, legend=player_name)
  p.line(x='Year', y='interest', source=src, line_width=3, line_color='green') 
  
  
  
  def update(attr, old, new):
    new_src = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID), new+2)
    src.data.update(new_src.data)
    p.title.text=player_name+' '+getPitchingStat(new+2)
    p.yaxis.axis_label=getPitchingStat(new+2)
    
    if(new+2 == 2):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 3):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 16):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))]))
    elif(new+2 == 14):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
  
  stat_selection = RadioGroup(labels=radio_list_pitching, active=stat-2)  
  stat_selection.on_change('active', update)
  
  if(stat == 2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 3):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 16):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))])
  elif(stat == 14):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
        
  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '1 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)

#Plots 2 batters and 1 stat, detailed hover shows year, games, avg, HR, RBI
def plot_2batter_1stat(playerID1, playerID2, stat):
  player1_name = playersDict_reverse[playerID1]
  player2_name = playersDict_reverse[playerID2]
  stat_name = getBattingStat(stat)
  src1 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID1), stat)
  src2 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID2), stat)
  p=figure(plot_width=800, plot_height=650, title = player1_name+' and ' + player2_name+ ' ' + stat_name, x_axis_label= "Year", y_axis_label=stat_name)
  p.circle(x='Year', y='interest', source=src1, size=8, color='green', alpha=0.8, legend=player1_name)
  p.line(x='Year', y='interest', source=src1, line_width=3, line_color='green')
  p.circle(x='Year', y='interest', source=src2, size=8, color='blue', alpha=0.8, legend=player2_name)
  p.line(x='Year', y='interest', source=src2, line_width=3, line_color='blue')
  
  def update(attr, old, new):
    new_src1 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID1), new+2)
    new_src2 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID2), new+2)
    src1.data.update(new_src1.data)
    src2.data.update(new_src2.data)
    p.title.text=player1_name+' and ' + player2_name+ ' ' + getBattingStat(new+2)
    p.yaxis.axis_label=getBattingStat(new+2)
  
    if(new+2==2):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))]))
    elif (new+2 == 19):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 9):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
  
  
  stat_selection = RadioGroup(labels=radio_list_batting, active=stat-2)  
  stat_selection.on_change('active', update)  
  
  if(stat==2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))])
  elif (stat == 19):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 9):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '2 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)

#Plots 2 pitchers and 1 stat, detailed hover shows year, wins, losses, ERA, K's, Saves
def plot_2pitcher_1stat(playerID1, playerID2, stat):
  player1_name = playersDict_reverse[playerID1]
  player2_name = playersDict_reverse[playerID2]
  stat_name = getPitchingStat(stat)
  src1 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID1), stat)
  src2 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID2), stat)
  p=figure(plot_width=800, plot_height=650, title = player1_name+' and ' + player2_name+ ' ' + stat_name, x_axis_label= "Year", y_axis_label=stat_name)
  p.circle(x='Year', y='interest', source=src1, size=8, color='green', alpha=0.8, legend=player1_name)
  p.line(x='Year', y='interest', source=src1, line_width=3, line_color='green') 
  p.circle(x='Year', y='interest', source=src2, size=8, color='blue', alpha=0.8, legend=player2_name)
  p.line(x='Year', y='interest', source=src2, line_width=3, line_color='blue')  
  
  
  def update(attr, old, new):
    new_src1 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID1), new+2)
    new_src2 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID2), new+2)
    src1.data.update(new_src1.data)
    src2.data.update(new_src2.data)
    p.title.text=player1_name+' and ' + player2_name+ ' ' + getPitchingStat(new+2)
    p.yaxis.axis_label=getPitchingStat(new+2)

    
    if(new+2 == 2):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 3):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 16):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))]))
    elif(new+2 == 14):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
  
  stat_selection = RadioGroup(labels=radio_list_pitching, active=stat-2)  
  stat_selection.on_change('active', update)
  
  if(stat == 2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 3):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 16):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))])
  elif(stat == 14):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
        
  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '2 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)


#Plots 2 batters and 1 stat, detailed hover shows year, games, avg, HR, RBI
#Plots by career year rather than absolute year (i.e. year 0 is rookie year)
def plot_2batter_1stat_career(playerID1, playerID2, stat):
  player1_name = playersDict_reverse[playerID1]
  player2_name = playersDict_reverse[playerID2]
  stat_name = getBattingStat(stat)
  src1 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID1), stat)
  src2 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID2), stat)
  p=figure(plot_width=800, plot_height=650, title = player1_name+' and ' + player2_name+ ' ' + stat_name, x_axis_label= "Career Year", y_axis_label=stat_name)
  p.circle(x='CareerYear', y='interest', source=src1, size=8, color='green', alpha=0.8, legend=player1_name)
  p.line(x='CareerYear', y='interest', source=src1, line_width=3, line_color='green')
  p.circle(x='CareerYear', y='interest', source=src2, size=8, color='blue', alpha=0.8, legend=player2_name)
  p.line(x='CareerYear', y='interest', source=src2, line_width=3, line_color='blue')
  
  def update(attr, old, new):
    new_src1 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID1), new+2)
    new_src2 = all_stats_dict_to_src_batter(get_batter_all_stats(playerID2), new+2)
    src1.data.update(new_src1.data)
    src2.data.update(new_src2.data)
    p.title.text=player1_name+' and ' + player2_name+ ' ' + getBattingStat(new+2)
    p.yaxis.axis_label=getBattingStat(new+2)
  
    if(new+2==2):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))]))
    elif (new+2 == 19):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
    elif (new+2 == 9):
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getBattingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))]))
  
  
  stat_selection = RadioGroup(labels=radio_list_batting, active=stat-2)  
  stat_selection.on_change('active', update)  
  
  if(stat==2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9))])
  elif (stat == 19):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  elif (stat == 9):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Avg', '@' + str(19)), ('HR', '@' + str(8)), ('Games', '@' + str(2))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Average', '@' + str(19)), ('HR', '@' + str(8)), ('RBI', '@' + str(9)), ('Games', '@' + str(2))])
  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '2 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)

#Plots 2 pitchers and 1 stat, detailed hover shows year, wins, losses, ERA, K's, Saves
#Plots by career year rather than absolute year (i.e. year 0 is rookie year) 
def plot_2pitcher_1stat_career(playerID1, playerID2, stat):
  player1_name = playersDict_reverse[playerID1]
  player2_name = playersDict_reverse[playerID2]
  stat_name = getPitchingStat(stat)
  src1 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID1), stat)
  src2 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID2), stat)
  p=figure(plot_width=800, plot_height=650, title = player1_name+' and ' + player2_name+ ' ' + stat_name, x_axis_label= "Year", y_axis_label=stat_name)
  p.circle(x='CareerYear', y='interest', source=src1, size=8, color='green', alpha=0.8, legend=player1_name)
  p.line(x='CareerYear', y='interest', source=src1, line_width=3, line_color='green') 
  p.circle(x='CareerYear', y='interest', source=src2, size=8, color='blue', alpha=0.8, legend=player2_name)
  p.line(x='CareerYear', y='interest', source=src2, line_width=3, line_color='blue')  
  
  
  def update(attr, old, new):
    new_src1 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID1), new+2)
    new_src2 = all_stats_dict_to_src_pitcher(get_pitcher_all_stats(playerID2), new+2)
    src1.data.update(new_src1.data)
    src2.data.update(new_src2.data)
    p.title.text=player1_name+' and ' + player2_name+ ' ' + getPitchingStat(new+2)
    p.yaxis.axis_label=getPitchingStat(new+2)

    
    if(new+2 == 2):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 3):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 16):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
    elif(new+2 == 8):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))]))
    elif(new+2 == 14):
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))]))
    else:
      p.add_tools(HoverTool(tooltips=[(getPitchingStat(new+2),'@' + str(new+2)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))]))
  
  stat_selection = RadioGroup(labels=radio_list_pitching, active=stat-2)  
  stat_selection.on_change('active', update)
  
  if(stat == 2):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 3):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 16):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
  elif(stat == 8):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14))])
  elif(stat == 14):
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Saves', '@' + str(8))])
  else:
    hover = HoverTool(tooltips=[(stat_name,'@' + str(stat)), ('Year', '@Year'), ('Wins', '@' + str(2)), ('Losses', '@' + str(3)), ('ERA', '@' + str(16)), ('Strikeouts', '@' + str(14)), ('Saves', '@' + str(8))])
        
  p.add_tools(hover)
  controls = WidgetBox(stat_selection)
  layout = row(controls, p)
  tab = Panel(child=layout, title = '2 Player Stats')
  tabs = Tabs(tabs=[tab])
  curdoc().add_root(tabs)
  



def load_data():
  #fills playersDict{} and playersDict_reverse{}
  with open('People.csv', mode='r') as batting_info:
    reader=csv.DictReader(batting_info)
    for row in reader:
      playersDict[(row['nameLast'], row['nameFirst'], row['debut'])] = row['playerID']
      playersDict_reverse[row['playerID']]=row['nameFirst'] + ' ' + row['nameLast']


  #fills battersAllStats{}
  with open ('completeBattingNoStints.csv', mode='r') as batter_stats:
    reader=csv.DictReader(batter_stats)
    for row in reader:
      battersAllStats[row['playerID'], int(row['yearID'])] = (row['teamID'], row['lgID'], iint(row['G']), iint(row['AB']), iint(row['R']), iint(row['H']), iint(row['2B']), iint(row['3B']), iint(row['HR']), iint(row['RBI']), iint(row['SB']), iint(row['CS']), iint(row['BB']), iint(row['SO']), iint(row['IBB']), iint(row['HBP']), iint(row['SH']), iint(row['SF']), iint(row['GIDP']), iint(row['H'])/noZero(row['AB']))

  #fills pitchersAllStats{}
  with open('completePitchingNoStints.csv', mode='r') as pitcher_stats:
    reader=csv.DictReader(pitcher_stats)
    for row in reader:
      pitchersAllStats[row['playerID'], int(row['yearID'])] = (row['teamID'], row['lgID'], iint(row['W']), iint(row['L']), iint(row['G']), iint(row['GS']), iint(row['CG']), iint(row['SHO']), iint(row['SV']), iint(row['IPouts']), iint(row['H']), iint(row['ER']), iint(row['HR']), iint(row['BB']), iint(row['SO']), ffloat(row['BAOpp']), ffloat(row['ERA']), iint(row['IBB']), iint(row['WP']), iint(row['HBP']), iint(row['BK']), iint(row['BFP']), iint(row['GF']), iint(row['R']), iint(row['SH']), iint(row['SF']), iint(row['GIDP']))

  #fills playersYearToYear{}
  with open ('player_year_year.csv', mode='r') as player_years:
    reader=csv.DictReader(player_years)
    for row in reader:
      playersYearToYear[(row['playerID'], int(row['year']))] = int(row['careerYear'])



def one_batter_script():
  fn1=input("Enter the Player1's first name: ")
  ln1=input("Enter the Player1's last name: ")
  playerID1=search_for_player(ln1, fn1)
  while playerID1 == None:
    fn1=input("Enter the Player1's first name: ")
    ln1=input("Enter the Player1's last name: ")
    playerID1=search_for_player(ln1, fn1)
  playerID1=playerID1[0]
  printBattingStats()
  stat=int(input("What stat do you want to view? (2-19) "))
  plot_1batter_1stat(playerID1, stat)
  
def one_pitcher_script():
  fn1=input("Enter the Player1's first name: ")
  ln1=input("Enter the Player1's last name: ")
  playerID1=search_for_player(ln1, fn1)
  while playerID1 == None:
    fn1=input("Enter the Player1's first name: ")
    ln1=input("Enter the Player1's last name: ")
    playerID1=search_for_player(ln1, fn1)
  playerID1=playerID1[0]
  printPitchingStats()
  stat=int(input("What stat do you want to view? (2-16) "))
  plot_1pitcher_1stat(playerID1, stat) 
  

def two_batters_script():
  fn1=input("Enter the Player1's first name: ")
  ln1=input("Enter the Player1's last name: ")
  playerID1=search_for_player(ln1, fn1)
  while playerID1 == None:
    fn1=input("Enter the Player1's first name: ")
    ln1=input("Enter the Player1's last name: ")
    playerID1=search_for_player(ln1, fn1)
  playerID1=playerID1[0]
  fn2=input("Enter the Player2's first name: ")
  ln2=input("Enter the Player2's last name: ")
  playerID2=search_for_player(ln2, fn2)
  playerID2=playerID2
  while playerID2 == None:
    fn2=input("Enter the Player2's first name: ")
    ln2=input("Enter the Player2's last name: ")
    playerID2=search_for_player(ln2, fn2)
  playerID2=playerID2[0]
  printBattingStats()
  stat=int(input("What stat do you want to view? (2-19) "))
  format=input("Would you like to compare by absolute year (A/a) or career year(C/c)")
  if format == 'A' or format == 'a':
    plot_2batter_1stat(playerID1, playerID2, stat)
  elif format == 'C' or format == 'c':
    plot_2batter_1stat_career(playerID1, playerID2, stat)

def two_pitchers_script():
  fn1=input("Enter the Player1's first name: ")
  ln1=input("Enter the Player1's last name: ")
  playerID1=search_for_player(ln1, fn1)
  while playerID1 == None:
    fn1=input("Enter the Player1's first name: ")
    ln1=input("Enter the Player1's last name: ")
    playerID1=search_for_player(ln1, fn1)
  playerID1=playerID1[0]
  fn2=input("Enter the Player2's first name: ")
  ln2=input("Enter the Player2's last name: ")
  playerID2=search_for_player(ln2, fn2)
  playerID2=playerID2
  while playerID2 == None:
    fn2=input("Enter the Player2's first name: ")
    ln2=input("Enter the Player2's last name: ")
    playerID2=search_for_player(ln2, fn2)
  playerID2=playerID2[0]
  printPitchingStats()
  stat=int(input("What stat do you want to view? (2-25) "))
  format=input("Would you like to compare by absolute year (A/a) or career year(C/c)")
  if format == 'A' or format == 'a':
    plot_2pitcher_1stat(playerID1, playerID2, stat)
  elif format == 'C' or format == 'c':
    plot_2pitcher_1stat_career(playerID1, playerID2, stat)
    




load_data()
b_or_p = input ("Batters (B/b) or Pitchers (P/p)?")
if b_or_p == 'b' or b_or_p == 'B':
  num_players = input("1 or 2 players?")
  if num_players == "1":
    one_batter_script()
  elif num_players == "2":
    two_batters_script()
elif b_or_p == 'p' or b_or_p == 'P':
  num_players = input("1 or 2 players?")
  if num_players == "1":
    one_pitcher_script()
  elif num_players == "2":
    two_pitchers_script()

   
