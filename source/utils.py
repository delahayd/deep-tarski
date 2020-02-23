import json
from scipy import stats
import os
import re
import itertools
import matplotlib.pyplot as plt
import pickle


def ensure_dir(file_path):
	"""
	Créé l'ensemble des dossier présents dans le chemin du fichier (ou dossier) donné si nécessaire. 
	"""
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)

def list_or_dict_to_json(list_or_dict,file_path):
    with open(file_path, 'w') as file:
        file.write(json.dumps(list_or_dict))
        
def json_to_list_or_dict(file_path):
    with open(file_path, 'r') as file:
        list_or_dict = json.loads(file.read())
    return list_or_dict

def parse_special_characters(text) :
	text_cpy=text[:]
	for i in range(len(text_cpy)) :
		text_cpy[i]=re.sub(r'([-<=>!]+)', r' \1 ', text_cpy[i])
		text_cpy[i]=re.sub(r'([&|]+)', r' \1 ', text_cpy[i])
		text_cpy[i]=re.sub(r'([~]+)', r' \1 ', text_cpy[i])
		text_cpy[i]=re.sub(r'([()])', r' \1 ', text_cpy[i])
	return text_cpy

def plot_history(history):
	"""
	Prend l'historique de l'apprentissage (retour de la méthode "fit" du modele)
	Affiche l'évolution de la top_k_categorical_accuracy et de la loss du réseau sur les données de test et d'entrainement, lors de l'apprentissage
	"""
	# summarize history for accuracy
	plt.plot(history.history['top_k_categorical_accuracy'])
	plt.plot(history.history['val_top_k_categorical_accuracy'])
	plt.title('model accuracy')
	plt.ylabel('accuracy')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.show()
	# summarize history for loss
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.show()



def write_ax_th_def(ax_th_declaration,ax_th_file_path) :
	"""
	Créé ou écrase le fichier ax_th_file_path pour y inscrire, au format reconnu par le DataManager, les axiomes ou théorèmes énoncés dans le dictonnaire ax_th_declaration (ses valeurs étant de la forme : nom de l'axiome ou théorème => énoncé)
	"""
	all_th_file=open(all_th_file_path,"w")
	
	for th in ax_th_declaration :
	    all_th_file.write("#"+th+"\n")
	    all_th_file.write(ax_th_declaration[th]+"\n")
	    
	all_th_file.close()

def types_to_list(types_list,rew_type_file_path) :
	"""
	lit le fichier contenant le typages des symboles de régles de réécriture. (ex : val Bet : point -> point -> point -> prop.) pour renvoyer une liste contenant les symboles en question (nécessite la suppression de certains symboles à la main (ex : val point : type.) n'est pas utilisé en tant que prémisse comme les autres symboles)
	"""
	types=[]
	with open(rew_type_file_path,"r") as file :
	    for line in file.readlines() :
	        if line.startswith("val") :
	            words = line.split(" ")
	            types.append(words[1])
	return types


def th_declaration_to_text(th_declaration) :
		"""
		Prend un énoncé d'axiome ou théorème et le renvoi après avoir enlevé "assert" et retour à la ligne, si il possède un label (détecté par un "]") renvoie la chaîne de charactère après le symbole "] "
		"""
		index = th_declaration.find("]")
		if index >= 0 :
		    return th_declaration[index+2:].replace("\n","")
		else :
		    return th_declaration.replace("assert ","").replace("\n","")


def occurence_of_classes(y) :
	"""
	Prend en entré la liste y renvoyé par la méthode DataManager.create_data (une liste contenant des listes de même taille à valeurs 0 et 1)
	Retourne une liste contenant le nombre de fois qu'apparait chaque prémisse (compte le nombre de 1 à l'indice i dans l'ensemble des listes de y)
	"""
	res=[0 for i in range(len(y[0]))]
	for vect in y :
		for i in range(len(vect)) :
			if vect[i]==1 :
				res[i]+=1
	return res

def display_balance_of_classes(y) :
	"""
	Prend en entré la liste y renvoyé par la méthode DataManager.create_data (une liste contenant des listes de même taille à valeurs 0 et 1)
	Trace la courbe des occurences de classes dans l'ordre décroissant.
	"""
	oc = occurence_of_classes(y)

	print(stats.describe(oc))

	
	oc=[value for value in oc]
	plt.plot(range(len(y[0])), sorted(oc,reverse=True), label = "nombre d'occurences")
	plt.show()


def get_tactic_data_from_file(datas,plot=False) :
	"""
	Prend en entre un fichier data (retour d'une des tactiques)
	Retourne la liste des noms des theoremes 
	"""
	seuil=[]
	done=[]
	notdone=[]
	gaveup=[]
	ressourceout=[]
	timeout=[]
	for i in range(len(datas)) :
		seuil.append(datas[i][0])
		done.append(len(list(itertools.chain.from_iterable([data[1] for data in datas[:(i+1)]]))))
		notdone.append(len(datas[i][2]))
		gaveup.append(len(datas[i][3]))
		ressourceout.append(len(datas[i][4]))
		timeout.append(len(datas[i][5]))
	if plot :
		x=seuil
		y1=done
		y2=notdone
		y3=gaveup
		y4=ressourceout
		y5=timeout
		plt.plot(x,y1,linewidth=2.0,label = "done")
		plt.plot(x,y3,linewidth=2.0,label = "gave_up")
		plt.plot(x,y4,linewidth=2.0,label = "ressource_out")
		plt.plot(x,y5,linewidth=2.0,label = "time_out")
		plt.xlim(x[0]+0.01,x[-1]-0.01)
		plt.legend()
		plt.show()
	return list(itertools.chain.from_iterable([data[1] for data in datas[:(len(datas))]])),datas[len(datas)-1][2],datas[len(datas)-1][3],datas[len(datas)-1][4],datas[len(datas)-1][5]


def get_prop_th_proved(th_proved_json_file,data_pickle_file):
	"""
	Prend en parametre un fichiers json, contenant une liste de nom de theoremes, et un fichier data (retour d'une des tactiques)
	Retourne les proportions de theoremes prouvés appartenant et n'appartenant pas à la liste donnée
	"""

	th_to_test = json_to_list_or_dict(th_proved_json_file)

	with open(data_pickle_file, 'rb') as handle:
		th_proved = pickle.load(handle)

	done,notdone,gaveup,ressourceout,timeout = get_tactic_data_from_file(th_proved)

	th_already_proved=0
	new_th_proved=0

	th_not_proved = list(set(done+notdone)-set(th_to_test))

	for th in done :
		if th in th_to_test :
			th_already_proved+=1
		else :
			new_th_proved+=1

	print("Proportion de preuves effectuées parmis les anciens théorèmes prouvés :",th_already_proved/len(th_to_test),"\nProportion de preuves effectuées parmis les anciens théorèmes non prouvés",new_th_proved/len(th_not_proved))
	return th_already_proved/len(th_to_test),new_th_proved/len(th_not_proved)
