"""
Buy 20 stocks showing strength vs SPY. Buy them. Liquidate at EOD

"""
import pandas as pd

class JumpingLightBrownScorpion(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetCash(100000) # Set Cash
        
        self.stocks = ["AAPL", "MSFT", "COTY", "GE"] # stocks I'm interested in
            
        # Dictionary to hold Symbol Data
        self.symbolData = {}

        for stock in self.stocks:
            # Add equity data
            symbol = self.AddEquity(stock, Resolution.Daily).Symbol
            # Create symbol data for respective symbol
            self.symbolData[symbol] = SymbolData(self, symbol)
        
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol # intialize SPY
        self.SetWarmUp(200, Resolution.Daily) # warm up indicators
        self.yest_close = self.SMA(self.spy, 1, Resolution.Daily, Field.Close) # set SMA with close price as field
        
        

    def OnData(self, data):
        if self.IsWarmingUp or not self.yest_close.IsReady or not len(data.Bars) > 0: # if indicators warming up, not ready, or no data bars then stop
            return
        
        if self.Time.hour == 9 and self.Time.minute == 45: # if it's 9:45am eastern
            price = self.Securities[self.spy].Price        # set price to SPYs price
            yest_close = self.yest_close.Current.Value     # set yesterday's closing price to variable
            
            if price < yest_close:# If SPY fell from yesterday, invest in stocks that are up from yesterday
                selected = []
                for symbol, value in self.symbolData.items():
                    value = value.id
                    if self.Securities[symbol].Price > float(str(value).strip()):
                        selected.append(symbol)
                for stock in selected:
                    self.SetHoldings(stock,1/len(selected))
                
                        
        if self.Time.hour == 15 and self.Time.minute == 45: # if it's 3:45pm eastern, liquidate portfolio
            self.Liquidate()
            
class SymbolData:
    
    def __init__(self, algorithm, symbol):
        self.algorithm = algorithm
        self.symbol = symbol
        self.id = algorithm.Identity(self.symbol, Resolution.Daily, Field.Close)
        
        # Warm up Identity, since it should be using 2-day-prior close price
        history = algorithm.History(self.symbol, 2, Resolution.Daily).iloc[0]
        self.id.Update(pd.to_datetime(history.name[1]), history.close)
        
