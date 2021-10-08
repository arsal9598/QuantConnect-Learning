"""
My own custom code I'm using to learn QuantConnect, find my mistakes, and develop algos
This code isn't complete, I'm trying to code a strategy that buys 20 most volatile stocks at 9:45am
if SPY is above yesterday's close. And then sell at 3:45pm. Not working yet, have a lot to figure out
"""
class EmotionalFluorescentPinkSalmon(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2021, 11, 1)
        self.SetCash(100000)
        
        self.tickers = {}
        self.symbols = ["AMZN", "MSFT", "AAPL"]
        
        for symbol in self.symbols[:2]:
            self.tickers[symbol] = 3.5
        
        self.portfolio_targets = []
        
        for stock, atr in self.tickers.items():
            if atr > 3:
                self.stock = self.AddEquity(stock, Resolution.Minute).Symbol
                self.portfolio_targets.append(self.stock)
                
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol
        self.SetWarmUp(1, Resolution.Daily)
        self.yest_close = self.SMA(self.spy, 1, Resolution.Daily, Field.Close)
        
        """
        Figure out universe selection error
        """
            
    def OnData(self, data):
        
        if self.IsWarmingUp or not self.yest_close.IsReady or not len(data.Bars) > 0: 
            return 
        
        # If SPY is above yesterday's close at 9:45, go long all stocks in ticker_symbols
        if self.Time.hour == 9 and self.Time.minute == 45:
            for stock in self.portfolio_targets:
                price = self.Securities[self.spy].Price
                yest_close = self.yest_close.Current.Value
            
                if price > yest_close:
                    self.SetHoldings(stock, 1/len(self.portfolio_targets))
        
        if self.Time.hour == 15 and self.Time.minute == 45:
            self.Liquidate()
