from predictionManager import *
from zipper_utils import *
import itertools
from shutil import copyfile
import argparse

def tactic_top_k(predictionManager,zf_dir_path,list_of_lemme,k=1,k_max=None,timeout=30,mem_limit=4000) :

    if k_max is None :
    	k_max=len(predictionManager.reseau.binarizer.classes_)
    
    if list_of_lemme is None :
        list_of_lemme = predictionManager.dataManager.th_names
    
    if not(list_of_lemme and k < k_max) :
        return []
    
    global zipper_exec_time
    print("size_of_echantillon =",len(list_of_lemme))
    print("starting")
    
    print("create files")

    copyfile(pm.dataManager.data_dir+pm.dataManager.rew_type_file, zf_dir_path+pm.dataManager.rew_type_file)

    for chapter in predictionManager.dataManager.struct_dict :
        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
	            zf_file=zf_dir_path+predictionManager.dataManager.get_chapter(lemme)+"/"+lemme+".zf"
	            predictionManager.th_name_pred_top_k_to_zf_file(lemme,zf_file,k=k)
                
    print("file created")
                
    threads=[]

    for chapter in predictionManager.dataManager.struct_dict :

        zipper_exec_time[chapter]=dict()

        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
                threads.append(Zipperposition(zf_dir_path,chapter,lemme,timeout,mem_limit))


    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()
    
    done,notdone,gaveup,ressourceout,timeout = get_zipper_stat(zipper_exec_time)
    
    print("Actual k : "+str(k))
    print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))

    data_list = tactic_top_k(predictionManager,zf_dir_path,notdone,k+k//10+1,k_max)
    return [[k,done,notdone,gaveup,ressourceout,timeout]]+data_list


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Technique des k plus grandes valeurs : Utilise le réseau sauvegardé dans le dossier network_save pour prédire les prémisses de l'ensemble des théorèmes du fichiers ax_th_def.zf. A chaque itération, génére, a partir des prémisses prédites et d'un k donné, des fichiers zf, stockés dans le dossier zf_dir. Zipperposition est appelé sur l'ensemble des zf générés, la prochaine itération ne s'applique que sur les théorèmes non prouvés par les itérations précédentes.")
	parser.add_argument("network_save", help="dossier contenant la sauvegarde du reseau a utiliser")
	parser.add_argument("zf_dir", help="dossier de destination des fichiers .zf generes")
	parser.add_argument("save_data_file", help="fichier de sauvegarde des donnees resultant de la tactique")
	parser.add_argument("-ki","--k_init",default=0, help="nombre de premisses selectionnees pour la premiere iteration", type=int)
	parser.add_argument("-km","--k_max", help="nombre maximal de premisses selectionnees pour la derniere iteration (par defaut = nombre de premisses connues par le reseau, type=int)", type=int)
	parser.add_argument("-t","--timeout", default=30, help="temps alloué par théorème à zipperposition", type=int)
	parser.add_argument("-mem","--mem_limit", default=4000, help="mémoire alloué par théorème à zipperposition", type=int)
	args = parser.parse_args()

		

	dm=DataManager(data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf")
	res=Reseau()
	res.load(args.network_save)
	pm=PredictionManager(dm,res)
	k_max=None
	if args.k_max :
		k_max=args.k_max
	ensure_dir(args.zf_dir)
	datas=tactic_top_k(pm,args.zf_dir,None,args.k_init,k_max,args.timeout,args.mem_limit)
	with open(args.save_data_file, "wb") as fp:
			pickle.dump(datas, fp)
	done,notdone,gaveup,ressourceout,timeout=get_tactic_data_from_file(datas)
