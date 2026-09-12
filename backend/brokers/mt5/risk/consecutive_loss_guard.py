class ConsecutiveLossGuard:

    # =====================================================
    # Maximum allowed consecutive losses
    # =====================================================

    MAX_CONSECUTIVE_LOSSES = 3

    def __init__(self):

        self._loss_count = 0

    # =====================================================

    def record_win(self):

        self._loss_count = 0

    # =====================================================

    def record_loss(self):

        self._loss_count += 1

    # =====================================================

    def reset(self):

        self._loss_count = 0

    # =====================================================

    def status(self):

        return {
            "loss_count": self._loss_count,
            "maximum_losses": self.MAX_CONSECUTIVE_LOSSES
        }

    # =====================================================

    def validate(self):

        if self._loss_count >= self.MAX_CONSECUTIVE_LOSSES:

            return {
                "success": False,
                "message": "Maximum consecutive losses reached.",
                "data": {
                    "allowed": False,
                    "loss_count": self._loss_count,
                    "maximum_losses": self.MAX_CONSECUTIVE_LOSSES
                }
            }

        return {
            "success": True,
            "message": "Consecutive loss validation passed.",
            "data": {
                "allowed": True,
                "loss_count": self._loss_count,
                "maximum_losses": self.MAX_CONSECUTIVE_LOSSES,
                "remaining_losses": (
                    self.MAX_CONSECUTIVE_LOSSES
                    - self._loss_count
                )
            }
        }


consecutive_loss_guard = ConsecutiveLossGuard()