# this file is meant to connect the webserver to the FedLab and blockchain components

# imports
# from ..blockchain import contract_test as contract

MEAN = [0.00133942, -0.1878125,  -0.40564301, -0.31044999, -0.23087019], 
STD_DEV = [0.01047967, 0.67000948, 0.63722758, 0.60562119, 0.36480168]

# region fedlab
from ai import model as fedImp
model = fedImp.init_model()

def classifyTransaction(inparr):
    outpTens = fedImp.computePoint(model, MEAN, STD_DEV, inparr)
    if (outpTens == -1): return {"code": -1, "msg": "ERROR!"}
    
    outp = outpTens.numpy()
    if (outp == 1): return {"code": 1, "msg": "This transaction is good!"}
    elif (outp == 2): return {"code": 2, "msg": "This transaction is alright, but perhaps watch your spending..."}
    elif (outp == 3): return {"code": 3, "msg": "This transaction is reckless, please reconsider!"}
    else: return {"code": -1, "msg": f"unknown classification '{outp}'!"}

a = [0.00016591157871593997,-0.4196428571428571,-0.9765157558835261,-0.9703491389589427,-0.33342069786393624]  # 1
b = [0.0005280176532643606,-0.4196428571428571,-0.9759910346268543,-0.9322903614990381,-0.49961232113912235]  # 1
c = [9.351468739346202e-05,-0.4196428571428571,-0.979564362641746,-0.798657369127207,-0.8020313981902603]  # 3

for i in [a,b,c]:
    outp = fedImp.computePoint(model, MEAN, STD_DEV, i)
    print("OUTPUT", outp)

# endregion
