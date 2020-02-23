# Automating Tarski's Geometry Using Deduction Modulo Theory and Deep Learning Based Premise Selection

## Goal of the Experiment

This experiment relies on the use of Zipperposition, a superposition-based tool, which has been extended to deduction modulo theory. Deduction modulo theory proposes to replace axioms with rewrite rules and provides a framework combining first-order proof systems with a congruence generated by rewrite rules on terms and propositions. [A first experiment](https://github.com/delahayd/tarski) consisted in applying Zipperposition to Tarski's geometry. As a benchmark, we used GeoCoq, a formalization of foundations of geometry in Coq, which uses the formalization based on Tarski’s axioms of the “Metamathematische Methoden in der Geometrie” by Schwabhäuser, Szmielew, and Tarski.

To improve the results obtained by Zipperposition on this benchmark, we propose a second experiment, whose goal is to exploit the knowledge that is brought by the manual proofs done in Coq, and perform premise selection by providing Zipperposition with all the material necessary
to find the proof. To do so, we build a deep neural network, which is trained using a set
of problems validated by Zipperposition, and which tries to predict the axioms and lemmas
necessary for Zipperposition to find the proof of a given problem.

## The Benchmark

We rely on [GeoCoq](https://geocoq.github.io/GeoCoq/), which is a formalization of foundations of geometry in Coq. In particular, we use the formalization based on Tarski’s axioms of the “[Metamathematische Methoden in der Geometrie](https://www.amazon.fr/Metamathematische-Methoden-Geometrie-Metamathematical-university/dp/4871877078)”, which consists of the development of the first part of the book (16 chapters). That is a total of 1,237 problems.

## The Automated Deduction Tool

Before running the experiment, you must have [Zipperposition](https://github.com/sneeuwballen/zipperposition/) pre-installed on your computer. This experiment was successfully run using Zipperposition version 1.5.

## Contents of the Archive

### The “datas” folder contains all the data necessary for the scripts to work properly:

  * File “ax_th_def.zf”: Definitions of theorems and axioms.
  * File “rew_def.zf”: Definitions of rewrite rules.
  * File “rew_type.zf”: Typing of rewrite rules.
  * File “rew_type.json”: Typing of the rewrite rules that are useful for the proof (it does not contain the primitive structures as points in particular) in JSON format.
  * File “config_struct.json”: Provides the structure of the folders that contain the dependency (“.dep”) and problem (“.zf”) files. Requires *exactly* one depth level. For example, if we have the structure {"Ch02_cong": ["cong_reflexivity"], "Ch03_bet": ["bet_col"]}, this means that the “cong_reflexivity” files are in the “Ch02_cong” folder.

### The “source” folder contains the following code:

  * Classes:
    * “dataManager” deals with data:
        * Gets the data (from the “datas” folder).
        * Processing of the data (from raw data to a set of couples data => labels).
    * “reseau” deals with the neural network from the data sent by the “dataManager”:
        * Pre-processing of the data.
        * Creation and training of the neural network.
        * Primitive prediction management.
        * Has options to save and load the involved structures (tokenizer, multi_label_binarizer, architecture and weight of the network).
    * “predictionManager” is the link between the “dataManager” and the network (“reseau”):
        * Finer processing of network predictions (selection of the k highest values of the prediction, i.e. top_k, or values above a given threshold, i.e. threshold).
        * Provides statistics on prediction performance.
        * Produces problem files from the predictions.
    * “zipper_utils” allows us to parallelize the calls to Zipperposition and return statistics on the obtained results.
    * “utils” contains a set of functions that do not require a particular environment.

  * Scripts (executables); for more information on their parameters, use the “-h” flag:
    * “zipper_exec.py”: calls Zipperposition on the set of problems (or a subset specified in the “th_to_prove_file” file) in the “zf_dir” folder (structured as specified in the “config_struct” file), and stores the list of proved problems in the “th_valid_file” file.
    * “train.py”: creates and trains a network on the set of problems specified by the “th_valid_file” file, whose premises are given in the “dep_dir” folder. This network is then saved in the “save_network_dir” folder.
    * “tactic_top_k.py”:
        * Technique of the k highest values: Uses the network saved in the “network_save” folder to predict the premises of the set of problems from the “ax_th_def.zf” file. Generates, at each iteration, from the predicted premises and a given k, zf files, stored in the “zf_dir” folder. Zipperposition is called over all the generated zf files. The next iteration only applies to the problems not proved by the previous iterations.
        * k ranges from 0 to the number of premises known by the network. At each iteration, k is increased by the result of the Euclidean division of k by 10 to which 1 is added.
    * “tactic_seuil.py”:
        * Threshold technique: Uses the network saved in the “network_save” folder to predict the premises of the set of problems from the “ax_th_def.zf” file. Generates, at each iteration, from the predicted premises and a given threshold, zf files, stored in the “zf_dir” folder. Zipperposition is called over all the generated zf files. The next iteration only applies to the problems not proved by the previous iterations.
        * The threshold ranges from 0.9 to 1e-7 and is divided by 1.2 at each iteration.
    * “tactic_data_to_th_proved_file.py”: Converts a data file (created by one of the tactic scripts) into a file containing the list of the names of the problems proved by this tactic.
    * “zf_dir_to_dep_dir.py”: Converts a folder containing zf files into a folder containing the corresponding files of dependencies, the latter containing all the names of the lemmas, axioms and rewrite rules appearing in the associated zf file.
    * “display_data.py”: Requests a data file (resulting from the application of a tactic) and the list of problems used in the training of the network. Displays a graph corresponding to the evolution of the proved theorems according to the tactic parameter (top_k or threshold). Gives the proportion of proved theorems among those used during the training and the proportion of proved theorems among the others (completely unknown premises).

## Classical Use

Go to the “source” folder and type:

1. ```python zipper_exec.py "../resultat/geocoq_extract/zf/" "../resultat/geocoq_extract/th_proved.json" "../datas/config_struct.json"```

1. ```python train.py "../resultat/geocoq_extract/th_proved.json" "../resultat/geocoq_extract/dependencies/" "../resultat/network/geocoq_extract_network/"```

1. ```python tactic_seuil.py "../resultat/network/geocoq_extract_network/" "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil2/tactic_datas.pickle" -si 0.05 -sm 0.02```

1. ```python tactic_top_k.py "../resultat/network/geocoq_extract_network/" "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil2/tactic_datas.pickle" -ki 2 -km 30```

1. ```python tactic_data_to_th_proved_file.py "../resultat/tactic_seuil/tactic_seuil_datas.pickle" "../resultat/tactic_seuil/th_proved.json"```

1. ```python zf_dir_to_dep_dir.py "../resultat/tactic_seuil/zf/" "../resultat/tactic_seuil/dependencies/"```

1. ```python display_data.py "../resultat/tactic_seuil/tactic_seuil_datas.pickle" "../resultat/geocoq_extract/th_proved.json"```

## Contacts

If you have any questions, comments or suggestions, please contact:

* David Delahaye (LIRMM, Université de Montpellier, CNRS, Montpellier, France), [David.Delahaye@lirmm.fr](mailto:David.Delahaye@lirmm.fr)
* Baptiste Lemoine (LIRMM, Université de Montpellier, CNRS, Montpellier, France), [Baptiste.Lemoine@lirmm.fr](mailto:Baptiste.Lemoine@lirmm.fr)