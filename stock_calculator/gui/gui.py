import customtkinter as ctk
from stock_calculator.utils.calculator import calculate_stock_metrics
from stock_calculator.database import init_db, add_stock, get_all_stocks, get_db_path

# Helper to parse user input (supports commas)
def parse_number(value: str, default=0.0):
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return default

def run_gui():
    init_db()
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("📈 Stock Tracker")
    app.geometry("800x500")

    # --- Layout: Sidebar + Main Frame ---
    sidebar = ctk.CTkFrame(app, width=150, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    main_frame = ctk.CTkFrame(app)
    main_frame.pack(side="right", expand=True, fill="both")

    # Frames for each tab
    calculator_tab = ctk.CTkFrame(main_frame)
    database_tab = ctk.CTkFrame(main_frame)

    for f in (calculator_tab, database_tab):
        f.place(relx=0, rely=0, relwidth=1, relheight=1)

    # --- Sidebar Buttons ---
    def show_frame(frame):
        frame.tkraise()

    calc_btn = ctk.CTkButton(sidebar, text="Calculator", command=lambda: show_frame(calculator_tab))
    calc_btn.pack(pady=20, padx=10)

    db_btn = ctk.CTkButton(sidebar, text="My Stocks", command=lambda: show_frame(database_tab))
    db_btn.pack(pady=10, padx=10)

    # ------------------------------------------------
    # TAB 1: CALCULATOR
    # ------------------------------------------------
    title = ctk.CTkLabel(calculator_tab, text="📊 Stock Break-Even Calculator", font=("Arial", 18, "bold"))
    title.pack(pady=15)

    entry_price = ctk.CTkEntry(calculator_tab, placeholder_text="Stock price (€)")
    entry_price.pack(pady=5)

    entry_amount = ctk.CTkEntry(calculator_tab, placeholder_text="Number of stocks")
    entry_amount.pack(pady=5)

    entry_fee = ctk.CTkEntry(calculator_tab, placeholder_text="Transaction fee (€ per trade)")
    entry_fee.pack(pady=5)

    entry_ticker = ctk.CTkEntry(calculator_tab, placeholder_text="Ticker symbol (optional)")
    entry_ticker.pack(pady=5)

    result_label = ctk.CTkLabel(calculator_tab, text="", font=("Arial", 14), justify="left")
    result_label.pack(pady=10)

    slider_label = ctk.CTkLabel(calculator_tab, text="Earnings %: 0.00%", font=("Arial", 14))
    slider_label.pack(pady=5)

    slider = ctk.CTkSlider(calculator_tab, from_=-100, to=100, number_of_steps=2000)
    slider.pack(fill="x", padx=40, pady=5)

    profit_label = ctk.CTkLabel(calculator_tab, text="", font=("Arial", 14))
    profit_label.pack(pady=5)

    def calculate():
        price = parse_number(entry_price.get())
        amount = int(parse_number(entry_amount.get()))
        fee = parse_number(entry_fee.get())

        metrics = calculate_stock_metrics(price, amount, fee)
        break_even = metrics["break_even_price"]
        total_invested = metrics["total_invested"]
        percent_increase = ((break_even - price) / price) * 100

        result_label.configure(
            text=(
                f"💰 Total invested: €{total_invested:.2f}\n"
                f"📊 Break-even price: €{break_even:.2f}\n"
                f"📈 Required increase: {percent_increase:.2f}%"
            )
        )

        # Save to DB if ticker provided
        ticker = entry_ticker.get().strip()
        if ticker:
            add_stock(ticker, price, amount, break_even)
            load_stocks()

        update_profit()

    def update_profit(event=None):
        price = parse_number(entry_price.get())
        amount = int(parse_number(entry_amount.get()))
        fee = parse_number(entry_fee.get())
        percent = slider.get()

        slider_label.configure(text=f"Earnings %: {percent:.2f}%")

        metrics = calculate_stock_metrics(price, amount, fee, percent)
        profit = metrics["profit_loss"]
        target = metrics["target_price"]

        if profit is not None:
            color = "green" if profit > 0 else "red" if profit < 0 else "gray"
            profit_label.configure(
                text=(
                    f"🎯 Target price: €{target:.2f}\n"
                    f"💵 Profit/Loss: {'+' if profit > 0 else ''}{profit:.2f}€"
                ),
                text_color=color
            )

    slider.configure(command=update_profit)
    calc_button = ctk.CTkButton(calculator_tab, text="Calculate / Save", command=calculate)
    calc_button.pack(pady=15)

    # ------------------------------------------------
    # TAB 2: DATABASE
    # ------------------------------------------------
    db_title = ctk.CTkLabel(database_tab, text="📚 My Saved Stocks", font=("Arial", 18, "bold"))
    db_title.pack(pady=10)
    db_path_label = ctk.CTkLabel(
        database_tab,
        text=f"Database: {get_db_path()}",
        font=("Arial", 10),
        text_color="gray"
    )
    db_path_label.pack(pady=5)

    stock_box = ctk.CTkTextbox(database_tab, width=600, height=350)
    stock_box.pack(pady=10)

    def load_stocks():
        rows = get_all_stocks()
        stock_box.delete("1.0", "end")
        if not rows:
            stock_box.insert("end", "No saved stocks yet.\n")
            return
        stock_box.insert("end", f"{'Ticker':<10}{'Buy Price':<15}{'Shares':<10}{'Break-Even':<15}\n")
        stock_box.insert("end", "-"*50 + "\n")
        for t, p, s, b in rows:
            stock_box.insert("end", f"{t:<10}{p:<15.2f}{s:<10}{b:<15.2f}\n")

    refresh_button = ctk.CTkButton(database_tab, text="🔄 Refresh", command=load_stocks)
    refresh_button.pack(pady=10)

    load_stocks()  # Load on start
    show_frame(calculator_tab)  # Default tab

    app.mainloop()
