import random

def create_otp_code() -> int:
    """
    Create a randomly generated 6 digit code
    """
    return random.randrange(100000, 1000000)