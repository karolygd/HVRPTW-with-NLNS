from sklearn.cluster import DBSCAN
import vrplib
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd

instance_name = "C2_2_1.txt"
instance = vrplib.read_instance(f"instances_200/{instance_name}", instance_format="solomon")
# save depot information:
depot_demand = instance['demand'][0]
depot_service_time = instance['service_time'][0]
depot_time_window = instance['time_window'][0]
instance_coords = instance['node_coord'][1:] # remove depot

# plt.rcParams["font.family"] = "serif"
# plt.title(f"C1_2_1 instance with 200 customers")
# plt.plot(instance_coords[:, 0], instance_coords[:, 1], 'o', color='red', label='customers')
# plt.plot(instance['node_coord'][0][0], instance['node_coord'][0][1], 'o', color='blue', label='depot')
# plt.legend()
# plt.show()

# cluster the customers/nodes
# C1 = eps=7
# C2 = eps=9
clustering = DBSCAN(eps=7, min_samples=5).fit(instance_coords) # higher min_samples or lower eps indicate higher density necessary to form a cluster.
labels = clustering.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print("Estimated number of clusters: %d" % n_clusters_)
print("Estimated number of noise points: %d" % n_noise_)


# 1. Remove the customers that where labeled as noise (-1):
valid_indices = labels != -1  # True for non-noise points, False for noise
#print("instance cords before change ", len(instance_coords)) #200
instance_coords = instance_coords[valid_indices]
#print("instance cords after change ", len(instance_coords)) #197
labels = labels[valid_indices]
for key in ['demand', 'time_window', 'service_time']:
    #print(f"{key} before change ", len(instance[key])) #201
    instance[key] = np.array(instance[key])[1:][valid_indices]  # Remove depot, then filter
    #print(f"{key} after change ", len(instance[key])) #197
#debug:
# print(len(instance_coords))
# print(len(instance['demand']))
# print(labels)

unique_clusters = np.unique(labels)
num_customers = len(labels)
num_clusters = len(unique_clusters)

customers_to_remove = num_customers - 100
if customers_to_remove <= 0:
    print("Already at or below 100 customers. No removal needed.")
else:
    cluster_sizes = {c: np.sum(labels == c) for c in unique_clusters}
    # do not do it by sorted clusters, better do it as their random positions already
    #sorted_clusters = sorted(cluster_sizes.items(), key=lambda x: x[1], reverse=True)

    removed_clusters = []
    remaining_customers = num_customers

    for cluster, size in cluster_sizes.items():
        if remaining_customers - size >= 100:
            # full-cluster removal
            removed_clusters.append(cluster)
            remaining_customers -= size
            print("size of cluster to remove: ", size)
        if remaining_customers <= 100:
            break  # Stop when we hit 100 customers

    # 6. Remove selected clusters from instance
    mask = np.isin(labels, removed_clusters, invert=True)  # Keep only non-removed clusters
    instance_coords = instance_coords[mask]
    labels = labels[mask]
    for key in ['demand', 'time_window', 'service_time']:
        instance[key] = instance[key][mask]

    # In case we need to remove single-customers:
    if remaining_customers - 100 > 0:
        print(f"randomly removing {remaining_customers-100} customers")
        nodes = [i for i in range(0, len(instance_coords))]
        nodes_to_remove = random.sample(nodes, remaining_customers-100)
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
instance['num_customers'] = len(instance_coords)

print("len node_cord: ", len(instance['node_coord']))
print("len demand", len(instance['demand']))
# print(len(instance['edge_weight']))
# print("num_customers", instance['num_customers'])
#
# print(instance['node_coord'])
# print(instance['demand'])
# print(instance['time_window'])
# print(instance['service_time'])

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
plt.title(f"C2_2_1 instance with 100 customers")
plt.plot(instance_coords[:, 0], instance_coords[:, 1], 'o', color='red', label='customers')
plt.plot(instance['node_coord'][0][0], instance['node_coord'][0][1], 'o', color='blue', label='depot')
plt.legend()
plt.show()


"""
# PLotting clustered the instance
unique_labels = set(labels)
core_samples_mask = np.zeros_like(labels, dtype=bool)
core_samples_mask[clustering.core_sample_indices_] = True

plt.rcParams["font.family"] = "serif"
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = labels == k

    xy = instance_coords[class_member_mask & core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=6,
    )

    xy = instance_coords[class_member_mask & ~core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=6,
    )

plt.title(f"Estimated number of clusters: {n_clusters_}")
plt.show()
"""

