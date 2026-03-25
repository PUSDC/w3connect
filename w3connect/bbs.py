import time

import requests
import tornado.web
from web3 import Web3
from eth_account.messages import encode_defunct

from .b0x import get_account

BASE_RPC_URL = "https://mainnet.base.org"

# BBS_URL = 'https://bbs.w3connect.org'
BBS_URL = 'http://127.0.0.1:3000'
BBS_SESSION = requests.Session()

BBS_STAKING_CONTRACT = '0x6623Af17C813252CDBE29d062817fd27Bd865c35'
BBS_STAKING_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "amount", "type": "uint256"}
        ],
        "name": "deposit",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "stakingId", "type": "uint256"}
        ],
        "name": "withdraw",
        "outputs": [],
        "type": "function"
    }
]


BASE_USDC_CONTRACT = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
BASE_CHAIN_ID = 8453

ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]


class BBSLoginHandler(tornado.web.RequestHandler):
    def login(self):
        account = get_account()
        if not account:
            self.set_status(500)
            self.finish({"error": "Account not loaded on server."})
            return

        address = account.address.lower()
        timestamp = int(time.time())
        print(f"Address: {address}")
        print(f"Timestamp: {timestamp}")
        
        # SIWE message format required by app.py
        message_text = f"Commit to the self-cleaning network.\n\nWallet: {address}\nTimestamp: {timestamp}"
        print(f"Message: {message_text}")
        message = encode_defunct(text=message_text)
        
        # Sign the message
        signed_message = account.sign_message(message)
        signature = signed_message.signature.hex()

        # Prepare payload for the verify endpoint
        payload = {
            "address": address,
            "signature": signature,
            "timestamp": timestamp
        }

        try:
            # POST to the verify endpoint and store the session in memory
            response = BBS_SESSION.post(f'{BBS_URL}/api/auth/wallet/verify', json=payload)
            if response.status_code == 200:
                # self.finish({
                #     "success": True, 
                #     "message": "Logged in successfully to BBS",
                #     # "user": response.json().get("user"),
                #     "address": address
                # })
                return True
            else:
                self.set_status(response.status_code)
                self.finish({
                    "success": False, 
                    "error": f"Login failed: {response.text}",
                    "status_code": response.status_code
                })
                return False
        except Exception as e:
            self.set_status(500)
            self.finish({"success": False, "error": str(e)})
            return False

class BBSCreatePostHandler(BBSLoginHandler):
    def get(self):
        self.post()

    def post(self):
        # This just shows that we have some session info in memory
        account = get_account()
        assert self.login()
        w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

        if not w3.is_connected():
            self.finish({"error": "Failed to connect to blockchain RPC."})
            return

        usdc_amount = int(float(0.01) * 10**6)
        contract_address = BASE_USDC_CONTRACT
        usdc_contract = w3.eth.contract(address=contract_address, abi=ERC20_ABI)
        staking_contract = w3.eth.contract(address=BBS_STAKING_CONTRACT, abi=BBS_STAKING_ABI)

        sleep = 2
        while True:
            try:
                nonce = w3.eth.get_transaction_count(account.address)
                gas_price = w3.eth.gas_price
                tx1 = usdc_contract.functions.approve(BBS_STAKING_CONTRACT, usdc_amount).build_transaction({
                        'from': account.address,
                        'chainId': BASE_CHAIN_ID,
                        'gas': 100000,
                        'gasPrice': gas_price,
                        'nonce': nonce,
                    })
                print('tx1 approve', tx1)
                signed_tx1 = w3.eth.account.sign_transaction(tx1, private_key=account.key)
                try:
                    tx_hash1 = w3.eth.send_raw_transaction(signed_tx1.raw_transaction)
                except Exception as e:
                    tx_hash1 = w3.eth.send_raw_transaction(signed_tx1.rawTransaction)

                print('tx_hash1', tx_hash1.hex())
                time.sleep(2)
                break

            except Exception as e:
                print(f"Failed to send tx1: {e}")
                sleep = sleep * 2
                time.sleep(sleep)
                continue

        sleep = 2
        tx_hash2 = None
        while True:
            try:
                nonce = w3.eth.get_transaction_count(account.address)
                gas_price = w3.eth.gas_price
                tx2 = staking_contract.functions.deposit(usdc_amount).build_transaction({
                        'from': account.address,
                        'chainId': BASE_CHAIN_ID,
                        'gas': 1000000,
                        'gasPrice': gas_price,
                        'nonce': nonce,
                    })
                print('tx2 deposit', tx2)
                signed_tx2 = w3.eth.account.sign_transaction(tx2, private_key=account.key)
                try:
                    tx_hash2 = w3.eth.send_raw_transaction(signed_tx2.raw_transaction)
                except Exception as e:
                    tx_hash2 = w3.eth.send_raw_transaction(signed_tx2.rawTransaction)

                print('tx_hash2', tx_hash2.hex())
                time.sleep(2)
                break

            except Exception as e:
                print(f"Failed to send tx2: {e}")
                sleep = sleep * 2
                time.sleep(sleep)
                continue

        # sleep = 2
        # while True:
        #     try:
        #         receipt = w3.eth.get_transaction_receipt(tx_hash2)
        #         # print(receipt)

        #         inbox_send_event_signature = w3.keccak(text="InboxSend(uint256)").hex()
        #         for log in receipt['logs']:
        #             if log['topics'] and log['topics'][0].hex() == inbox_send_event_signature:
        #                 parsed_log = pusdc_contract.events.InboxSend().process_log(log)
        #                 print(f"Parsed InboxSend event from {log['address']}: {parsed_log.args}")
        #                 tx_no = parsed_log.args.txNo
        #                 break
        #         break

        #     except Exception as e:
        #         print(f"Failed to get receipt: {e}")
        #         sleep = sleep * 2
        #         time.sleep(sleep)
        #         continue

        # print('tx_no', tx_no)


        cookies = BBS_SESSION.cookies.get_dict()

        if tx_hash2:
            req = requests.post(BBS_URL+'/api/create_post', json={
                "tx_hash": tx_hash2.hex(),
            }, cookies=cookies)
            # print('req', req.text)
        self.finish({
            "result": req.json()
        })

class BBSEditPostHandler(BBSLoginHandler):
    """Optional: A handler to edit post on BBS"""
    def get(self):
        self.post()

    def post(self):
        assert self.login()

        post_id = self.get_argument('post_id', '')
        title = self.get_argument('title', '')
        content = self.get_argument('content', '')
        category = self.get_argument('category', 'jd')
        live = self.get_argument('live', 'false')
        
        cookies = BBS_SESSION.cookies.get_dict()
        
        req = requests.post(f'{BBS_URL}/post/{post_id}/edit', data={
            "title": title,
            "content": content,
            "category": category,
            "live": live,
        }, cookies=cookies)
        # print('req', req.text)
        self.finish({
            "result": True
        })
