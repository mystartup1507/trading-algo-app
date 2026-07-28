from account import account_service


class RiskCalculator:

    DEFAULT_RISK_PERCENT = 2.0

    def calculate(self, risk_percent=None):

        if risk_percent is None:
            risk_percent = self.DEFAULT_RISK_PERCENT

        account = account_service.get_account_info()

        if not account["success"]:
            return account

        balance = account["data"]["balance"]

        max_risk_amount = balance * (risk_percent / 100)

        return {
            "success": True,
            "message": "Risk calculated successfully.",
            "data": {
                "balance": round(balance, 2),
                "risk_percent": risk_percent,
                "max_risk_amount": round(max_risk_amount, 2)
            }
        }


risk_calculator = RiskCalculator()