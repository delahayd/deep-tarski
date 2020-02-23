import numpy as np
from dataManager import *
from reseau import *
from utils import *

class PredictionManager :
	def __init__(self,dataManager,reseau):
		self.dataManager=dataManager
		self.reseau=reseau

	def predict_seuil_th(self,theorem,seuil=0.05):
		return self.reseau.predict_seuil(self.dataManager.ax_th_declaration[theorem],seuil)

	def predict_top_k_th(self,theorem,k=5):
		return self.reseau.predict_top_k(self.dataManager.ax_th_declaration[theorem],k)

	def eval_pred_seuil(self,theorem,dep_dir_path,seuil=0.05) :
		pred_y = self.predict_seuil_th(theorem,seuil)

		pred_y_ones = np.where(pred_y==1)[0]


		labeled_y = self.dataManager.dep_to_list(dep_dir_path+self.dataManager.get_chapter(theorem)+"/"+theorem+".dep")
		y = self.reseau.binarizer.transform(np.array([labeled_y]))

		y_ones = np.where(y[0]==1)[0]

		compare = [1 if val in pred_y_ones else 0 for val in y_ones]

		if len(compare)==0 :
			compare=[0]
			
		if len(y_ones)==0 :
			compare=[1]	
		

		return (np.average(compare),len(pred_y_ones)/len(pred_y))

	def eval_pred_top_k(self,theorem,dep_dir_path,k=5) :
		pred_y = self.predict_top_k_th(theorem,k)

		pred_y_ones = np.where(pred_y==1)[0]


		labeled_y = self.dataManager.dep_to_list(dep_dir_path+self.dataManager.get_chapter(theorem)+"/"+theorem+".dep")
		y = self.reseau.binarizer.transform(np.array([labeled_y]))

		y_ones = np.where(y[0]==1)[0]

		compare = [1 if val in pred_y_ones else 0 for val in y_ones]

		if len(compare)==0 :
			compare=[0]
		if len(y_ones)==0 :
			compare=[1]	

		return (np.average(compare),len(pred_y_ones)/len(pred_y))

	def test_pred_seuil(self,dep_dir_path,ths_to_test,seuil=0.05) :
		"""
		Test les predictions du reseau sur l'ensemble (ou un sous ensemble) des theoremes connus
		Methode des seuils
		Prend :
		 le dossier contenant les fichiers .dep (architecture specifie dans le dataManager)
		 la liste des noms des theoremes a tester, doivent posseder leur fichier .dep (valeur = None : pour tester sur tout les theoremes)
		 la valeur du seuil
		"""
		sum_res=0
		size=0
		fail_size=0
		total_precision=None
		total_prop_classe=None
		for chapter in self.dataManager.struct_dict :
		    for lemme in self.dataManager.struct_dict[chapter] :
		        if ths_to_test is None or lemme in ths_to_test:
		            (res,prop_classe) = self.eval_pred_seuil(lemme,dep_dir_path,seuil)
		            if res==1 :
		                sum_res+=1
		            else :
		                if total_precision is None :
		                    total_precision=res
		                else :
		                    total_precision+=res
		                fail_size+=1
		            if total_prop_classe is None :
		                total_prop_classe=prop_classe
		            else :
		                total_prop_classe+=prop_classe
		            size+=1
		if total_precision is None :
		    total_precision=0
		if total_prop_classe is None :
		    total_prop_classe=0
		if fail_size==0 :
		    fail_size=1
		    total_precision=1
		return (sum_res/size,total_prop_classe/size,total_precision/fail_size)

	def test_pred_top_k(self,dep_dir_path,ths_to_test,k=5) :
	    """
        Test les predictions du reseau sur l'ensemble (ou un sous ensemble) des theoremes connus
        Methode top k
	    Prend :
	     le dossier contenant les fichiers .dep (architecture specifie dans le dataManager)
	     la liste des noms des theoremes a tester, doivent posseder leur fichier .dep (valeur = None : pour tester sur tout les theoremes)
	     la valeur de k
	    """
	    sum_res=0
	    size=0
	    fail_size=0
	    total_precision=None
	    total_prop_classe=None
	    for chapter in self.dataManager.struct_dict :
		    for lemme in self.dataManager.struct_dict[chapter] :
		        if ths_to_test is None or lemme in ths_to_test :
		            (res,prop_classe) = self.eval_pred_top_k(lemme,dep_dir_path,k)
		            if res==1 :
		                sum_res+=1
		            else :
		                if total_precision is None :
		                    total_precision=res
		                else :
		                    total_precision+=res
		                fail_size+=1
		            if total_prop_classe is None :
		                total_prop_classe=prop_classe
		            else :
		                total_prop_classe+=prop_classe
		            size+=1
	    if total_precision is None :
		    total_precision=0
	    if total_prop_classe is None :
		    total_prop_classe=0
	    if fail_size==0 :
		    fail_size=1
		    total_precision=1
	    return (sum_res/size,total_prop_classe/size,total_precision/fail_size)
	    
	    
	def test_multiple_seuil(self,min_seuil,max_seuil,dep_dir_path,ths_to_test) :
		seuil_table=[]
		acc_table=[]
		prop_table=[]
		seuil=max_seuil
		accuracy=0
		prop_classe=0.5
		while(accuracy < 1 and prop_classe < 1 and seuil > min_seuil) :
		    (accuracy,prop_classe,precision) = self.test_pred_seuil(dep_dir_path,ths_to_test,seuil)
		    seuil_table.append(seuil)
		    acc_table.append(accuracy)
		    prop_table.append(prop_classe)
		    print(seuil,accuracy,prop_classe)
		    seuil=seuil/2
		return seuil_table,acc_table,prop_table

	def test_multiple_top_k(self,dep_dir_path,ths_to_test) :
		seuil_table=[]
		acc_table=[]
		prop_table=[]
		k=0
		accuracy=0
		prop_classe=0.5
		while(accuracy < 1 and prop_classe < 1 and k < len(self.reseau.binarizer.classes_)) :
		    (accuracy,prop_classe,precision) = self.test_pred_top_k(dep_dir_path,ths_to_test,k)
		    seuil_table.append(k)
		    acc_table.append(accuracy)
		    prop_table.append(prop_classe)
		    print(k,accuracy,prop_classe)
		    k=k+k//10+1
		return seuil_table,acc_table,prop_table
		
	def th_name_pred_to_zf_file(self,theorem,pred,zf_file) :
		"""
		Prend le nom du theoreme et sa prediction
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file 
		"""
		all_th = self.dataManager.get_all_th()
		deps = self.reseau.binarizer.inverse_transform(np.array([pred]))[0]
		ensure_dir(zf_file)
		f=open(zf_file,"w+")
		f.write("include \"../"+self.dataManager.rew_type_file+"\".\n")
		for dep in deps :
		    if dep in all_th :
		        if dep==theorem :
		            f.write("#include itself\n")
		        else :
		            f.write("#"+dep+"\n")
		            f.write(self.dataManager.ax_th_declaration[dep])
		    if dep in self.dataManager.types :
		        f.write(self.dataManager.rewrite_declaration[dep])
		        
		f.write("goal "+th_declaration_to_text(self.dataManager.ax_th_declaration[theorem]))
		f.close()
		
	def th_string_pred_to_zf_file(self,th_string,pred,zf_file) :
		"""
		Prend l'enoncee du theoreme et sa prediction
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file 
		"""
		all_th = self.dataManager.get_all_th()
		deps = self.reseau.binarizer.inverse_transform(np.array([pred]))[0]
		ensure_dir(zf_file)
		f=open(zf_file,"w+")
		f.write("include \"../"+self.dataManager.rew_type_file+"\".\n")
		for dep in deps :
			if dep in all_th :
			    f.write("#"+dep+"\n")
			    f.write(self.dataManager.ax_th_declaration[dep])
			if dep in self.dataManager.types :
			    f.write(self.dataManager.rewrite_declaration[dep])
		        
		f.write("goal "+th_declaration_to_text(th_string))
		f.close()
		
	def th_name_pred_seuil_to_zf_file(self,theorem,zf_file,seuil=0.05):
		"""
		A partir du nom du theorem, predit les premisses necessaires (methode seuil)
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file
		"""
		pred = self.predict_seuil_th(theorem,seuil)
		
		self.th_name_pred_to_zf_file(theorem,pred,zf_file)
		
		
	def th_name_pred_top_k_to_zf_file(self,theorem,zf_file,k=5):
		"""
		A partir du nom du theoreme, predit les premisses necessaires (methode top k)
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file
		"""
		pred = self.predict_top_k_th(theorem,k)
		
		self.th_name_pred_to_zf_file(theorem,pred,zf_file)
		
	def th_string_pred_seuil_to_zf_file(self,th_string,zf_file,seuil=0.05):
		"""
		A partir de l'enonce d'un theorem, predit les premisses necessaires (methode seuil)
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file
		"""
		pred = self.reseau.predict_seuil(th_string,seuil)
		
		self.th_string_pred_to_zf_file(th_string,pred,zf_file)
		
		
	def th_string_pred_top_k_to_zf_file(self,th_string,zf_file,k=5):
		"""
		A partir de l'enonce d'un theoreme, predit les premisses necessaires (methode top k)
		Ecrit les enonces des premisses predites, ainsi que l'enonce du theoreme a prouver dans le fichiers zf_file
		"""
		pred = self.reseau.predict_top_k(th_string,k)
		
		self.th_string_pred_to_zf_file(th_string,pred,zf_file,rew_type_file)
	
	

