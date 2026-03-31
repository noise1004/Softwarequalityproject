import asyncio
import random
import time
import json
import requests
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Datapoint

thingsURL   = "http://localhost:8080/api/2/things/"
policiesURL = "http://localhost:8080/api/2/policies/"
auth        = ("ditto", "ditto")

VEHICLE_IDS = [
    "org.vehicle:vehicle-1",
    "org.vehicle:vehicle-2",
    "org.vehicle:vehicle-3",
]

NUM_VEHICLES = 1


def put_policy(policyID, PolicyData):
    url = policiesURL + policyID
    headers = {"Content-Type": "Application/json"}
    return requests.put(url, json=PolicyData, headers=headers, auth=auth)


def put_thing(thingID, ThingData):
    url = thingsURL + thingID
    headers = {"Content-Type": "Application/json"}
    return requests.put(url, json=ThingData, headers=headers, auth=auth)


def put_feature_value(thingID, feature, value):
    url = thingsURL + thingID + "/features/" + feature + "/properties"
    headers = {"Content-Type": "Application/json"}
    return requests.put(url, json={"value": value}, headers=headers, auth=auth)


def setup_vehicle(thingID):
    with open("policy.json", "r") as f:
        policy_data = json.load(f)
    response = put_policy("org.ovin:my-policy", policy_data)
    print(f'Policy response: {response}')

    with open("VSS_Ditto.json", "r") as f:
        thing_data = json.load(f)
    thing_data["policyId"] = "org.ovin:my-policy"
    response = put_thing(thingID, thing_data)
    print(f'Thing {thingID} response: {response}')


async def simulate_vehicle(thingID):
    print(f'Starting simulation for {thingID}')
    setup_vehicle(thingID)

    async with VSSClient('127.0.0.1', 55555) as client:
        while True:
            VehicleSpeed       = random.randint(0, 255)
            EngineSpeed        = random.randint(0, 1000)
            ThrottlePosition   = random.randint(0, 200)
            CoolantTemperature = random.randint(0, 500)

            await client.set_current_values({
                'Vehicle.OBD.VehicleSpeed':       Datapoint(VehicleSpeed),
                'Vehicle.OBD.CoolantTemperature': Datapoint(CoolantTemperature),
                'Vehicle.OBD.ThrottlePosition':   Datapoint(ThrottlePosition),
                'Vehicle.OBD.EngineSpeed':        Datapoint(EngineSpeed),
            })

            print(f'[{thingID}] VehicleSpeed={VehicleSpeed} EngineSpeed={EngineSpeed} '
                  f'ThrottlePosition={ThrottlePosition} CoolantTemperature={CoolantTemperature}')

            put_feature_value(thingID, 'VehicleSpeed',       VehicleSpeed)
            put_feature_value(thingID, 'EngineSpeed',        EngineSpeed)
            put_feature_value(thingID, 'ThrottlePosition',   ThrottlePosition)
            put_feature_value(thingID, 'CoolantTemperature', CoolantTemperature)

            print('-----------------------------')
            time.sleep(1)


async def main():
    vehicles = VEHICLE_IDS[:NUM_VEHICLES]
    print(f'Simulating {NUM_VEHICLES} vehicle(s): {vehicles}')
    tasks = [simulate_vehicle(vid) for vid in vehicles]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        NUM_VEHICLES = int(sys.argv[1])
    asyncio.run(main())
