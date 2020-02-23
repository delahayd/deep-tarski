from predictionManager import *
from dataManager import *
from reseau import *
from utils import *
import pickle
"""
dm=DataManager()

th_valid=json_to_list_or_dict("../resultat/geocoq_extract/th_proved.json")

x,labeled_y=dm.create_data("../resultat/geocoq_extract/dependencies/",th_valid)
res=Reseau()
history = res.init_train(x,labeled_y)
plot_history(history)

pm=PredictionManager(dm,res)

print(pm.eval_pred_top_k('cong3_bet_eq',"../resultat/geocoq_extract/dependencies/",k=25))
print(pm.eval_pred_seuil('cong3_bet_eq',"../resultat/geocoq_extract/dependencies/",seuil=0.2))
ensure_dir("./save_geocoq2/")
res.save("./save_geocoq2/")

"""


dm=DataManager()
res=Reseau()
res.load("./save_geocoq2/")
pm=PredictionManager(dm,res)

th_to_test=json_to_list_or_dict("../resultat/geocoq_extract/th_proved.json")

k_table,acc_table,prop_table=pm.test_multiple_top_k("../resultat/geocoq_extract/dependencies/",th_to_test)
#seuil_table,acc_table,prop_table=pm.test_multiple_seuil(1e-7,0.5,"../resultat/geocoq_extract/dependencies/",th_to_test)
#pm.th_string_pred_seuil_to_zf_file("forall (A B C A1 B1 C1 : point). Cong_3 A B C A1 B1 C1 => Cong_3 B A C B1 A1 C1.","./cong_3_swap.zf",seuil=0.05)
#pm.th_string_pred_top_k_to_zf_file("forall (A B C A1 B1 C1 : point). Cong_3 A B C A1 B1 C1 => Cong_3 B A C B1 A1 C1.","./cong_3_swap.zf",k=25)
#res.predict_top_k('forall (A B : point). A=B || A!=B.')

"""
import matplotlib.pyplot as plt
x=seuil_table
y1=acc_table
y2=prop_table
plt.plot(x,y1,linewidth=2.0,label = "proportion de theoreme dont l'ensemble des premisses sont predites (sur le nombre total de theoremes)")
plt.plot(x,y2,linewidth=2.0,label = "proportion du nombre moyen de premisses donnees par l'ensemble des predictions (sur le nombre total de premisses)")
plt.xlim(x[0]+0.01,x[-1]-0.01)
plt.legend()
plt.show()
"""
