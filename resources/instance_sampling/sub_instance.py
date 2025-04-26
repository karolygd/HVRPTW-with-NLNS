# Take the customers taken for instance C1, C2, R1, and RC1 and replicate them for the remaining instances

import pandas as pd
import vrplib
import numpy as np

for i in [10]:
    instance_name = f"RC2_2_{i}.txt"
    instance_200 = vrplib.read_instance(f"instances_200/{instance_name}", instance_format="solomon")

    # customer set
    instance_name_100 = instance_name[:-10]+"1_2_1_100.txt"
    predefined_customers_df = pd.read_csv("../instances/training_instances/" + instance_name_100)

    node_coords_100 = predefined_customers_df[['x', 'y']].to_numpy()
    coord_to_earliest_arrival = {tuple(coord): tw[0] for coord, tw in zip(instance_200['node_coord'], instance_200['time_window'])}
    coord_to_latest_arrival = {tuple(coord): tw[1] for coord, tw in zip(instance_200['node_coord'], instance_200['time_window'])}
    print("coord --> earliest arrival: ",coord_to_earliest_arrival)
    print("coord --> latest arrival: ",coord_to_latest_arrival)

    # Convert (x, y) columns to tuples
    predefined_customers_df['coord_tuple'] = list(map(tuple, node_coords_100))

    predefined_customers_df['earliest_arrival'] = node_coords_100.tolist()  # Convert back to tuples
    predefined_customers_df['latest_arrival'] = node_coords_100.tolist()
    predefined_customers_df['earliest_arrival'] = predefined_customers_df['coord_tuple'].map(coord_to_earliest_arrival) #predefined_customers_df['earliest_arrival'].map(coord_to_earliest_arrival)  # Map based on (x, y)
    predefined_customers_df['latest_arrival'] = predefined_customers_df['coord_tuple'].map(coord_to_latest_arrival) #predefined_customers_df['latest_arrival'].map(coord_to_earliest_arrival)  # Map based on (x, y)
    # Create a mapping from (x, y) to time_window

    predefined_customers_df.drop(columns=['coord_tuple'], inplace=True)
    #print(predefined_customers_df[['x', 'y', 'earliest_arrival', 'latest_arrival']].head())

    # # Check the values where passed correctly
    # for _, row in predefined_customers_df.iterrows():
    #     coord_tuple = (row['x'], row['y'])
    #     expected_earliest = coord_to_earliest_arrival.get(coord_tuple, "Not Found")
    #     expected_latest = coord_to_latest_arrival.get(coord_tuple, "Not Found")
    #
    #     if expected_earliest != row['earliest_arrival'] or expected_latest != row['latest_arrival']:
    #         print(
    #         f"Coord: {coord_tuple} | DF Earliest: {row['earliest_arrival']} (Expected: {expected_earliest}) | DF Latest: {row['latest_arrival']} (Expected: {expected_latest})")

    predefined_customers_df.to_csv(f"../instances/training_instances/{instance_name[:-4]}_100.txt", index=False)


