
import numpy as np
import os
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import itertools
from torch.utils.data import DataLoader, TensorDataset, random_split
from fedlab.contrib.algorithm.basic_client import SGDSerialClientTrainer
from fedlab.contrib.algorithm.basic_server import SyncServerHandler
from fedlab.core.standalone import StandalonePipeline
from fedlab.utils.functional import evaluate
from sklearn.model_selection import KFold


class SGDSerialClientTrainerTensor(SGDSerialClientTrainer):
    def local_process(self, model_parameters, client_data):
        if isinstance(client_data, torch.utils.data.dataset.Subset):
            data_loader = DataLoader(client_data, batch_size=self.batch_size, shuffle=False)
            pack = self.train(model_parameters, data_loader)
            self.cache.append(pack)
        else:
            print(f"Invalid data format for client data, type {type(client_data)}")



class DeepMLP(nn.Module):
    def __init__(self, input_size=0, hidden_layer_sizes=[0, 0], output_size=0):
        super(DeepMLP, self).__init__()
        layers = []

        # Input layer
        layers.append(nn.Linear(input_size, hidden_layer_sizes[0]))
        layers.append(nn.ReLU())

        # Hidden layers
        for i in range(len(hidden_layer_sizes)-1):
            layers.append(nn.Linear(hidden_layer_sizes[i], hidden_layer_sizes[i+1]))
            layers.append(nn.ReLU())

        # Output layer
        layers.append(nn.Linear(hidden_layer_sizes[-1], output_size))

        # Combine all layers
        self.layers = nn.Sequential(*layers)

    # Feed Forward.
    def forward(self, x):
        return self.layers(x)


class EvalPipeline(StandalonePipeline):
    def __init__(self, handler, trainer, test_loader, client_data, show_data=True):
        super().__init__(handler, trainer)
        self.show_data = show_data
        self.test_loader = test_loader
        self.client_data = client_data
        self.loss, self.acc = [], []
        self.ax = None
        self.ax2 = None

    def getLoss(self):
        return self.loss
    
    def getAcc(self):
        return self.acc

    def main(self):
        t = 0
        while not self.handler.if_stop:
            model_parameters = self.handler.downlink_package[0]

            for client_id in self.handler.sample_clients():
                client_data = self.client_data[client_id]
                self.trainer.local_process(model_parameters, client_data)
            
            for pack in self.trainer.uplink_package:
                self.handler.load(pack)
            
            loss, acc = evaluate(self.handler.model, 
                                nn.CrossEntropyLoss(),
                                self.test_loader)
            if (self.show_data):
                print(f"Round {t}, Loss {round(loss,4)}, Test Acc {round(acc,4)}")

            self.loss.append(loss)
            self.acc.append(acc)
            
            t += 1

    def show(self):
        plt.figure(figsize=(8,4.5))
        self.ax = plt.subplot(1,2,1)
        self.ax.plot(np.arange(len(self.loss)), self.loss)
        self.ax.set_xlabel("Communication Round")
        self.ax.set_ylabel("Loss")
        
        self.ax2 = plt.subplot(1,2,2)
        self.ax2.plot(np.arange(len(self.acc)), self.acc)
        self.ax2.set_xlabel("Communication Round")
        self.ax2.set_ylabel("Accuracy")


# Just like in the lab, we need to implement client-side training and server side aggregation.
# I simply copy and pasted from my code:

def run(
    training_data: np.ndarray,
    test_data: np.ndarray,
    Y_train: np.ndarray,
    Y_test: np.ndarray,
    input_size: int, 
    hidden_layer_sizes: list,
    output_size: int,
    show_data=True,
    epochs=1,
    batch_size=16,
    eta=0.04,
    cuda=False,
    num_rounds=100,
    num_clients=8
):
    # Convert numpy arrays to PyTorch tensors
    training_data_tensor = torch.from_numpy(training_data).float()
    test_data_tensor = torch.from_numpy(test_data).float()
    output_train_tensor = torch.from_numpy(Y_train).long()
    output_test_tensor = torch.from_numpy(Y_test).long()

    model = DeepMLP(input_size, hidden_layer_sizes, output_size)

    # Create an instance of the trainer for serial training on clients
    trainer = SGDSerialClientTrainerTensor(model=model,
                                    num_clients=num_clients,
                                    cuda=cuda
                                    )


    # Once we actually HAVE the data, you can set it up as follows:
    trainer.setup_dataset(training_data_tensor)

    # Setup optimizer with the defined epochs, batch size, and learning rate
    trainer.setup_optim(epochs=epochs,
                        batch_size=batch_size,
                        lr=eta)

    handler = SyncServerHandler(model=model, 
                                global_round=num_rounds,
                                sample_ratio=0.1)

    train_dataset = TensorDataset(training_data_tensor, output_train_tensor)
    test_dataset = TensorDataset(test_data_tensor, output_test_tensor)

    client_data_size = len(training_data_tensor) // num_clients
    client_data = random_split(train_dataset, [client_data_size] * num_clients)

    test_loader = DataLoader( test_dataset, batch_size=batch_size)
    standalone_eval = EvalPipeline(handler=handler, trainer=trainer, test_loader=test_loader, client_data=client_data, show_data=show_data)
    standalone_eval.main()

    return standalone_eval.acc[-1], model



def cross_validation(
    training_data: np.ndarray, 
    input_size: int, 
    output_size: int,
    neuron_ranges=[16, 32, 64], 
    learning_rate_ranges=[0.01, 0.001]
):
    hyperparameter_combinations = itertools.product(neuron_ranges, learning_rate_ranges)
    best_performance = float('inf')
    best_params = None

    for neurons, lr in hyperparameter_combinations:
        kf = KFold(n_splits=5)
        fold_performances = []

        for train_index, val_index in kf.split(training_data):
            X_train_fold, X_valid_fold = training_data[train_index], training_data[val_index]

            # Assuming 'run' function is adapted for training and returns a trained model and its performance
            acc, _ = \
                run (
                    training_data=X_train_fold[:,:-1], 
                    test_data=X_valid_fold[:,:-1],
                    Y_train=X_train_fold[:,-1],
                    Y_test=X_valid_fold[:,-1],
                    input_size=input_size,
                    hidden_layer_sizes=neuron_ranges,
                    output_size=output_size,
                    eta=lr,
                    show_data=False
                )

            # Evaluate the trained model on the validation set
            fold_performances.append(acc)

        average_performance = np.mean(fold_performances)

        if average_performance < best_performance:
            best_performance = average_performance
            best_params = (neurons, lr)

    return best_params


def createModel(training_data, testing_data, input_size=5, output_size=4):
    best_params = cross_validation(
                    training_data=training_data, 
                    input_size=input_size,
                    output_size=output_size
                )

    print(best_params)


    optimal_hidden_layer_sizes = [best_params[0]]
    optimal_lr = best_params[1] 

    # Train the model
    best_accuracy, model = run(
        training_data=training_data[:,:-1],
        test_data=testing_data[:,:-1],
        Y_train=training_data[:,-1],
        Y_test=testing_data[:,-1],
        input_size=5,
        hidden_layer_sizes=optimal_hidden_layer_sizes,
        output_size=4,
        epochs=1,  # Set your optimal number of epochs
        batch_size=16,
        eta=optimal_lr,
        cuda=False,
        num_rounds=200,
        num_clients=8,
        show_data=False
    )

    print(best_accuracy)

    # Assuming the model is named 'model' and is part of your 'run' function or returned by it
    torch.save(model.state_dict(), './ai/model.pth')
    return best_params


def init_model(optimal_hidden_layer_sizes = [32, 32], input_size=5, output_size=4):
    # Initialize the model
    model = DeepMLP(input_size, optimal_hidden_layer_sizes, output_size)

    # Load the saved model parameters
    model.load_state_dict(torch.load('./ai/model.pth'))

    # Set the model to evaluation mode
    model.eval()
    return model


# # Example: Predicting for some new data
# new_data = torch.tensor([your_new_data_here], dtype=torch.float32)
# with torch.no_grad():  # Disable gradient calculation for inference
#     prediction = model(new_data)


def testModel(model, features, labels):
    # Convert NumPy arrays to PyTorch tensors
    features_tensor = torch.tensor(features, dtype=torch.float32)
    labels_tensor = torch.tensor(labels, dtype=torch.float32)

    print(labels_tensor)
    print(features_tensor)

    for i in range(len(features_tensor)):
        feature, label = features_tensor[i], labels_tensor[i]
        with torch.no_grad():
            output = model(feature)

        print(torch.argmax(torch.softmax(output, 0), 0), "==", label)


def computePoint(model, x = []):
    if (len(x) != 5): return -1

    data_point = torch.tensor(x, dtype=torch.float32)

    with torch.no_grad():
        output = model(data_point)

    # print(output)
    testModel(model)

    return torch.argmax(torch.softmax(output, 0), 0)
