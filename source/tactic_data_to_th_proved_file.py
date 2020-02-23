from utils import *
import argparse
import pickle


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Converti un fichier data (créé par un des scripts tactique) en un fichier contenant la liste des noms des théorèmes prouvés par cette tactique")
	parser.add_argument("tactic_data_file", help="fichier pickle (créé par l'application d'une tactique)")
	parser.add_argument("th_proved_file", help="fichier json dans lequel sera stocké les noms des theoremes prouvés")
	args = parser.parse_args()

with open(args.tactic_data_file, 'rb') as handle:
	datas = pickle.load(handle)

done,notdone,gaveup,ressourceout,timeout=get_tactic_data_from_file(datas)

list_or_dict_to_json(done,args.th_proved_file)


