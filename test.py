from colorama import Fore, init
from tabulate import tabulate

init()

print(Fore.GREEN + "Colorama is working!")

data = [
    ["C001", "Theft", "Active"],
    ["C002", "Fraud", "Closed"]
]

print(tabulate(data,
               headers=["Case ID", "Crime Type", "Status"],
               tablefmt="grid"))