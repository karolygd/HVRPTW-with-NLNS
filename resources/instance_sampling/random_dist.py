import vrplib
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd

instance_name = "R1_2_1.txt"
instance = vrplib.read_instance(f"instances_200/{instance_name}", instance_format="solomon")
# save depot information:
depot_demand = instance['demand'][0]
depot_service_time = instance['service_time'][0]
depot_time_window = instance['time_window'][0]
instance_coords = instance['node_coord'][1:] # remove depot

plt.rcParams["font.family"] = "serif"
plt.title(f"{instance_name[:-4]} instance with 200 customers")
plt.plot(instance_coords[:, 0], instance_coords[:, 1], 'o', color='red', label='customers')
plt.plot(instance['node_coord'][0][0], instance['node_coord'][0][1], 'o', color='blue', label='depot')
plt.legend()
plt.show()

for key in ['demand', 'time_window', 'service_time']:
    instance[key] = instance[key][1:]

customers_to_remove = len(instance_coords)-100
if customers_to_remove > 0:
    print(f"randomly removing {customers_to_remove} customers")
    nodes = [i for i in range(0, len(instance_coords))]
    nodes_to_remove = random.sample(nodes, customers_to_remove)
    print(nodes_to_remove)
    mask = np.ones(len(instance_coords), dtype=bool)
    mask[nodes_to_remove] = False
    instance_coords = instance_coords[mask]
    for key in ['demand', 'time_window', 'service_time']:
        instance[key] = instance[key][mask]

# Save updated instance
instance['node_coord'] = np.vstack([instance['node_coord'][0], instance_coords])  # Add depot back
instance['demand'] = np.hstack([depot_demand, instance['demand']])
instance['time_window'] = np.vstack([depot_time_window, instance['time_window']])
instance['service_time'] = np.hstack([depot_service_time, instance['service_time']])

print("len node_cord: ", len(instance['node_coord']))
print("len demand", len(instance['demand']))

df_instance = pd.DataFrame({
    "x": [x[0] for x in instance['node_coord']],
    "y": [x[1] for x in instance['node_coord']],
    "node_coord": list(map(tuple, instance['node_coord'])),
    "demand": instance['demand'],
    "earliest_arrival": [x[0] for x in instance['time_window']],
    "latest_arrival": [x[1] for x in instance['time_window']],
    "service_time": instance['service_time']
})

print(df_instance.head())
df_instance.to_csv(f"../instances/training_instances/{instance_name[:-4]}_100.txt", index=False)

plt.rcParams["font.family"] = "serif"
plt.title(f"{instance_name[:-4]} instance with 100 customers")
plt.plot(instance_coords[:, 0], instance_coords[:, 1], 'o', color='red', label='customers')
plt.plot(instance['node_coord'][0][0], instance['node_coord'][0][1], 'o', color='blue', label='depot')
plt.legend()
plt.show()