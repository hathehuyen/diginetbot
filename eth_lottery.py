import os
from datetime import datetime
from web3.auto import w3


log_file = "eth_lottery.log"
jackpot_file = "eth_jackpot.gold"
my_log_file = open(log_file, "a")
while True:
    check_time = str(datetime.now())
    key_bin = os.urandom(32)
    key_hex = key_bin.hex()
    account = w3.eth.account.privateKeyToAccount(key_bin)
    address = account.address
    balance = w3.eth.getBalance(address)
    result = '{0} {1} {2} {3}'.format(check_time, key_hex, address, balance)
    print(result)
    my_log_file.write(result + '\n')
    if balance != 0:
        with open(jackpot_file, "a") as winfile:
            winfile.write(result + '\n')
