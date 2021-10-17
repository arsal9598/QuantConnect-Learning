"""
Simple algorithm to learn about crypto algos, 
Buys if RSI goes above 70 and sells if it drops below 60
Has to meet minimum volume thresholds
Note this algorithm is vulnerable to survivorship bias

"""
class MeasuredFluorescentPinkParrot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        
        self.Settings.FreePortfolioValuePercentage = 0.05
        self.positionSizeUSD = 5000
        self.rsiEntryThreshold = 70
        self.rsiExitThreshold = 60
        self.minimumVolume = 1000000
        
        universe = ['BTCUSD', 'LTCUSD', 'ETHUSD', 'ETCUSD', 'RRTUSD', 'ZECUSD', 'XMRUSD', 'XRPUSD', 'EOSUSD', 'SANUSD', 'OMGUSD', 'NEOUSD', 'ETPUSD', 'BTGUSD', 'SNTUSD', 'BATUSD', 'FUNUSD', 'ZRXUSD', 'TRXUSD', 'REQUSD', 'LRCUSD', 'WAXUSD', 'DAIUSD', 'BFTUSD', 'ODEUSD', 'ANTUSD', 'XLMUSD', 'XVGUSD', 'MKRUSD', 'KNCUSD', 'LYMUSD', 'UTKUSD', 'VEEUSD', 'ESSUSD', 'IQXUSD', 'ZILUSD', 'BNTUSD', 'XRAUSD', 'VETUSD', 'GOTUSD', 'XTZUSD', 'MLNUSD', 'PNKUSD', 'DGBUSD', 'BSVUSD', 'ENJUSD', 'PAXUSD']
        
        self.pairs = [Pair(self, ticker, self.minimumVolume) for ticker in universe]
        self.SetBenchmark("BTCUSD")
        self.SetWarmUp(30)


    def OnData(self, data):
        for pair in self.pairs:
            if not pair.rsi.IsReady:
                return
            symbol = pair.symbol
            rsi = pair.rsi.Current.Value
            
            if self.Portfolio[symbol].Invested:
                if not pair.Investable():
                    self.Liquidate(symbol, "Not enough volume")
                elif rsi < self.rsiExitThreshold:
                    self.Liquidate(symbol, "RSI below threshold")
                continue
            if not pair.Investable():
                continue
            if rsi > self.rsiEntryThreshold and self.Portfolio.MarginRemaining > self.positionSizeUSD:
                self.Buy(symbol, self.positionSizeUSD / self.Securities[symbol].Price)
   
    
class Pair:
    def __init__(self, algorithm, ticker, minimumVolume):
        self.symbol = algorithm.AddCrypto(ticker, Resolution.Daily, Market.Bitfinex).Symbol
        self.rsi = algorithm.RSI(self.symbol, 14, MovingAverageType.Simple, Resolution.Daily)
        self.volume = IndicatorExtensions.Times(
            algorithm.SMA(self.symbol, 30, Resolution.Daily, Field.Volume),
            algorithm.SMA(self.symbol, 30, Resolution.Daily, Field.Close))
        self.minimumVolume = minimumVolume
    def Investable(self):
        return (self.volume.Current.Value > self.minimumVolume)
            
            
            
            
            
