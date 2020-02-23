from predictionManager import *
from dataManager import *
from reseau import *
from utils import *
import pickle
import argparse



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Créé et entraine un réseau sur l'ensemble des théorèmes spécifiés par le fichier th_valid, dont les prémisses sont données dans le dossier dep_dir. Ce réseau est ensuite sauvegarder dans le dossier save_network_dir")
	parser.add_argument("th_valid", help="chemin vers un fichier json contenant la liste des theoremes a utiliser pour l'entrainement et le test")
	parser.add_argument("dep_dir", help="dossier contenant les fichiers dep (dependances) des theoremes de th_valid")
	parser.add_argument("save_network_dir", help="dossier où sera stocké la sauvegarde du reseau")
	args = parser.parse_args()
	

	dm=DataManager(data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf")

	th_valid=json_to_list_or_dict(args.th_valid)

	x,labeled_y=dm.create_data(args.dep_dir,th_valid)
	res=Reseau()
	history = res.init_train(x,labeled_y)
	plot_history(history)

	pm=PredictionManager(dm,res)

	ensure_dir(args.save_network_dir)
	res.save(args.save_network_dir)
