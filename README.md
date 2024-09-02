# Theoretical-SF-cost-calculator
A calculator for the theoretical cost of starforcing in maplestory

To download, go to downloads and find latest stable version and download.

To run, double click the .exe file which will start the calculator. Input item level, current or starting star, and target star along with any events you wish to apply. Then, hit calculate.

The expected value given is not the exact amount it will take, but the amount each item would cost on average across multiple items with those configurations.
The expected number of booms is the same.
The probability of not booming P(no boom) is used to make a distribution of the probability of each number of booms occurring. 
    To get the percent probability, multiply by 100. Ex. if P(no boom) = .10, the the probability of not booming is 10%
    To build the distribution, copy the number and navigate to https://homepage.divms.uiowa.edu/~mbognar/applets/geo1.html paste your number into "p=" and a chart will be built. If you wish to get the probability of a specific number of booms, select P(X=x) and enter a number into "x=". Ex. p=.1, x=1, P(X=x) will show you the distribution with 1 highlighted and .09 (9%) in the box next to P(X=x). This means there is a 9% chance of booming exactly 1 time with a p value of .1