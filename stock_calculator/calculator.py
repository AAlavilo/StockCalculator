def break_even_price(stock_price, amount, transaction_fee):
    """
    Calculate the minimum price increase needed to break even.

    Args:
        stock_price (float): Price of a single stock
        amount (int): Number of stocks
        transaction_fee (float): Total transaction fees

    Returns:
        float: Minimum price the stock needs to reach to break even
    """
    total_cost = stock_price * amount + transaction_fee
    break_even = total_cost / amount
    return break_even