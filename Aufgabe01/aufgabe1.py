import time
import ntplib
import csv
from datetime import datetime, timedelta

# Reference Timestamp: Time when the system clock was last set or corrected
# Original Timestamp: Time at the client when the request departed for the server
# Receive Timestamp: Time at the server when the response left for the client
# Transmit Timestamp: Time at the server when the response left for the client
# Destination Timestamp: Time at the clinet when the reply arrived from the server


PERIOD_IN_MINUTES=3*60
MEASUREMENT_INTERVAL_IN_SECONDS=30

APPLE_TIME='time.apple.com'
MICROSOFT_TIME='time.microsoft.com'
GOOGLE_TIME='time.google.com'
BERKLEY_TIME='ntp1.net.berkeley.edu'

OUTPU_FILE_CSV='aufgabe01_results.csv'

def main():
    client = ntplib.NTPClient()

    start_time = datetime.now()
    
    with open(OUTPU_FILE_CSV, 'w+') as csvfile:
        file = csv.writer(csvfile)
        file.writerow(['ITERATION', 'APPLE', 'MICROSOFT', 'GOOGLE', 'BERKLEY'])
        
        i=0
        while(start_time + timedelta(minutes=PERIOD_IN_MINUTES) > datetime.now()):
            apple_offset = get_offset(client, APPLE_TIME)
            microsoft_offset = get_offset(client, MICROSOFT_TIME)
            google_offset = get_offset(client, GOOGLE_TIME)
            berkley_offset = get_offset(client, BERKLEY_TIME)
            file.writerow([i, apple_offset, microsoft_offset, google_offset, berkley_offset])
            
            i+=1
            csvfile.flush()
            time.sleep(MEASUREMENT_INTERVAL_IN_SECONDS)

def get_offset(client:ntplib.NTPClient, ntp_url):
    res = client.request(APPLE_TIME)
    return res.offset


if __name__ == '__main__':
    main()

