from pyalgotrade import strategy
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.barfeed import yahoofeed


class BBands(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)

    def getBollingerBands(self):
        return self.__bbands

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        if shares == 0 and bar.getClose() < lower:
            sharesToBuy = int(self.getBroker().getEquity() * 0.2 / bars[self.__instrument].getPrice())
            self.marketOrder(self.__instrument, sharesToBuy)
            self.info("buy %s" % (bars.getDateTime()))
            self.info("at buy %s" % (bar.getClose()))
        elif shares > 0 and bar.getClose() > upper:
            self.marketOrder(self.__instrument, -1*shares)
            self.info("sell %s" % (bars.getDateTime()))
            self.info("at sell %s" % (bar.getClose()))
        
def main(plot):
    from pyalgotrade import bar
    from pyalgotrade import plotter
    instrument = "002665"
    bBandsPeriod = 40
    strat= BBands
    frequency=bar.Frequency.DAY
    plot = True

    # Download the bars.
    from pyalgotrade.barfeed.csvfeed import GenericBarFeed
    barfeed=GenericBarFeed(frequency)
    barfeed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')
    barfeed.addBarsFromCSV("002665","F:/shuju/002665-barfeed.csv")
    strat = strat(barfeed,instrument,bBandsPeriod)

    strat = BBands(barfeed, instrument, bBandsPeriod)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    
    if plot:
           
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("upper", strat.getBollingerBands().getUpperBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("middle", strat.getBollingerBands().getMiddleBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("lower", strat.getBollingerBands().getLowerBand())

    strat.run()
    print ("Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05))

    if plot:
        
        plt.plot()


if __name__ == "__main__":
    main(True)
