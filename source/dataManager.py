from utils import *
import re
from decimal import Decimal



class DataManager :

	def __init__(self,data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf") :
		"""
		Gère la structure des dossiers contenant les dépendances/prémisses et les fichiers de preuves (utilisant struct_file (json)).
		Stocke les déclarations des théorèmes et axiomes explicités dans ax_th_def_file.
		Idem pour les règles de réécritures explicités dans rew_def_file.
		Nécessite de connaitre l'ensemble des symboles décrits par les règles de réécritures (utilise rew_type (json) pour cause de difficultés de parsing)
		L'ensemble de ces fichiers se trouvant dans le dossier data_dir.
		"""
		self.data_dir=data_dir
		self.rew_def_file=rew_def_file
		self.ax_th_def_file=ax_th_def_file
		self.struct_file=struct_file
		self.rew_type_list=rew_type_list
		self.rew_type_file=rew_type_file

		self.types=json_to_list_or_dict(data_dir+rew_type_list)

		self.rewrite_declaration = self.get_rewrites_definitions(data_dir+rew_def_file)
		self.ax_th_declaration = self.get_ax_th_definitions(data_dir+ax_th_def_file)

		self.ax_names,self.th_names = self.get_ax_th_names(data_dir+ax_th_def_file)

		self.struct_dict = json_to_list_or_dict(data_dir+struct_file)


	def get_all_th(self):
		"""
		Retourne le nom de tout les théorèmes connues
		"""
		return list(self.ax_th_declaration.keys())

	def get_chapter(self,theorem_to_find) :
		for chapter in self.struct_dict :
			for lemme in self.struct_dict[chapter] :
				if lemme==theorem_to_find :
					return chapter

	def get_rewrites_definitions(self,rew_def_file_path) :
		"""
		Parcourt le fichier rew_def_file contenant les déclarations des règles de réécriture
		retourne un dictonnaire dont les valeurs sont de la forme (symbole réécrit => règle de réécriture)
		"""
		rewrite = dict()

		rew_def_file=open(rew_def_file_path,"r")

		for line in rew_def_file.readlines():
			if line.startswith('rewrite') :
			    words=re.findall(r"[\w']+", line)
			    for w in words :
			        if w in self.types :
			            type_rew=w
			            break
			    try:
			        rewrite[type_rew]=line
			    except:
			        print(line)
			        break
			        
		rew_def_file.close()
		return rewrite

	def get_ax_th_definitions(self,ax_th_file_path) :
		"""
		Parcourt le fichier ax_th_file contenant les déclarations des axiomes et théorèmes
		retourne un dictonnaire dont les valeurs sont de la forme (nom du théorème ou axiome => déclaration)
		"""
		th_decl = dict()
		ax_th_file=open(ax_th_file_path,"r")
		balise="#name: "
		
		lines = ax_th_file.readlines()
		
		for i in range(len(lines)) :
			if lines[i].startswith(balise) :
			    name_size = len(lines[i])
			    th_decl[lines[i][len(balise):name_size-1]]=lines[i+1]
		return th_decl

	def get_ax_th_names(self,ax_th_file_path) :
		"""
		Retourne la liste des noms des axiomes et la liste des noms des theoremes presents dans le fichier ax_th_file_path
		"""
		is_axiom=False
		is_th=False

		ax_names = []
		th_names = []
		ax_th_file=open(ax_th_file_path,"r")
		balise="#name: "
		
		lines = ax_th_file.readlines()
		
		for i in range(len(lines)) :
			if lines[i].startswith("##axioms") :
				is_axiom=True
				is_th=False

			if lines[i].startswith("##theorems") :
				is_axiom=False
				is_th=True

			if lines[i].startswith(balise) and is_axiom :
				name_size = len(lines[i])
				ax_names.append(lines[i][len(balise):name_size-1])

			if lines[i].startswith(balise) and is_th :
				name_size = len(lines[i])
				th_names.append(lines[i][len(balise):name_size-1])
		return ax_names,th_names

	def dep_to_list(self,dep_file_path) :
		"""
		Lit un fichier de dépendance/prémisse
		Renvoi ces informations sous forme de liste
		"""
		all_th=self.get_all_th()
		res=[]
		dep_file=open(dep_file_path,"r")
		for line in dep_file.readlines() :
		    line=line.replace("\n","")
		    line=line.replace("\r","")
		    if line.startswith("lemme :") :
		        for w in line.split(" ") :
		            if w in all_th :
		                res.append(w)
		    if line.startswith("rewrite :") :
		        for w in line.split(" ") :
		            if w in self.types :
		                res.append(w)
		dep_file.close()
		return res
		
	def dep_to_zf(self,lemme,dep_file_name,zf_file_name) :
		"""
		Convertit un fichier dep en file zf, necessite le nom du lemme correspondant au fichier dep pour pouvoir ecrire le but
		"""    
		dep_list=self.dep_to_list(dep_file_name)
		
		ensure_dir(zf_file_name)
		f=open(zf_file_name,"w+")
		f.write("include \"../tarski_term_def.zf\".\n")
		for dep in dep_list :
		    if dep in self.get_all_th() :
		        if dep==lemme :
		            f.write("#include itself\n")
		        else :
		            f.write("#"+dep+"\n")
		            f.write(self.ax_th_declaration[dep])
		    if dep in self.types :
		        f.write(self.rewrite_declaration[dep])
		        
		f.write("goal "+th_declaration_to_text(self.ax_th_declaration[lemme]))
		f.close()
		
	def dep_dir_to_zf_dir(self,dep_dir,zf_dir) :
		"""
		Le premier dossier passé en parametre doit avoir une architecture correspondant aux informations du dataManager
		Convertit l'ensemble des fichiers dep du premier dossier en fichiers zf dans le second
		"""
		nb_convert=0
		nb_parcour=0
		if os.path.exists(dep_dir) :
		    for chapter in self.struct_dict :
		        ensure_dir(zf_dir+chapter)
		        for lemme in self.struct_dict[chapter] :
		            nb_parcour+=1
		            if os.path.exists(dep_dir+chapter+"/"+lemme+".dep") :
		                self.dep_to_zf(lemme,dep_dir+chapter+"/"+lemme+".dep",zf_dir+chapter+"/"+lemme+".zf")
		                nb_convert+=1
		            print("done :",nb_convert,"progress :",round(nb_parcour/len(self.get_all_th())*100,2),"%")
		    print("nb_file_converted = "+str(nb_convert))
		else :
		    print("no such directory : "+dep_dir)
		    
	def write_dep(self,th_dep,rew_dep,dep_file):
		"""
		Ecrit le fichier dep a partir de la liste des axiomes et lemmes, et de la liste des regles de reecritures donnees
		"""
		with open(dep_file,"w+") as dep_f :
		    dep_f.write("lemme :")
		    for th in list(set(th_dep)) :
		        dep_f.write(" "+th)
		        
		    dep_f.write("\nrewrite :")
		    for rew in list(set(rew_dep)) :
		        dep_f.write(" "+rew)
		    
	def dot_to_dep(self,dot_file,dep_file) :
		"""
		convertit un fichier dot en fichier dep
		"""
		th_dep=[]
		rew_dep=[]
		ensure_dir(dep_file)
		with open(dot_file,"r") as dot_f :
		    lines = dot_f.readlines()
		    for line in lines :
		        for word in self.types :
		            if "\\\"Label"+word+"\\\"" in line :
		                rew_dep.append(word)
		        for word in self.get_all_th() :
		            if "\\\"Label"+word+"\\\"" in line :
		                th_dep.append(word)
		self.write_dep(th,rew,dep_file)
		
	def zf_to_dep(self,zf_file,dep_file) :
		"""
		convertit un fichier zf en fichier dep
		"""
		th_dep=[]
		rew_dep=[]
		ensure_dir(dep_file)
		with open(zf_file,"r") as zf_f :
		    lines = zf_f.readlines()
		    for line in lines :
		        for word in self.types :
		            if "\"Label"+word+"\"" in line :
		                rew_dep.append(word)
		        for word in self.get_all_th() :
		            if "\"Label"+word+"\"" in line :
		                th_dep.append(word)
		self.write_dep(th_dep,rew_dep,dep_file)
		
	def zf_dir_to_dep_dir(self,zf_dir,dep_dir) :
		"""
		Le premier dossier passé en parametre doit avoir une architecture correspondant aux informations du dataManager
		Convertit l'ensemble des fichiers dep du premier dossier en fichiers zf dans le second
		"""
		nb_convert=0
		nb_parcour=0
		if os.path.exists(zf_dir) :
		    for chapter in self.struct_dict :
		        ensure_dir(dep_dir+chapter)
		        for lemme in self.struct_dict[chapter] :
		            nb_parcour+=1
		            if os.path.exists(zf_dir+chapter+"/"+lemme+".zf") :
		                self.zf_to_dep(zf_dir+chapter+"/"+lemme+".zf",dep_dir+chapter+"/"+lemme+".dep")
		                nb_convert+=1
		            print("done :",nb_convert,"progress :",round(nb_parcour/len(self.get_all_th())*100,2),"%")
		    print("nb_file_converted = "+str(nb_convert))
		else :
		    print("no such directory : "+dep_dir)

		
	def create_data(self,dep_dir_path,th_valid) :
		"""
		    retourne deux listes :
				x contenant les énoncés des théorèmes dont le nom appartient à la liste theorem_list
				y contenant des listes de 0 et 1, si dans la liste d'indice i la valeur d'indice j est 1, cela indique que la prémisse j (dans le multilabel_binarizer) est nécessaires au théorème d'indice i dans la liste x
    	"""
		x,labeled_y=[],[]
		for chapter in self.struct_dict :
		    for lemme in self.struct_dict[chapter] :
		        if th_valid is None or lemme in th_valid :
		            index = self.ax_th_declaration[lemme].find("]")
		            x.append(th_declaration_to_text(self.ax_th_declaration[lemme]))
		            labeled_y.append(self.dep_to_list(dep_dir_path+chapter+"/"+lemme+".dep"))

		return x,labeled_y

