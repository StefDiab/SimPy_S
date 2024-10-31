import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Constants for simulation parameters
NUM_CASHIERS = 10  # Total number of cashiers
INITIAL_OPEN_CASHIERS = 2  # Number of open cashiers under normal conditions
SIMULATION_TIME = 480  # Simulation time in minutes (8 hours)
INTERARRIVAL_TIME = 2  # Average arrival time (minutes)
SERVICE_TIME = 5  # Average service time (minutes)
REPAIR_TIME = 10  # Time (in minutes) it takes to repair a cashier

# List to store repair times
repair_times = []

def customer(env, name, cashiers):
    """Function for customer behavior."""
    arrival_time = env.now
    print(f'{name} arrives at the store at {arrival_time:.2f} minutes')

    with cashiers.request() as request:
        yield request
        wait_time = env.now - arrival_time
        print(f'{name} starts checkout at {env.now:.2f} minutes (waited {wait_time:.2f} minutes)')
        
        # Simulate service time
        yield env.timeout(random.expovariate(1.0 / SERVICE_TIME))
        print(f'{name} leaves the store at {env.now:.2f} minutes')

def repair_cashier(env, cashier_id):
    """Repair a cashier and log start and end time."""
    start_time = env.now
    print(f'Cashier {cashier_id} is going into repair at {start_time:.2f} minutes')
    yield env.timeout(REPAIR_TIME)
    end_time = env.now
    print(f'Cashier {cashier_id} has been repaired and is now available at {end_time:.2f} minutes')

    # Log repair times
    repair_times.append((cashier_id, start_time, end_time))

def setup(env, num_cashiers, initial_open_cashiers):
    """Setup for the store and cashiers."""
    cashiers = simpy.Resource(env, num_cashiers)

    # Initial opening of cashiers
    for i in range(initial_open_cashiers):
        env.process(customer(env, f'Customer {i + 1}', cashiers))

    # Generate customers over time
    customer_id = initial_open_cashiers + 1
    while True:
        yield env.timeout(random.expovariate(1.0 / INTERARRIVAL_TIME))
        env.process(customer(env, f'Customer {customer_id}', cashiers))
        customer_id += 1
        
        # Condition to open more cashiers if needed (e.g., more than 5 customers in queue)
        if len(cashiers.queue) > 5 and cashiers.count < num_cashiers:
            cashiers.put(1)  # Open a new cashier (simulate a cashier being available)

        # Simulate a cashier going into repair
        if random.random() < 0.1:  # 10% chance that a cashier goes into repair
            if cashiers.count > 0:  # If there are available cashiers
                cashier_id = num_cashiers - cashiers.count  # Determine which cashier goes into repair
                yield env.timeout(0)  # Wait for a cycle
                env.process(repair_cashier(env, cashier_id))

def generate_histograms(results_df):
    """Generates histograms for wait times and service times."""
    try:
        # Create histograms for Wait Time and Service Time
        plt.figure(figsize=(12, 6))

        # Histogram for Wait Times
        plt.subplot(1, 2, 1)
        plt.hist(results_df['Wait Time'], bins=20, alpha=0.7, color='blue', edgecolor='black')
        plt.title('Distribution of Wait Times')
        plt.xlabel('Wait Time (minutes)')
        plt.ylabel('Number of Customers')

        # Histogram for Service Times
        plt.subplot(1, 2, 2)
        plt.hist(results_df['Service Time'], bins=20, alpha=0.7, color='green', edgecolor='black')
        plt.title('Distribution of Service Times')
        plt.xlabel('Service Time (minutes)')
        plt.ylabel('Number of Customers')

        # Save the figure
        plt.tight_layout()
        plt.savefig('queue_management_histograms.png')
        plt.close()

        print("Histograms have been created and saved as 'queue_management_histograms.png'.")

    except ImportError as e:
        print(f"An import error occurred: {e}. Please ensure all necessary libraries are installed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the simulation
env = simpy.Environment()
env.process(setup(env, NUM_CASHIERS, INITIAL_OPEN_CASHIERS))
env.run(until=SIMULATION_TIME)

# Simulate data for 213 customers for histogram
num_customers = 213
arrival_times = np.cumsum(np.random.exponential(scale=3, size=num_customers))
wait_times = np.random.exponential(scale=2, size=num_customers)  # Only generate wait times
service_times = np.random.exponential(scale=5, size=num_customers)

# Create DataFrame for results
results_df = pd.DataFrame({
    'Arrival Time': arrival_times,
    'Wait Time': wait_times,
    'Service Time': service_times
})

# Generate histograms
generate_histograms(results_df)
