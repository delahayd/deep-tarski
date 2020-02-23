from dataManager import *
from utils import *
import argparse
import pickle

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Converti un dossier contenant des fichiers zf en un dossier contenant les fichiers dep correspondant, ces derniers coniennent l'ensemble des noms des lemmes, axiomes et règles de réécritures apparaissant dans le fichiers zf associé")
	parser.add_argument("zf_dir", help="dissier contenant les fichiers zf a convertir")
	parser.add_argument("dep_dir", help="dossier de destination des fichiers dep")
	args = parser.parse_args()

	dm=DataManager(data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf")
	dm.zf_dir_to_dep_dir(args.zf_dir,args.dep_dir)

