# Evaluating Output

To evaluate Mukalma's output, we have used a free tool named nlg-eval made available by Maluuba Inc., an Artificial Intelligence Company that has been acquired by Microsoft. To acquire and setup nlg-eval, please follow the guide on its [repository](https://github.com/Maluuba/nlg-eval)
 

Nlg-eval runs comparisons between actual and expected output of NLG on several unsupervised, automated metrics. The Gold standard we have used to compare our output to is the Wizards of Wikipedia Dialogue Dataset, which can be found [here](https://drive.google.com/drive/folders/1yYCOeMwm-8d9Q6KlM3vTx3vzjCNTeAF7?usp=sharing)

These are some of the metrics that nlg-eval produces results for : 

- BLEU-1
- METEOR
- ROUGE-L
- Skip Thoughts Cosine Similarity
- Embedding Average Cosine Similarity
- Vector Extrema Cosine Similarity
- Greedy Matching Score

# Steps to reproduce our results  

- Using mukalma_out.txt and wizards_out.txt , run nlg-eval to produce the metrics for Mukalma
- Using dialo_out.txt and wizards_out.txt , run nlg-eval to produce the metrics for DialoGPT

# Steps to evaluate Mukalma using a larger amount of Data

The following instructions are to evaluate MUKALMA on the data given in the 'test_topic_split.json' file. To evaluate MUKALMA on a different data file from the Wizards dataset , paste the chosen file in the 'eval' directory and change the filename from 'test_topic_split.json' to the chosen file on line 6 of the file 'DataGeneration.py'

## Running the Evaluation

- Setup and Run MUKALMA. 
- Run the 'data-generation.py' file
- Upon execution , provide the endpoint url of the model that is running
- Once executed , the following files will be generated : 
    - wizard_statements.txt
    - apprentice_statements.txt
    - mukalma_output.txt
- Use the mukalma_output.txt and wizard_statements.txt files with nlg-eval to produce the required metrics 
