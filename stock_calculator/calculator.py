def calculate_stock_metrics(stock_price, amount, transaction_fee, percent_change=None):
    """
    Calculate break-even price, total investment, and optional profit/loss.

    Args:
        stock_price (float): Price per stock when buying
        amount (int): Number of stocks purchased
        transaction_fee (float): Transaction fee per trade (applies to buy and sell)
        percent_change (float, optional): Percent change applied to the stock price (-100 to 100)

    Returns:
        dict: {
            "break_even_price": float,
            "total_invested": float,
            "target_price": float or None,
            "profit_loss": float or None
        }
    """
    total_invested = stock_price * amount + transaction_fee
    break_even_price = (stock_price * amount + 2 * transaction_fee) / amount

    target_price = None
    profit_loss = None

    if percent_change is not None:
        target_price = stock_price * (1 + percent_change / 100)
        sell_value = target_price * amount - transaction_fee
        profit_loss = sell_value - total_invested

    return {
        "break_even_price": break_even_price,
        "total_invested": total_invested,
        "target_price": target_price,
        "profit_loss": profit_loss
    }
