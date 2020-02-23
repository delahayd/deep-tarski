from zipper_utils import *
import argparse


def zipper(zf_dir_path,struct_file,th_to_prove_file=None,timeout=30,mem_limit=4000):

	struct_dict = json_to_list_or_dict(struct_file)


	threads=[]

	for chapter in struct_dict :
	    
		zipper_exec_time[chapter]=dict()

		if th_to_prove_file is None :
			for lemme in struct_dict[chapter] :
				threads.append(Zipperposition(zf_dir_path,chapter,lemme,timeout,mem_limit))
		else :
			th_to_prove= json_to_list_or_dict(th_to_prove_file)
			for lemme in struct_dict[chapter] :
				if lemme in th_to_prove :
					threads.append(Zipperposition(zf_dir_path,chapter,lemme,timeout,mem_limit))

	for i in range(len(threads)):
	    threads[i].start()

	for i in range(len(threads)):
	    threads[i].join()

	print("done")

	return get_zipper_stat(zipper_exec_time)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Appel Zipperposition sur l'ensemble des théorèmes (ou un sous ensemble spécifié par th_to_prove_file) du dossier zf_dir (structuré tel qu'indiqué dans le fichier config_struct), stocke la liste des théorèmes prouvés dans th_valid_file")
	parser.add_argument("zf_dir", help="dossier contenant les fichiers de preuves")
	parser.add_argument("th_valid_file", help="fichier dans lequel seront stockés les noms des théorèmes ainsi prouvés (json)")
	parser.add_argument("config_struct", help="fichier spécifiant la structure du contenu du dossier zf_dir")
	parser.add_argument("-ttp","--th_to_prove_file", help="fichier contenant les noms des theoremes a traiter par le script")
	parser.add_argument("-t","--timeout", default=30, help="temps alloué par théorème à zipperposition", type=int)
	parser.add_argument("-mem","--mem_limit", default=4000, help="mémoire alloué par théorème à zipperposition", type=int)
	args = parser.parse_args()

	(done,notdone,gaveup,ressourceout,timeout)=zipper(args.zf_dir,args.config_struct,args.th_to_prove_file,args.timeout,args.mem_limit)
	list_or_dict_to_json(done,args.th_valid_file)
	print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))
