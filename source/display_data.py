from utils import *
import argparse
import pickle


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description= "Affiche un graphe correspondant à l'évolution des théorèmes prouvés en fonction du paramètre de la tactique (seuil ou top_k). Donne la proportion de théorèmes prouvés parmi ceux ayant servi lors de l'apprentissage et la proportion de théorème prouvés parmi les autres (prémisses complétement inconnues)")
	parser.add_argument("tactic_data_file", help="fichier pickle (créé par l'application d'une tactique)")
	parser.add_argument("th_proved_file", help="fichier json contenant les noms des théorèmes ptouvés")
	args = parser.parse_args()

with open(args.tactic_data_file, 'rb') as handle:
	datas = pickle.load(handle)

done,notdone,gaveup,ressourceout,timeout=get_tactic_data_from_file(datas)

get_prop_th_proved(args.th_proved_file,args.tactic_data_file)

get_tactic_data_from_file(datas,plot=True)
