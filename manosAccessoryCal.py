import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading

# Define the success rates for each enhancement level
success_rates = {
    1: 0.75,
    2: 0.45,
    3: 0.30,
    4: 0.15,
    5: 0.05,
    # Add more levels as needed
}

# Fixed downgrade rate for all levels
downgrade_rate = 0.4

# Cron price per unit
cron_price = 3000000  # Set your desired cron price per unit here

# Cron fixed amount required for each enhancement level
cron_fix_amounts = {
    1: 25,
    2: 80,
    3: 275,
    4: 1100,
    5: 2200,
    # Add more levels as needed
}

# Default base cost
DEFAULT_BASE_COST = 230000000  # Set your desired default base cost here

def format_cost(cost):
    return "{:,.0f}".format(cost)

def show_success_rates():
    # Create a new window to display success rates
    success_rates_window = tk.Toplevel(root)
    success_rates_window.title("Success Rates")

    # Create labels for each enhancement level's success rate
    for level, rate in success_rates.items():
        ttk.Label(success_rates_window, text=f"Level {level}: {rate}").pack(padx=10, pady=5)

def edit_cron_price():
    new_cron_price = simpledialog.askfloat("Edit Cron Price", "Enter the new cron price per unit:")
    if new_cron_price is not None:
        global cron_price
        cron_price = new_cron_price
        cron_price_value_label.config(text=f"{cron_price} silver")

def toggle_use_crons():
    global use_crons_checkbox_var
    use_crons_checkbox_var.set(not use_crons_checkbox_var.get())

def simulate_enhancements(target_level, num_simulations, base_cost, use_crons, results):
    total_cost = 0
    for _ in range(num_simulations):
        current_level = starting_level_var.get() - 1  # Get starting level from dropdown
        cost = base_cost  # Start with base cost
        
        while current_level < target_level:
            enhancement_success_rate = success_rates.get(current_level + 1, 0)
            cost += base_cost  # Base cost for enhancing
            
            if random.random() < enhancement_success_rate:
                current_level += 1
            else:
                if use_crons and random.random() >= downgrade_rate:
                    # Check if enough crons are available
                    cron_cost = cron_price * cron_fix_amounts.get(current_level + 1, 0)
                    if cron_cost > 0:
                        cost += cron_cost  # Add cron cost
                else:
                    cost += base_cost  # Add base cost for rebuilding
                    current_level = starting_level_var.get() - 1  # Reset to starting level upon failure
        
        total_cost += cost
    
    average_cost = total_cost / num_simulations
    results.append(average_cost)

def calculate_average_cost():
    try:
        target_level = int(target_level_entry.get())
        if target_level < 1:
            raise ValueError("Enhancement level must be greater than or equal to 1.")
        
        base_cost = float(base_cost_entry.get() or DEFAULT_BASE_COST)  # Use default if entry is empty
        num_simulations = 100000
        use_crons = use_crons_checkbox_var.get()
        
        # Number of threads to use
        num_threads = 4  # You can adjust this based on your system's capabilities
        
        # Create a list to store the results from each thread
        results = []
        threads = []
        
        # Create and start threads
        for _ in range(num_threads):
            thread = threading.Thread(target=simulate_enhancements, args=(target_level, num_simulations // num_threads, base_cost, use_crons, results))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # Calculate the average cost from the results
        average_cost = sum(results) / num_threads
        
        formatted_cost = format_cost(int(average_cost))
        result_label.config(text=f"Average cost: {formatted_cost} silver")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("BDO Enhancement Calculator")

# Create and pack widgets
base_cost_label = ttk.Label(root, text="Base Cost:")
base_cost_label.grid(row=0, column=0, padx=10, pady=5)

base_cost_entry = ttk.Entry(root)
base_cost_entry.insert(0, str(DEFAULT_BASE_COST))  # Set default value
base_cost_entry.grid(row=0, column=1, padx=10, pady=5)

target_level_label = ttk.Label(root, text="Target Enhancement Level:")
target_level_label.grid(row=1, column=0, padx=10, pady=5)

target_level_entry = ttk.Entry(root)
target_level_entry.grid(row=1, column=1, padx=10, pady=5)

starting_level_label = ttk.Label(root, text="Starting Enhancement Level:")
starting_level_label.grid(row=2, column=0, padx=10, pady=5)

# Exclude level 5 from the dropdown options
starting_level_var = tk.IntVar(value=1)  # Default starting level is 1
starting_levels = list(success_rates.keys())[:-1]  # Exclude level 5
starting_level_dropdown = ttk.OptionMenu(root, starting_level_var, starting_levels[0], *starting_levels)
starting_level_dropdown.grid(row=2, column=1, padx=10, pady=5)

cron_price_label = ttk.Label(root, text="Cron Price per unit:")
cron_price_label.grid(row=3, column=0, padx=10, pady=5)

cron_price_value_label = ttk.Label(root, text=f"{cron_price} silver")
cron_price_value_label.grid(row=3, column=1, padx=10, pady=5)

edit_cron_price_button = ttk.Button(root, text="Edit Cron Price", command=edit_cron_price)
edit_cron_price_button.grid(row=4, columnspan=2, padx=10, pady=5)

use_crons_checkbox_var = tk.BooleanVar()
use_crons_checkbox = ttk.Checkbutton(root, text="Use Crons to prevent loss (may affect cost)", variable=use_crons_checkbox_var)
use_crons_checkbox.grid(row=5, columnspan=2, padx=10, pady=5)

calculate_button = ttk.Button(root, text="Calculate", command=calculate_average_cost)
calculate_button.grid(row=7, columnspan=2, padx=10, pady=10)

show_rates_button = ttk.Button(root, text="Show Success Rates", command=show_success_rates)
show_rates_button.grid(row=6, columnspan=2, padx=10, pady=5)

result_label = ttk.Label(root, text="")
result_label.grid(row=8, columnspan=2, padx=10, pady=5)

root.mainloop()


