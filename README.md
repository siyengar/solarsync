This is an experimental project I did to check out what managed charging might look like for a Tesla.
It aims to allow you to use your solar generation in order to schedule charging for your tesla.
Unlike traditional managed charging solutions that use the EVSE (often referred to the charging station)
to control the charge rates, this project controls the charing rate directly on the EV onboard charger
on the car, so this approach would technically work with any EVSE.

This project currently is setup for the following configuration:
1. Tesla wall connector
2. Enphase inverters connected to your solar panel
3. A single Tesla car household

The way it works is that the project first checks whether your car is connected to the wall connector.
It then polls enphase's APIs to check what the current solar generation is
at periodic intervals, and then sets the charging rate for your tesla accordingly. 

Steps to setup:
1. Setup your enphase developer account https://developer-v4.enphase.com/docs/quickstart.html
2. Get the API key, Client ID, Client Secret from the guide above
3. Fill up the "tmp.config" file with the correct parameters
4. Run ./setup.sh and click through the SSO webviews for both enphase as well as tesla
5. Run python3 solarsync.py
6. Logs are in logs/solarsync

running this on a raspberry pi might allow you to do this continuously.
