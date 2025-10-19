# stock_calculator/gui/calculator.py

class StockCalculator:
    """
    Object-oriented stock calculator responsible for all financial logic.
    Keeps the GUI clean and focused only on display.
    """

    def __init__(self, stock_price: float, shares: int, transaction_fee: float):
        self.stock_price = stock_price
        self.shares = shares
        self.transaction_fee = transaction_fee

    # --- BASE VALUES ---

    @property
    def total_invested(self) -> float:
        """Total money spent when buying (including buy-side transaction fee)."""
        return self.stock_price * self.shares + self.transaction_fee

    @property
    def break_even_price(self) -> float:
        """Per-stock price required to break even after paying sell-side fee too."""
        return (self.stock_price * self.shares + 2 * self.transaction_fee) / self.shares

    @property
    def percent_increase_to_break_even(self) -> float:
        """How much the price must increase (%) from initial cost to break even."""
        return ((self.break_even_price - self.stock_price) / self.stock_price) * 100

    # --- PROFIT/LOSS AT GIVEN % ---

    def profit_at(self, percent_change: float) -> dict:
        """
        Returns what your P/L would be IF the stock moved by given percent.
        Useful for the slider functionality.
        """
        target_price = self.stock_price * (1 + percent_change / 100)
        sell_value = target_price * self.shares - self.transaction_fee
        profit_loss = sell_value - self.total_invested
        return {
            "target_price": target_price,
            "profit_loss": profit_loss
        }

    # --- PACKED RESULT ---

    def as_dict(self, percent_change: float | None = None) -> dict:
        """Return all results in dictionary form."""
        results = {
            "total_invested": self.total_invested,
            "break_even_price": self.break_even_price,
            "percent_increase_to_break_even": self.percent_increase_to_break_even,
        }
        if percent_change is not None:
            results.update(self.profit_at(percent_change))
        return results
