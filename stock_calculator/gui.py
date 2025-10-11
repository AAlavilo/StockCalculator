import tkinter as tk
from stock_calculator.calculator import break_even_price

def run_gui():
    def calculate():
        try:
            price = float(entry_price.get())
            amount = int(entry_amount.get())
            fee = float(entry_fee.get())
            target = break_even_price(price, amount, fee)
            result_label.config(text=f"Break-even price: ${target:.2f}")
        except ValueError:
            result_label.config(text="Please enter valid numbers.")

    window = tk.Tk()
    window.title("Stock Break-Even Calculator")

    tk.Label(window, text="Stock Price:").grid(row=0, column=0)
    entry_price = tk.Entry(window)
    entry_price.grid(row=0, column=1)

    tk.Label(window, text="Number of Stocks:").grid(row=1, column=0)
    entry_amount = tk.Entry(window)
    entry_amount.grid(row=1, column=1)

    tk.Label(window, text="Transaction Fees:").grid(row=2, column=0)
    entry_fee = tk.Entry(window)
    entry_fee.grid(row=2, column=1)

    tk.Button(window, text="Calculate", command=calculate).grid(row=3, column=0, columnspan=2)

    result_label = tk.Label(window, text="")
    result_label.grid(row=4, column=0, columnspan=2)

    window.mainloop()
