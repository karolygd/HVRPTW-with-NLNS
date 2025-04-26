from sklearn.cluster import DBSCAN
import vrplib
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import math

instance_name = "RC1_2_1.txt"
instance = vrplib.read_instance(f"instances_200/{instance_name}", instance_format="solomon")
# save depot information:
depot_demand = instance['demand'][0]
depot_service_time = instance['service_time'][0]
depot_time_window = instance['time_window'][0]
instance_coords = instance['node_coord'][1:] # remove depot

# plt.rcParams["font.family"] = "serif"
# plt.title(f"{instance_name[:-4]} instance with 200 customers")
# plt.plot(instance_coords[:, 0], instance_coords[:, 1], 'o', color='red', label='customers')
# plt.plot(instance['node_coord'][0][0], instance['node_coord'][0][1], 'o', color='blue', label='depot')
# plt.legend()
# plt.show()

for key in ['demand', 'time_window', 'service_time']:
    instance[key] = instance[key][1:]

# cluster the customers/nodes
# C1 = eps=7
# C2 = eps=9
clustering = DBSCAN(eps=8, min_samples=5).fit(instance_coords) # higher min_samples or lower eps indicate higher density necessary to form a cluster.
labels = clustering.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print("Estimated number of clusters: %d" % n_clusters_)
print("Estimated number of noise points: %d" % n_noise_)

unique_clusters = np.unique([label for label in labels if label != -1])
num_customers = len(labels)
print("num_customers: ", num_customers)
num_clusters = len(unique_clusters)

cluster_sizes = {c: np.sum(labels == c) for c in unique_clusters}
num_clustered_customers = sum(cluster_sizes.values())
num_random_customers = 200-num_clustered_customers

percentage_clustered_customers = num_clustered_customers/200
percentage_random_customers = num_random_customers/200

print(f"number of clustered customers: {num_clustered_customers}, percentage to remove: {percentage_clustered_customers:.2f}%")
print(f"number of random customers: {num_random_customers}, percentage to remove: {percentage_random_customers:.2f}%")

remaining_customers = 0
clustered_customers_to_remove = int((num_customers - 100)*percentage_clustered_customers)
print("clustered customers to remove: ", clustered_customers_to_remove)
if clustered_customers_to_remove <= 0:
    print("Already at or below 100 customers. No removal needed.")
else:
    cluster_sizes = {c: np.sum(labels == c) for c in unique_clusters}
    #do not do it by sorted clusters, better do it as their random positions already
    #sorted_clusters = sorted(cluster_sizes.items(), key=lambda x: x[1], reverse=True)
    clusters = list(cluster_sizes.keys())
    random.shuffle(clusters)
    shuffled_clusters = [(cluster, cluster_sizes[cluster]) for cluster in clusters]
    print("shuffled clusters: ", shuffled_clusters)
    removed_clusters = []
    remaining_customers = clustered_customers_to_remove

    for cluster, size in shuffled_clusters: #cluster_sizes.items():
        if remaining_customers - size >= 0:
            # full-cluster removal
            removed_clusters.append(cluster)
            remaining_customers -= size
            print("cluster: ", cluster, "size of cluster to remove: ", size)
        if remaining_customers <= 0:
            break  # Stop when we hit 100 customers

    # 6. Remove selected clusters from instance
    mask = np.isin(labels, removed_clusters, invert=True)  # Keep only non-removed clusters
    instance_coords = instance_coords[mask]
    labels = labels[mask]
    for key in ['demand', 'time_window', 'service_time']:
        instance[key] = instance[key][mask]

print("remaining customers: ", remaining_customers)
# In case we need to remove single-customers:
print("random customers to remove: ", (num_customers - 100)*percentage_random_customers, "int: ", int((num_customers - 100)*percentage_random_customers))
random_customers_to_remove = math.ceil(remaining_customers + (num_customers - 100)*percentage_random_customers)
if random_customers_to_remove > 0:
    print(f"randomly removing {random_customers_to_remove} customers")
    nodes = [i for i in range(0, len(instance_coords))]
    nodes_to_remove = random.sample(nodes, random_customers_to_remove)
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
plt.title(f"{instance_name[:-4]} instance with 100 customers")
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