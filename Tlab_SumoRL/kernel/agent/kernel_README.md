`vehicle_agent.py`

This code defines the `VehicleAgent` class, which represents a vehicle agent in a SUMO simulation. The class provides functionalities to interact with the SUMO environment, retrieve vehicle information, and perform actions like lane changes.

Key Components:

- **Initialization**: The `VehicleAgent` class is initialized with parameters like vehicle ID, network path, origin, destination, entrance time, and other optional parameters.

- **Properties**: The class provides several properties to retrieve information about the vehicle, such as its current edge, speed, acceleration, position, and neighboring vehicles.

- **Methods**: The class contains methods to set vehicle attributes, change lanes, check for collisions, and retrieve shape positions.

- **Utility Functions**: There are utility functions like `generate_vehicle_agent` to generate vehicle agents and `from_config` to create a vehicle agent from a configuration.
