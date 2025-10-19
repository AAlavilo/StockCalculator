import customtkinter as ctk
from tkinter import ttk
from stock_calculator.utils.calculator import StockCalculator
from stock_calculator.database import init_db, add_stock, get_all_stocks, move_to_history, get_history, get_db_path

# --- Helper to parse user input (supports commas) ---
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
    app.geometry("900x550")

    # --- Sidebar + Main Frame ---
    sidebar = ctk.CTkFrame(app, width=150, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    main_frame = ctk.CTkFrame(app)
    main_frame.pack(side="right", expand=True, fill="both")

    # --- Frames for each tab ---
    calculator_tab = ctk.CTkFrame(main_frame)
    mystocks_tab = ctk.CTkFrame(main_frame)
    history_tab = ctk.CTkFrame(main_frame)

    for f in (calculator_tab, mystocks_tab, history_tab):
        f.place(relx=0, rely=0, relwidth=1, relheight=1)

    # --- Sidebar Buttons ---
    def show_frame(frame):
        frame.tkraise()

    ctk.CTkButton(sidebar, text="Calculator", command=lambda: show_frame(calculator_tab)).pack(pady=20, padx=10)
    ctk.CTkButton(sidebar, text="My Stocks", command=lambda: show_frame(mystocks_tab)).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="History", command=lambda: show_frame(history_tab)).pack(pady=10, padx=10)

    # -----------------------
    # Calculator Tab
    # -----------------------
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

    current_calc = None  # Store StockCalculator instance

    def calculate():
        nonlocal current_calc
        price = parse_number(entry_price.get())
        amount = int(parse_number(entry_amount.get()))
        fee = parse_number(entry_fee.get())

        current_calc = StockCalculator(price, amount, fee)
        metrics = current_calc.as_dict()
        break_even = metrics["break_even_price"]
        total_invested = metrics["total_invested"]
        required_percent = metrics["percent_increase_to_break_even"]

        result_label.configure(
            text=(
                f"💰 Total invested: €{total_invested:.2f}\n"
                f"📊 Break-even price: €{break_even:.2f}\n"
                f"📈 Required increase: {required_percent:.2f}%"
            )
        )

        # Save to DB if ticker provided
        ticker = entry_ticker.get().strip()
        if ticker:
            add_stock(ticker, price, amount, break_even)
            load_mystocks()

        update_profit()

    def update_profit(event=None):
        if current_calc is None:
            return
        percent = slider.get()
        slider_label.configure(text=f"Earnings %: {percent:.2f}%")
        metrics = current_calc.as_dict(percent)
        profit = metrics.get("profit_loss")
        target = metrics.get("target_price")
        if profit is not None:
            color = "green" if profit > 0 else "red" if profit < 0 else "gray"
            profit_label.configure(
                text=f"🎯 Target price: €{target:.2f}\n💵 Profit/Loss: {'+' if profit > 0 else ''}{profit:.2f}€",
                text_color=color
            )

    slider.configure(command=update_profit)
    ctk.CTkButton(calculator_tab, text="Calculate / Save", command=calculate).pack(pady=15)

    # -----------------------
    # MyStocks Tab
    # -----------------------
    db_title = ctk.CTkLabel(mystocks_tab, text="📚 My Saved Stocks", font=("Arial", 18, "bold"))
    db_title.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 5))

    db_path_label = ctk.CTkLabel(
        mystocks_tab, text=f"Database: {get_db_path()}", font=("Arial", 10), text_color="gray"
    )
    db_path_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

    # Frame for Treeview
    tree_frame = ctk.CTkFrame(mystocks_tab)
    tree_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    # Make the tab resizable
    mystocks_tab.rowconfigure(2, weight=1)
    mystocks_tab.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    # Treeview
    columns = ("ID","Ticker", "Buy Price", "Shares", "Break-Even")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
    tree.grid(row=0, column=0, sticky="nsew")

    # Scrollbars
    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=v_scroll.set)
    v_scroll.grid(row=0, column=1, sticky="ns")

    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(xscroll=h_scroll.set)
    h_scroll.grid(row=1, column=0, sticky="ew")

    # Configure Treeview columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=80)

    # Load stocks function
    def load_mystocks():
        for row in tree.get_children():
            tree.delete(row)
        for idx, (idx, ticker, buy_price, shares, break_even) in enumerate(get_all_stocks(), start=1):
            tree.insert("", "end", values=(idx, ticker, f"{buy_price:.2f}", shares, f"{break_even:.2f}"))

    # --- Sell functionality ---
    def sell_selected():
        selected = tree.selection()
        if not selected:
            return

        item = tree.item(selected[0])
        stock_id, ticker, buy_price, shares, break_even = item["values"]
        buy_price, shares, break_even = float(buy_price), int(shares), float(break_even)

        # --- Popup Window ---
        popup = ctk.CTkToplevel(app)
        popup.title(f"Sell {ticker}")
        popup.geometry("300x200")

        ctk.CTkLabel(popup, text=f"Ticker: {ticker}").pack(pady=5)
        sell_amount_entry = ctk.CTkEntry(popup, placeholder_text=f"Amount to sell (max {shares})")
        sell_amount_entry.pack(pady=5)
        sell_price_entry = ctk.CTkEntry(popup, placeholder_text="Sell price per share (€)")
        sell_price_entry.pack(pady=5)

        def confirm_sell():
            try:
                sell_amount = int(parse_number(sell_amount_entry.get()))
                sell_price = parse_number(sell_price_entry.get())
            except ValueError:
                return

            if sell_amount <= 0 or sell_amount > shares:
                return

            profit_loss = (sell_price - buy_price) * sell_amount

            # Move to history
            move_to_history(stock_id, sell_amount, sell_price, profit_loss)

            # Refresh both tabs
            load_mystocks()
            load_history()
            popup.destroy()

        ctk.CTkButton(popup, text="Confirm Sell", command=confirm_sell).pack(pady=10)

    # --- Sell Button on Tab ---
    ctk.CTkButton(mystocks_tab, text="Sell Selected", command=sell_selected).grid(row=3, column=0, pady=10)

    # Load initial data
    load_mystocks()

    # -----------------------
    # History Tab
    # -----------------------
    history_label = ctk.CTkLabel(history_tab, text="📜 Sold Stocks History", font=("Arial", 18, "bold"))
    history_label.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 5))

    # Frame for Treeview
    hist_frame = ctk.CTkFrame(history_tab)
    hist_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    # Make the tab resizable
    history_tab.rowconfigure(1, weight=1)
    history_tab.columnconfigure(0, weight=1)
    hist_frame.rowconfigure(0, weight=1)
    hist_frame.columnconfigure(0, weight=1)

    # Treeview
    hist_columns = ("Ticker", "Buy Price", "Shares", "Break-Even", "Sell Price", "Profit/Loss", "Date Sold")
    hist_tree = ttk.Treeview(hist_frame, columns=hist_columns, show="headings")
    hist_tree.grid(row=0, column=0, sticky="nsew")

    # Scrollbars
    v_scroll_hist = ttk.Scrollbar(hist_frame, orient="vertical", command=hist_tree.yview)
    hist_tree.configure(yscroll=v_scroll_hist.set)
    v_scroll_hist.grid(row=0, column=1, sticky="ns")

    h_scroll_hist = ttk.Scrollbar(hist_frame, orient="horizontal", command=hist_tree.xview)
    hist_tree.configure(xscroll=h_scroll_hist.set)
    h_scroll_hist.grid(row=1, column=0, sticky="ew")

    # Configure tags for coloring
    hist_tree.tag_configure("profit", foreground="green")
    hist_tree.tag_configure("loss", foreground="red")
    hist_tree.tag_configure("neutral", foreground="gray")

    # Configure columns
    for col in hist_columns:
        hist_tree.heading(col, text=col)
        hist_tree.column(col, anchor="center", width=90)

    # Load history function
    def load_history():
        for row in hist_tree.get_children():
            hist_tree.delete(row)

        for row in get_history():
            ticker, buy_price, shares, break_even, sell_price, profit_loss, date_sold = row[1:8]

            # Determine tag based on profit/loss
            if profit_loss > 0:
                tag = "profit"
            elif profit_loss < 0:
                tag = "loss"
            else:
                tag = "neutral"

            hist_tree.insert(
                "",
                "end",
                values=(ticker, f"{buy_price:.2f}", shares, f"{break_even:.2f}",
                        f"{sell_price:.2f}", f"{profit_loss:.2f}", date_sold),
                tags=(tag,)
            )

    # Load initial data
    load_history()

    # Force geometry update
    app.update_idletasks()

    # Show default tab
    show_frame(calculator_tab)
    app.mainloop()
