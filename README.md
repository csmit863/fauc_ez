This is a reworked version of the faucet.

This version uses a 6 digit code instead of a lengthy link to click.


This is a testnet ETH faucet app built for the QUT blockchain club.

The project is split as following:
 - main.py: the uvicorn logic and APIs
 - /ethereum/send_eth.py: function to send test ether and monitor balance of faucet
 - /otp/send_email.py: one-time-password generation and email confirmation logic

a .env file must be set up with a few variables in order for the faucet to work.
 - /ethereum/.env:
   - faucet_key: a private key for signing transactions to send ether
   - faucet_manager: an email to send notifications for when the faucet is low and needs to be topped up
 - /otp/send_email/.env:
   - jwt_secret: key for creating OTPs
   - sender_email: club email
   - qutbtc_app_pw: specially generated key for this app to send emails (should find a more secure way for future reference)

