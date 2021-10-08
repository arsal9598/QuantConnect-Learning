"""
Exploring Quantconnect universe selection and filtering
Buying and holding stocks of a current dollar volume an PE ratio
"""

class LogicalRedOrangeCrocodile(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2005, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000) 
        
        self.reBalanceTime = datetime.min
        self.activeStocks = set()
        
        self.AddUniverse(self.CoarseFilter, self.FineFilter)
        self.UniverseSettings.Resolution = Resolution.Hour
        
        self.portfolioTargets = []
        
    def CoarseFilter(self, coarse):
        if self.Time <= self.reBalanceTime:
            return self.Universe.Unchanged
                
        self.reBalanceTime = self.Time + timedelta(30)
        sortedByDollarVolume = sorted(coarse, key = lambda x: x.DollarVolume, reverse = True)
        return [x.Symbol for x in sortedByDollarVolume if x.Price > 10 and x.HasFundamentalData][:200]
        
    def FineFilter(self, fine):
        sortedByPE = sorted(fine, key=lambda x: x.MarketCap)
        return [x.Symbol for x in sortedByPE if x.MarketCap > 0][:10]
        
    def OnSecuritiesChanged(self, changes):
        for x in changes.RemovedSecurities:
            self.Liquidate(x.Symbol)
            self.activeStocks.remove(x.Symbol)
            
        for x in changes.AddedSecurities:
            self.activeStocks.add(x.Symbol)
            
        self.portfolioTargets = [PortfolioTarget(symbol, 1/len(self.activeStocks)) for symbol in self.activeStocks]

    def OnData(self, data):
        if self.portfolioTargets == []:
            return
        
        for symbol in self.activeStocks:
            if symbol not in data:
                return
        if self.Time.hour == "9" and self.Time.minute == 45:
            self.SetHoldings(self.portfolioTargets)
            self.portfolioTargets = []
