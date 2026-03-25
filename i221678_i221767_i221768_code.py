import tkinter as tk
from tkinter import messagebox
import secrets
import random
import functools
import json
import os
import time

# === Shamir's Secret Sharing Implementation ===
def polynom(x, coefficients):
    return sum([c * (x ** i) for i, c in enumerate(coefficients)])

def create_shares(secret_bytes, n, k):
    shares = []
    for idx in range(len(secret_bytes)):
        coeffs = [random.randint(0, 255) for _ in range(k - 1)]
        coeffs.insert(0, secret_bytes[idx])
        share_set = [(i + 1, polynom(i + 1, coeffs) % 256) for i in range(n)]
        shares.append(share_set)

    final_shares = []
    for i in range(n):
        share_bytes = bytes([shares[b][i][1] for b in range(len(secret_bytes))])
        final_shares.append((i + 1, share_bytes))
    return final_shares

def recover_secret(shares):
    def lagrange_interpolate(x, x_s, y_s):
        def _PI(vals): return functools.reduce(lambda x, y: x * y, vals, 1)
        total = 0
        for i in range(len(x_s)):
            xi, yi = x_s[i], y_s[i]
            others = list(x_s)
            del others[i]
            num = _PI(x - o for o in others)
            den = _PI(xi - o for o in others)
            total += yi * num // den
        return total

    k = len(shares)
    length = len(shares[0][1])
    secret_bytes = bytearray()
    for byte_idx in range(length):
        x_s = [s[0] for s in shares]
        y_s = [s[1][byte_idx] for s in shares]
        recovered = lagrange_interpolate(0, x_s, y_s)
        secret_bytes.append(recovered % 256)
    return bytes(secret_bytes)

# === File Helpers ===
def save_wallet(wallet_id, wallet_data):
    filename = f"wallet_{wallet_id}.json"
    with open(filename, "w") as f:
        json.dump(wallet_data, f)

def load_wallet(wallet_id):
    filename = f"wallet_{wallet_id}.json"
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return json.load(f)

def save_users(users_set):
    with open("users.json", "w") as f:
        json.dump(list(users_set), f)

def load_users():
    if not os.path.exists("users.json"):
        return set()
    with open("users.json", "r") as f:
        return set(json.load(f))

# === GUI Application ===
class MultiUserWalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-User Crypto Wallet")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)
        self.root.maxsize(900, 650)
        
        # Modern theme colors
        self.primary_color = "#0d6efd"  # Bootstrap primary blue
        self.secondary_color = "#6c757d"  # Bootstrap secondary gray
        self.success_color = "#198754"  # Bootstrap success green
        self.danger_color = "#dc3545"  # Bootstrap danger red
        self.light_color = "#f8f9fa"  # Bootstrap light
        self.dark_color = "#212529"  # Bootstrap dark
        self.bg_color = "#f8f9fa"  # Light background
        self.card_color = "#ffffff"  # Card background
        
        # Font styles
        self.font_main = ("Segoe UI", 12)
        self.font_header = ("Segoe UI", 24, "bold")
        self.font_subheader = ("Segoe UI", 18)
        self.font_button = ("Segoe UI", 12, "bold")
        self.font_label = ("Segoe UI", 11)
        self.font_mono = ("Consolas", 10)
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize variables
        self.secret = b""
        self.shares = []
        self.k = 3
        self.n = 5
        self.wallet_id = ""
        self.users = []
        self.wallet_data = {}
        
        self.build_main_page()

    def create_card(self, parent):
        """Create a card-like container with shadow effect"""
        card = tk.Frame(parent, bg=self.card_color, padx=20, pady=20, 
                       relief="ridge", borderwidth=1)
        card.pack(pady=20, padx=20, fill="both", expand=True)
        return card

    def create_button(self, parent, text, command, style="primary"):
        """Create a styled button with hover effects"""
        colors = {
            "primary": self.primary_color,
            "secondary": self.secondary_color,
            "success": self.success_color,
            "danger": self.danger_color
        }
        bg_color = colors.get(style, self.primary_color)
        
        btn = tk.Button(parent, text=text, command=command,
                       font=self.font_button, bg=bg_color, fg="white",
                       activebackground=bg_color, activeforeground="white",
                       borderwidth=0, relief="flat", padx=15, pady=8)
        
        # Add hover effects
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.darken_color(bg_color)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        return btn

    def darken_color(self, color, factor=0.8):
        """Darken a hex color by a factor"""
        rgb = tuple(int(color[i+1:i+3], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return "#%02x%02x%02x" % darkened

    def build_main_page(self):
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 20))
        
        tk.Label(header, text="🔐 Multi-User Wallet", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        tk.Label(header, text="Secure collaborative cryptocurrency management", 
                font=self.font_subheader, bg=self.bg_color, fg=self.secondary_color).pack()
        
        # Card for buttons
        card = self.create_card(container)
        
        # Buttons
        self.create_button(card, "Generate New Wallet", self.build_wallet_setup_page, "primary").pack(pady=10, fill="x")
        self.create_button(card, "Recover Existing Wallet", self.build_recover_wallet_page, "secondary").pack(pady=10, fill="x")

    def build_wallet_setup_page(self):
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text="Setup New Wallet", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Form card
        card = self.create_card(container)
        
        # Form fields
        fields = [
            ("Wallet ID:", "wallet_id_entry"),
            ("Number of users (n):", "n_entry"),
            ("Recovery threshold (k ≤ n):", "k_entry"),
            ("Usernames (comma separated):", "users_entry")
        ]
        
        for label_text, attr_name in fields:
            frame = tk.Frame(card, bg=self.card_color)
            frame.pack(fill="x", pady=8)
            
            tk.Label(frame, text=label_text, font=self.font_label, 
                    bg=self.card_color, fg=self.dark_color).pack(anchor="w")
            
            entry = tk.Entry(frame, font=self.font_main, bg="white", fg=self.dark_color,
                           relief="solid", borderwidth=1, highlightthickness=0)
            entry.pack(fill="x", ipady=5)
            setattr(self, attr_name, entry)
        
        # Button container
        button_frame = tk.Frame(card, bg=self.card_color)
        button_frame.pack(fill="x", pady=10)
        
        self.create_button(button_frame, "Generate Wallet", self.generate_wallet, "success").pack(side="right", padx=5)
        self.create_button(button_frame, "Cancel", self.build_main_page, "secondary").pack(side="right", padx=5)

    def generate_wallet(self):
        self.wallet_id = self.wallet_id_entry.get()
        if not self.wallet_id:
            self.show_error("Wallet ID cannot be empty.")
            return

        try:
            self.n = int(self.n_entry.get())
            self.k = int(self.k_entry.get())
            if self.k > self.n:
                self.show_error("Threshold (k) cannot be greater than number of users (n).")
                return
        except ValueError:
            self.show_error("Invalid input for number of users or threshold.")
            return

        all_users = load_users()
        self.users = [user.strip() for user in self.users_entry.get().split(",")]

        if len(self.users) != self.n:
            self.show_error(f"Please provide exactly {self.n} usernames.")
            return

        for user in self.users:
            if user in all_users:
                self.show_error(f"Username '{user}' already exists. Choose another.")
                return
            all_users.add(user)

        # Generate the secret and shares
        self.secret = secrets.token_bytes(32)
        self.shares = create_shares(self.secret, self.n, self.k)

        # Set initial wallet data
        self.wallet_data = {
            "wallet_id": self.wallet_id,
            "threshold": self.k,
            "balance": 10.0,
            "transactions": [],
            "users": {}
        }

        # Save shares for each user
        self.shares_text = ""
        for i, user in enumerate(self.users):
            index, share = self.shares[i]
            self.wallet_data["users"][user] = {
                "index": index,
                "share": share.hex()
            }
            self.shares_text += f"User: {user}, Share {index}: {share.hex()}\n"

        save_wallet(self.wallet_id, self.wallet_data)
        save_users(all_users)

        self.show_success(f"Wallet created successfully with ID: {self.wallet_id}", True)

    def show_success(self, message, show_shares=False):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Success card
        card = self.create_card(container)
        
        # Success icon and message
        tk.Label(card, text="✓", font=("Segoe UI", 48), 
                bg=self.card_color, fg=self.success_color).pack(pady=10)
        tk.Label(card, text=message, font=self.font_subheader, 
                bg=self.card_color, fg=self.dark_color).pack(pady=10)

        if show_shares:
            # Shares display
            tk.Label(card, text="User Shares:", font=self.font_button, 
                    bg=self.card_color, fg=self.dark_color).pack(pady=10)
            
            scroll_frame = tk.Frame(card, bg=self.card_color)
            scroll_frame.pack(fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(scroll_frame)
            scrollbar.pack(side="right", fill="y")
            
            shares_text = tk.Text(scroll_frame, font=self.font_mono, 
                                yscrollcommand=scrollbar.set,
                                bg=self.card_color, fg=self.dark_color,
                                borderwidth=0, highlightthickness=0)
            shares_text.insert("1.0", self.shares_text)
            shares_text.config(state="disabled")
            shares_text.pack(fill="both", expand=True)
            
            scrollbar.config(command=shares_text.yview)

        # Back button
        self.create_button(card, "Back to Main Page", self.build_main_page, "primary").pack(pady=20)

    def show_error(self, message):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Error card
        card = self.create_card(container)
        
        # Error icon and message
        tk.Label(card, text="⚠", font=("Segoe UI", 48), 
                bg=self.card_color, fg=self.danger_color).pack(pady=10)
        tk.Label(card, text=message, font=self.font_subheader, 
                bg=self.card_color, fg=self.dark_color).pack(pady=10)
        
        # Back button
        self.create_button(card, "Go Back", self.build_main_page, "danger").pack(pady=20)

    def build_recover_wallet_page(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text="Recover Wallet", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Form card
        card = self.create_card(container)
        
        # Wallet ID input
        frame = tk.Frame(card, bg=self.card_color)
        frame.pack(fill="x", pady=8)
        
        tk.Label(frame, text="Enter Wallet ID:", font=self.font_label, 
                bg=self.card_color, fg=self.dark_color).pack(anchor="w")
        
        self.wallet_id_entry = tk.Entry(frame, font=self.font_main, bg="white", 
                                      fg=self.dark_color, relief="solid", borderwidth=1)
        self.wallet_id_entry.pack(fill="x", ipady=5)
        
        # Button container
        button_frame = tk.Frame(card, bg=self.card_color)
        button_frame.pack(fill="x", pady=10)
        
        self.create_button(button_frame, "Next", self.verify_wallet_id, "primary").pack(side="right", padx=5)
        self.create_button(button_frame, "Back", self.build_main_page, "secondary").pack(side="right", padx=5)

    def verify_wallet_id(self):
        wallet_id = self.wallet_id_entry.get()
        if not wallet_id:
            self.show_error("Wallet ID cannot be empty.")
            return

        wallet_data = load_wallet(wallet_id)
        if wallet_data is None:
            self.show_error("Wallet ID is incorrect.")
            return

        self.wallet_data = wallet_data
        self.k = wallet_data["threshold"]
        self.build_user_key_input_page()

    def build_user_key_input_page(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text="Enter Recovery Keys", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Form card
        card = self.create_card(container)
        
        self.user_entries = []
        self.key_entries = []

        for i in range(self.k):
            frame = tk.Frame(card, bg=self.card_color)
            frame.pack(fill="x", pady=8)
            
            tk.Label(frame, text=f"Username {i+1}:", font=self.font_label, 
                    bg=self.card_color, fg=self.dark_color).pack(anchor="w")
            
            user_entry = tk.Entry(frame, font=self.font_main, bg="white", 
                                fg=self.dark_color, relief="solid", borderwidth=1)
            user_entry.pack(fill="x", ipady=5)
            self.user_entries.append(user_entry)
            
            tk.Label(frame, text=f"Share Key {i+1}:", font=self.font_label, 
                    bg=self.card_color, fg=self.dark_color).pack(anchor="w")
            
            key_entry = tk.Entry(frame, font=self.font_main, bg="white", 
                               fg=self.dark_color, relief="solid", borderwidth=1)
            key_entry.pack(fill="x", ipady=5)
            self.key_entries.append(key_entry)
        
        # Button container
        button_frame = tk.Frame(card, bg=self.card_color)
        button_frame.pack(fill="x", pady=10)
        
        self.create_button(button_frame, "Recover Wallet", self.recover_wallet, "success").pack(side="right", padx=5)
        self.create_button(button_frame, "Back", self.build_recover_wallet_page, "secondary").pack(side="right", padx=5)

    def recover_wallet(self):
        shares = []
        for i in range(self.k):
            user = self.user_entries[i].get()
            key = self.key_entries[i].get()
            if not user or not key:
                self.show_error("All fields must be filled.")
                return
            if user not in self.wallet_data["users"]:
                self.show_error(f"User '{user}' is not part of the wallet.")
                return
            if key != self.wallet_data["users"][user]["share"]:
                self.show_error("Invalid key for user.")
                return
            shares.append((i + 1, bytes.fromhex(key)))

        self.secret = recover_secret(shares)
        self.show_success("Wallet recovered successfully!")
        self.build_wallet_page()

    def build_wallet_page(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text=f"Wallet: {self.wallet_data['wallet_id']}", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Wallet info card
        card = self.create_card(container)
        
        # Balance display
        balance_frame = tk.Frame(card, bg=self.card_color)
        balance_frame.pack(fill="x", pady=10)
        
        tk.Label(balance_frame, text="Balance:", font=self.font_subheader, 
                bg=self.card_color, fg=self.dark_color).pack(side="left")
        tk.Label(balance_frame, text=f"${self.wallet_data['balance']:.2f}", 
                font=self.font_subheader, bg=self.card_color, fg=self.primary_color).pack(side="left", padx=10)
        
        # Action buttons
        self.create_button(card, "Send Transaction", self.send_transaction, "primary").pack(pady=10, fill="x")
        self.create_button(card, "View Transactions", self.view_transactions, "secondary").pack(pady=10, fill="x")
        self.create_button(card, "Back", self.build_recover_wallet_page, "secondary").pack(pady=10, fill="x")

    def send_transaction(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text="Send Transaction", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Form card
        card = self.create_card(container)
        
        # Receiver input
        frame = tk.Frame(card, bg=self.card_color)
        frame.pack(fill="x", pady=8)
        
        tk.Label(frame, text="Receiver Wallet ID:", font=self.font_label, 
                bg=self.card_color, fg=self.dark_color).pack(anchor="w")
        
        self.receiver_wallet_id = tk.Entry(frame, font=self.font_main, bg="white", 
                                         fg=self.dark_color, relief="solid", borderwidth=1)
        self.receiver_wallet_id.pack(fill="x", ipady=5)
        
        # Amount input
        frame = tk.Frame(card, bg=self.card_color)
        frame.pack(fill="x", pady=8)
        
        tk.Label(frame, text="Amount:", font=self.font_label, 
                bg=self.card_color, fg=self.dark_color).pack(anchor="w")
        
        self.transaction_amount = tk.Entry(frame, font=self.font_main, bg="white", 
                                         fg=self.dark_color, relief="solid", borderwidth=1)
        self.transaction_amount.pack(fill="x", ipady=5)
        
        # Button container
        button_frame = tk.Frame(card, bg=self.card_color)
        button_frame.pack(fill="x", pady=10)
        
        self.create_button(button_frame, "Send", self.process_transaction, "success").pack(side="right", padx=5)
        self.create_button(button_frame, "Cancel", self.build_wallet_page, "secondary").pack(side="right", padx=5)

    def process_transaction(self):
        receiver_wallet_id = self.receiver_wallet_id.get()
        amount = self.transaction_amount.get()

        if not receiver_wallet_id or not amount:
            self.show_error("Please fill in all fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            self.show_error("Invalid transaction amount.")
            return

        if amount <= 0:
            self.show_error("Amount should be greater than zero.")
            return

        if self.wallet_data["balance"] < amount:
            self.show_error("Insufficient balance.")
            return

        receiver_wallet_data = load_wallet(receiver_wallet_id)
        if not receiver_wallet_data:
            self.show_error("Receiver wallet ID does not exist.")
            return

        # Update balances
        self.wallet_data["balance"] -= amount
        receiver_wallet_data["balance"] += amount

        # Log transaction
        transaction = {
            "sender": self.wallet_data["wallet_id"],
            "receiver": receiver_wallet_id,
            "amount": amount,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.wallet_data["transactions"].append(transaction)
        receiver_wallet_data["transactions"].append(transaction)

        save_wallet(self.wallet_data["wallet_id"], self.wallet_data)
        save_wallet(receiver_wallet_data["wallet_id"], receiver_wallet_data)

        self.show_success(f"Transaction of ${amount:.2f} sent successfully!")
        self.build_wallet_page()

    def view_transactions(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(pady=(0, 10))
        
        tk.Label(header, text="Transaction History", 
                font=self.font_header, bg=self.bg_color, fg=self.dark_color).pack()
        
        # Transactions card
        card = self.create_card(container)
        
        if not self.wallet_data["transactions"]:
            tk.Label(card, text="No transactions yet", 
                    font=self.font_subheader, bg=self.card_color, fg=self.secondary_color).pack(pady=20)
        else:
            scroll_frame = tk.Frame(card, bg=self.card_color)
            scroll_frame.pack(fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(scroll_frame)
            scrollbar.pack(side="right", fill="y")
            
            transactions_text = tk.Text(scroll_frame, font=self.font_main, 
                                      yscrollcommand=scrollbar.set,
                                      bg=self.card_color, fg=self.dark_color,
                                      borderwidth=0, highlightthickness=0)
            
            for tx in self.wallet_data["transactions"]:
                transactions_text.insert("end", 
                    f"{tx['timestamp']}\n"
                    f"From: {tx['sender']}\n"
                    f"To: {tx['receiver']}\n"
                    f"Amount: ${tx['amount']:.2f}\n\n")
            
            transactions_text.config(state="disabled")
            transactions_text.pack(fill="both", expand=True)
            scrollbar.config(command=transactions_text.yview)
        
        # Back button
        self.create_button(card, "Back to Wallet", self.build_wallet_page, "primary").pack(pady=20)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiUserWalletApp(root)
    root.mainloop()