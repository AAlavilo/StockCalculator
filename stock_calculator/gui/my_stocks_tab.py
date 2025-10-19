import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from stock_calculator.database import get_all_stocks, delete_stock, move_to_history

class MyStocksTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.create_ui()

    def create_ui(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            rowheight=25,
            fieldbackground="#2b2b2b",
            bordercolor="#2b2b2b"
        )
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        title = ctk.CTkLabel(self, text="My Stocks", font=("Arial", 18, "bold"))
        title.pack(pady=(10, 10))

        # Frame for table and scrollbar
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview setup
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ticker", "buy_price", "shares", "break_even"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
            height=10
        )
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Define columns
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("buy_price", text="Buy Price (€)")
        self.tree.heading("shares", text="Shares")
        self.tree.heading("break_even", text="Break-even (€)")

        self.tree.column("ticker", anchor="center", width=100)
        self.tree.column("buy_price", anchor="center", width=120)
        self.tree.column("shares", anchor="center", width=80)
        self.tree.column("break_even", anchor="center", width=120)

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        self.sell_button = ctk.CTkButton(btn_frame, text="Sell Stock", command=self.sell_selected_stock)
        self.sell_button.grid(row=0, column=0, padx=10)

        self.delete_button = ctk.CTkButton(btn_frame, text="Delete Stock", command=self.delete_selected_stock)
        self.delete_button.grid(row=0, column=1, padx=10)

        self.refresh_table()

    def refresh_table(self):
        # Clear old rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch new data
        stocks = get_all_stocks()
        for stock in stocks:
            stock_id, ticker, buy_price, shares, break_even = stock
            self.tree.insert("", "end", iid=stock_id, values=(ticker, buy_price, shares, break_even))

    def sell_selected_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Stock", "Please select a stock to sell.")
            return
        stock_id = selected[0]
        sell_price = tk.simpledialog.askfloat("Sell Price", "Enter the sell price (€):")
        if sell_price is None:
            return
        move_to_history(stock_id, sell_price)
        messagebox.showinfo("Sold", "Stock moved to Profits/Losses.")
        self.refresh_table()

    def delete_selected_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Stock", "Please select a stock to delete.")
            return
        stock_id = selected[0]
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this stock?")
        if confirm:
            delete_stock(stock_id)
            self.refresh_table()


