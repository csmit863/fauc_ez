from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from web3 import Web3
from otp.create_code import create_otp_code
import time
from otp.send_email import send_email
from ethereum.send_eth import send_eth

app = FastAPI()

origins = [
    "https://faucet.qutblockchain.club",
    "http://localhost",
    "localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ethereum address validation function
def is_valid_ethereum_address(address: str) -> bool:
    return Web3.is_address(address)

# store a list of OTP codes, emails
current_codes = set()

# In-memory store to track email and address combinations
used_combinations = set()

def checkClaimed(email, address):
    print(used_combinations)
    current_time = time.time()
    for entry in list(used_combinations):
        if entry[0] == email or entry[1] == address:
            if current_time - entry[2] < 3 * 60 * 60:  # 3 hours in seconds
                print('Wait 1 hours')
                raise HTTPException(status_code=400, detail="This email and address combination has already received funding within the last 3 hours")
            else:
                # Remove the old entry since it's expired
                used_combinations.remove(entry)


@app.post("/api/get-otp")
async def getotp(email: str, address: str):

    if not (email.endswith("@qut.edu.au") or email.endswith("@connect.qut.edu.au")):
        raise HTTPException(status_code=422, detail='Email must be a QUT email address')

    # create the key / lock pair (based on email and address)
    if is_valid_ethereum_address(address):
        checkClaimed(email, address)
        otp = create_otp_code()

        # add in time created
        print(email, address, otp)
        current_codes.add((email, address, otp))

        # send email with otp link
        message = f"Your 6-digit one time code to verify your QUT Email with the QUT Blockchain Club is {otp}"
        subject = 'QUT Blockchain - One Time Code'
        send_email(email, message, subject)
        return 'Email successfully sent.'
    else:
        raise HTTPException(status_code=422, detail='Not a valid Ethereum address')



@app.post("/api/get-eth")
async def get_eth(email: str, address: str, otp: str):
    otp = int(otp)
    print(email, address, otp)
    if ((email, address, otp)) in current_codes:
        checkClaimed(email, address)
        current_codes.remove((email, address, otp))
        used_combinations.add((email, address, time.time()))

        # Send ETH transaction
        status, tx_hash = await send_eth(address)
        return {"status": status, "tx_hash": tx_hash}
    
    raise HTTPException(status_code=400, detail='Invalid OTP or combination')
