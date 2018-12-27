# baseballvis
A  visualization for baseball player statistics

This program allows you to graphically view statistics from one or two MLB players. 
Statistics are available from between 1870 and 2017.
This program uses Bokeh for data visualization in Python.

To use the program:
1. Run the server. In the command line type: bokeh serve --show main.py
2. Follow the prompts on the command line: choose batters or pitchers, 1 or 2 players, choose the players, default statistic, and year type
3. View graph in browser
4. Manipulate/interact with graph
5. To change players, restart the server


If you are unfamiliar with baseball players, try using Barry Bonds and Hank Aarom as Player 1 and Player 2

For choosing the statistic to view, make sure to type the corresponding number i.e. type 8 to view Home Runs (don't type "Home Runs").


Absolute year plots the players' statistics by the true year on the X axis (i.e. 1983)
Career year plots the players' statistics by sequential years in their careers beginning at 0 for the players' rookie year.
Career year allows for a feasible comparison of players from different time periods.
