import random
import time

def main():
    # Repeat Infinitely
    while True:
        # Generate random values for each feature with the defined ranges
        VehicleSpeed = random.randint(0,255)
        EngineSpeed = random.randint(0,1000)
        ThrottlePosition = random.randint(0,200)
        CoolantTemperature = random.randint(0,500)

        # Print the value for each feature
        print('Vehicle Speed =', VehicleSpeed)
        print('Engine Speed =', EngineSpeed)
        print('Throttle Position =', ThrottlePosition)
        print('Coolant Temperature =', CoolantTemperature)

        # Pause for 1 second
        time.sleep(1)

        print('-----------------------------')

# Run the main function
main()
