from model import *
import pandas as pd


if __name__ == "__main__":
    DATAPATH = './ai/data'

    df = pd.read_csv(DATAPATH + "/user-data.csv", delimiter=",")
    df_out = pd.read_csv(DATAPATH + "/not-normalized.csv", delimiter=",")

    # Data matrix
    D = df.to_numpy()
    Y = df_out.to_numpy()[:, -1]

    training_data, testing_data = np.column_stack((D[:80, :], Y[:80])), np.column_stack((D[80:, :], Y[80:]))
    training_data = training_data.astype(np.float64)
    testing_data = testing_data.astype(np.float64)

    #optimal_hidden_layer_sizes, optimal_lr = createModel(training_data, testing_data)
    model = init_model([16])

    testModel(model, D, Y)