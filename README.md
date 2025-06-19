# HVRPTW-with-NN-ALNS

This repository contains the implementation of an ALNS algorithm enhanced with a feed-forward neural network as the operator selection mechanism.

- artifacts: contains the feature scalers used for the input data of the neural network.
- experiments: contains the files corresponding to the ablation analysis and the hyperparameter tuning.
- resources: cointains files related to
  - datatypes: custom-made datatypes for the model (instance, node, operator, route, and solution)
  - instances: the benchmark instances and the training instances as .txt files
  - instance-sampling: the functions to reduce the 200 customer training instances
  - training_data: data used to train the neural network model
- results and logs: logs from the alns for analysis of the solutions
- src: main functions for the alns algorithm
  - alns_components: the neural network and helper functions for its implementation, operator selection mechanisms, adaptive customer removal, local search operators, function to set and update the temperature for simmulated annealing.
  - operators: remove and insert operators used in the alns
  - alns.py: structure of the alns algorithm
  - evaluation.py: functions to evaluate the solutions and perform feasibility checks.
  - initial_solution.py: savings algorithm
- main.py: setting of the instance and parameters to run the model.
