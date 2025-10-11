import customtkinter as ctk
from stock_calculator.calculator import calculate_stock_metrics

def run_gui():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("📈 Stock Break-Even Calculator")
    app.geometry("450x420")

    title = ctk.CTkLabel(app, text="📊 Stock Break-Even Calculator", font=("Arial", 18, "bold"))
    title.pack(pady=15)

    entry_price = ctk.CTkEntry(app, placeholder_text="Stock price (€)")
    entry_price.pack(pady=5)

    entry_amount = ctk.CTkEntry(app, placeholder_text="Number of stocks")
    entry_amount.pack(pady=5)

    entry_fee = ctk.CTkEntry(app, placeholder_text="Transaction fee (€ per trade)")
    entry_fee.pack(pady=5)

    # Labels for results
    result_label = ctk.CTkLabel(app, text="", font=("Arial", 14), justify="left")
    result_label.pack(pady=10)

    slider_label = ctk.CTkLabel(app, text="Earnings %: 0%", font=("Arial", 14))
    slider_label.pack(pady=5)

    # Slider for percentage adjustment
    slider = ctk.CTkSlider(app, from_=-100, to=100, number_of_steps=20000)
    slider.pack(fill="x", padx=40, pady=5)

    profit_label = ctk.CTkLabel(app, text="", font=("Arial", 14), justify="left")
    profit_label.pack(pady=5)

    def calculate():
        """
        Calculate and display break-even price and total investment.
        """
        try:
            price = float(entry_price.get().replace(',', '.'))
            amount = int(entry_amount.get())
            fee = float(entry_fee.get())

            metrics = calculate_stock_metrics(price, amount, fee)
            break_even = metrics["break_even_price"]
            total_invested = metrics["total_invested"]
            percent_increase = ((break_even - price) / price) * 100

            result_label.configure(
                text=(
                    f"💰 Total invested: {total_invested:.2f}€\n"
                    f"📊 Break-even price: {break_even:.2f}€\n"
                    f"📈 Required increase: {percent_increase:.2f}%"
                )
            )

            # Reset profit display
            update_profit()
        except ValueError:
            result_label.configure(text="⚠️ Please enter valid numbers.")

    def update_profit(event=None):
        """Updates profit/loss dynamically when the slider moves."""
        try:
            price = float(entry_price.get())
            amount = int(entry_amount.get())
            fee = float(entry_fee.get())
            percent = slider.get()

            slider_label.configure(text=f"Earnings %: {percent:.2f}%")

            metrics = calculate_stock_metrics(price, amount, fee, percent)
            if metrics["profit_loss"] is not None:
                profit = metrics["profit_loss"]
                target = metrics["target_price"]

                color = "green" if profit > 0 else "red" if profit < 0 else "gray"
                profit_label.configure(
                    text=(
                        f"🎯 Target price: €{target:.2f}\n"
                        f"💵 Profit/Loss: {'+' if profit > 0 else ''}{profit:.2f}€"
                    ),
                    text_color=color
                )
        except ValueError:
            profit_label.configure(text="")

    # Bind slider movement to profit update
    slider.configure(command=update_profit)

    calc_button = ctk.CTkButton(app, text="Calculate", command=calculate)
    calc_button.pack(pady=10)

    app.mainloop()
