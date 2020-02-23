import tensorflow as tf
import numpy as np
import re
import pickle
from utils import *
from sklearn.preprocessing import MultiLabelBinarizer
import keras.preprocessing as prepro
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

from keras.models import Model
from keras.layers import Input, Dense, Dropout, concatenate, Conv1D, Embedding
from keras.layers.core import Reshape, Flatten
from keras import regularizers
from keras.optimizers import Adam
from keras.metrics import top_k_categorical_accuracy

from keras.models import load_model
from keras import backend as K
config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)
K.set_session(sess)


class Reseau:
	tokenizer=None
	binarizer=None

	embedding_dim=50
	filter_sizes=[3,4,5]
	num_filters = 50
	drop = 0.2

	input_length=None
	output_length=None

	model=None

	def init_train(self,x,labeled_y):
		self.tokenizer=prepro.text.Tokenizer(filters='"#$%*+,./:;?@[\\]^{}\t\n',split=" ",char_level=False)
		text=parse_special_characters(x)
		self.tokenizer.fit_on_texts(text)
		encoded_docs = self.tokenizer.texts_to_sequences(text)
		self.input_length = len(max(encoded_docs,key=len))
		padded_docs = prepro.sequence.pad_sequences(encoded_docs, maxlen=self.input_length, padding='post')

		padded_docs=self.pretraitement(x)
		y=self.premisse_list_to_binary_label(labeled_y)
		self.x_train, self.x_test, self.y_train, self.y_test = self.train_test_split_with_weight(padded_docs,y,weight=100000)
		self.set_input_length(self.x_train)
		self.set_output_length(self.y_train)
		self.model = self.create_model()
		return self.train_model(self.x_train,self.x_test,self.y_train,self.y_test)
		
	
	def pretraitement(self,x,max_length=None) :
		"""
		Prend l'ensemble des énoncés des théorèmes servant de données d'entrainement et de test.

		Sépare les charactères/ensembles de charactères importants (ex : <=>).
		Créé un dictionnaire à partir des mots apparaisant dans ces énoncés.
		Remplace les mots par l'index dans ce dictionnaire.
		Uniformise la taille des énoncés avec du padding.

		Renvoie l'ensemble des énoncés ainsi convertis en liste d'entiers
		"""

		text=parse_special_characters(x)

		encoded_docs = self.tokenizer.texts_to_sequences(text)

		if max_length is None :
			max_length = len(max(encoded_docs,key=len))

		padded_docs = prepro.sequence.pad_sequences(encoded_docs, maxlen=max_length, padding='post')
		return padded_docs


	def premisse_list_to_binary_label(self,labeled_y):
		"""
		Prend un ensemble de listes de premisses (listes "labeled_y" de DataManager.create_data principalement)

		Créé un dictonnaire contenant l'ensemble des prémisses présentes
		Remplace chaque liste de premisses par une liste de 0 et 1
		La valeur 1 à l'indice i indique la présence, dans la liste initiale, du prémisse i
		(pour i indice dans la liste des classes du MultiLabelBinarizer)

		Renvoie l'ensemble des listes ainsi traitées
		"""
		self.binarizer = MultiLabelBinarizer()
		self.binarizer.fit(labeled_y)
		index=self.binarizer.classes_
		y = self.binarizer.transform(labeled_y)
		return y

	def train_test_split_with_weight(self,padded_docs,y,weight=1,test_size=0.2):
		"""
		Multiplie les valeurs de y par weight.
		Sépare les données en un ensemble d'entrainement et un ensemble de test.
		Prend :
			padded_docs : La liste des énoncés des théorèmes traité sous forme de liste d'entiers.
			y : La liste des prémisses nécessaires pour un théorèmes sous forme de liste binaire.
			ATTENTION : la valeur d'indice i dans padded_docs doit correspondre au même théorème que celui de la valeur i dans y
			weight : Le poid par lequel on multiplie les valeurs de y
			test_size : proportion des données utilisés pour tester les résultats du réseau 
		Renvoie x_train, x_test, y_train, y_test (x pour les énoncés des théorèmes, y pour les listes de prémisses)
		"""
		return train_test_split(np.array(padded_docs), np.array(y)*weight, test_size=0.20, random_state=10)

	def set_input_length(self,x_train) :
		self.input_length=x_train.shape[1]

	def set_output_length(self,y_train) :
		self.output_length=y_train.shape[1]


	def create_model(self):
		"""
		Créé le modele/architecture du réseau
		Necessite que input_length, output_length et tokenizer soient définis
		"""

		inputs = Input(shape=(self.input_length,))

		vocabulary_size=len(self.tokenizer.word_index)+1
	
		embedding = Embedding(vocabulary_size, self.embedding_dim)(inputs)

		conv_0 = Conv1D(self.num_filters, (self.filter_sizes[0]),activation='relu',kernel_regularizer=regularizers.l2(0.01))(embedding)
		conv_1 = Conv1D(self.num_filters, (self.filter_sizes[1]),activation='relu',kernel_regularizer=regularizers.l2(0.01))(embedding)
		conv_2 = Conv1D(self.num_filters, (self.filter_sizes[2]),activation='relu',kernel_regularizer=regularizers.l2(0.01))(embedding)

		merged_tensor = concatenate([conv_0, conv_1, conv_2], axis=1)

		flatten = Flatten()(merged_tensor)
		dropout = Dropout(self.drop)(flatten)


		output = Dense(units=self.output_length, activation='softmax',kernel_regularizer=regularizers.l2(0.01))(dropout)

		model = Model(inputs, output)

		adam = Adam(lr=1e-3)

		#top_k_categorical_accuracy verifie si 5 labels avec les valeurs de prédiction les plus eleves font bien partie des labels à prédire
		model.compile(loss='binary_crossentropy',optimizer=adam,metrics=['top_k_categorical_accuracy'])

		return model

	def train_model(self,x_train,x_test,y_train,y_test,nb_epochs=10,batch_size=32,verbose=1,shuffle=False):
		"""
		Entraine le model a partir des données passées en entré
		Retourne l'historique de l'apprentissage
		"""
		history=self.model.fit(x_train, y_train, batch_size=batch_size, epochs=nb_epochs, verbose=verbose, validation_data=(x_test, y_test),shuffle=shuffle)
		return history

	def predict(self,th_string) :
		x = th_declaration_to_text(th_string)
		padded_docs = self.pretraitement(np.array([x]),self.input_length)

		return self.model.predict(padded_docs)[0]

	def predict_seuil(self,th_string,seuil=0.05) :
		y_pred = self.predict(th_string)

		max_pred_value = np.max(y_pred)
		y_pred = np.array([0 if val < max_pred_value*seuil else 1 for val in y_pred])

		return y_pred

	


	def predict_top_k(self,th_string,k=5) :
		y_pred = self.predict(th_string)

		pred_sort = sorted(y_pred)[::-1]
		index_top_k=[list(y_pred).index(pred_sort[i]) for i in range(k)]
		new_y_pred = np.zeros(len(y_pred))
		for i in range(k) :
			new_y_pred[index_top_k[i]]=1

		return new_y_pred

	


	def save_model(self,file) :
		"""
		Enregistre le modele (structure et poids) dans le fichier file (format .h5 recommandé)
		"""
		self.model.save(file)


	def load_model(self,file) :
		"""
		Charge le modele (structure et poids) depuis le fichier file (format .h5 recommandé)
		"""
		self.model=load_model(file)

	def save_tokenizer(self,file) :
		with open(file, 'wb') as handle:
			pickle.dump(self.tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def load_tokenizer(self,file) :
		with open(file, 'rb') as handle:
			self.tokenizer = pickle.load(handle)

	def save_binarizer(self,file) :
		with open(file, 'wb') as handle:
			pickle.dump(self.binarizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def load_binarizer(self,file) :
		with open(file, 'rb') as handle:
			self.binarizer = pickle.load(handle)

	def save(self,dir) :
		"""
		Sauvegarde le modele, tokenizer et multiLabelBinarizer
		"""
		self.save_model(dir+"model.h5")
		self.save_tokenizer(dir+"tokenizer.pickle")
		self.save_binarizer(dir+"binarizer.pickle")

	def load(self,dir) :
		"""
		Sauvegarde le modele, tokenizer et multiLabelBinarizer
		"""
		self.load_model(dir+"model.h5")
		self.load_tokenizer(dir+"tokenizer.pickle")
		self.load_binarizer(dir+"binarizer.pickle")
		self.input_length=self.model.input_shape[1]
		self.output_length=self.model.output_shape[1]

