import requests
import time

url = "http://localhost:5000/ussd"

data = {
    "sessionId": "12345",
    "phoneNumber": "08012345678"
}

# Step 1: POST with text: "1"
response1 = requests.post(url, data={**data, "text": "1"})
print("Step 1 Status Code:", response1.status_code)
print("Step 1 Response:", response1.text)

# Step 2: POST with text: "1*user2"
response2 = requests.post(url, data={**data, "text": "1*user2"})
print("Step 2 Status Code:", response2.status_code)
print("Step 2 Response:", response2.text)

# Step 3: POST with text: "1*user2*100"
response3 = requests.post(url, data={**data, "text": "1*user2*100"})
print("Step 3 Status Code:", response3.status_code)
print("Step 3 Response:", response3.text)

# Step 4: POST with text: "1*user2*100*1234"
response4 = requests.post(url, data={**data, "text": "1*user2*100*1234"})
print("Step 4 Status Code:", response4.status_code)
print("Step 4 Response:", response4.text)

# Step 5: Check balance before sync
response5 = requests.post(url, data={**data, "text": "2"})
print("Step 5 Status Code:", response5.status_code)
print("Step 5 Response:", response5.text)

# Wait to reduce contention
time.sleep(0.5)

# Step 6: Sync transactions
response6 = requests.post(url, data={**data, "text": "4"})
print("Step 6 Status Code:", response6.status_code)
print("Step 6 Response:", response6.text)

# Step 7: Check balance after sync
response7 = requests.post(url, data={**data, "text": "2"})
print("Step 7 Status Code:", response7.status_code)
print("Step 7 Response:", response7.text)

# Verify results
if response4.status_code == 200 and "END Transaction initiated" in response4.text:
    print("Transaction successfully initiated!")
else:
    print("Transaction failed.")

if response6.status_code == 200 and "END Transactions synced successfully" in response6.text:
    print("Sync successful!")
else:
    print("Sync failed.")