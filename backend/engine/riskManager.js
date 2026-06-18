class RiskManager {

  constructor() {
    this.maxTradesPerDay = 5;
    this.maxDailyLoss = 2000;
    this.maxRiskPerTrade = 1;
    this.trailingSL = true;
  }

  validateTrade(account, trade) {

    if (account.dailyTrades >= this.maxTradesPerDay) {
      return {
        allowed: false,
        reason: "Maximum daily trades reached"
      };
    }

    if (account.dailyLoss >= this.maxDailyLoss) {
      return {
        allowed: false,
        reason: "Maximum daily loss reached"
      };
    }

    return {
      allowed: true
    };

  }

}

module.exports = new RiskManager();
