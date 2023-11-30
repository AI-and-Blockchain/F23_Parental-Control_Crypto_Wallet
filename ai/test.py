from ai import model as fedImp
import numpy as np
import pandas as pd


if __name__ == "__main__":
    DATAPATH = './ai/data'

    df = pd.read_csv(DATAPATH + "/user-data.csv", delimiter=",")
    df_out = pd.read_csv(DATAPATH + "/not-normalized.csv", delimiter=",")

    # Data matrix
    D = df.to_numpy()
    Y = df_out.to_numpy()[:, -1]

    mean = np.mean(D, axis=0)
    std = np.std(D, axis=0)
    print(mean, std)