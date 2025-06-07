import requests


def api_requst(serialNumbers):

    # serialNumbers = [10240035, 10240036, 10240037, 10240038]
    apiInfos = list()
    for serialNumber in serialNumbers:
        print(serialNumber)
        url = 'https://neo-manager.ru/passport/meters/' + str(serialNumber)
        headers = {
            'Api-Key': 'IYYrqffqeWF9esyMvTrF586OqqywN2Dd3xk6L8vUjtUZDN46ocBM5K5TXrG4Cd58'}
        response = requests.get(url, headers=headers)
        print(response)
        api_info = response.json()
        apiInfos.append(api_info)
    print(apiInfos)
    print(len(apiInfos))


startNumber = 10240047
finishNumber = 10240049
numbers = list()
for i in range(startNumber, finishNumber+1):
    numbers.append(i)
    print(numbers)
api_requst(numbers)
