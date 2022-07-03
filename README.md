# MUKALMA
## _A Knowledge-Powered Conversational Agent_

MUKALMA is a human-like chatbot which incorporates correct, relevant knowledge in its responses.

## How does it work?

- Takes key features from messages you send to it
- Uses those features to search Wikipedia for the most relevant articles
- Uses its Information Retrieval capabilities to identify sentence(s) that are most relevant to the conversation
- Incorporates knowledge from these sentences in human-like responses

<!--
## Tech: TODO
-->

## Installation

### Installing the required python packages
```sh
pip install virtualenv
cd src
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Downloading the submodels used by MUKALMA

MUKALMA has model size presets to achieve a tradeoff between model size and performance. It utilizes sub-models of different sizes to achieve this tradeoff. MUKALMA will automatically download any models that are missing from the ```models``` folder at the root of this repository.

The following table depicts the presets available for MUKALMA, and their accompanying model sizes. The presets can be customized in ```src/api/APIModel.py```.


| MUKALMA Preset | Model Size |
| ------ | ------ |
| small | 1.67 GB|
| medium | 3.40 GB |
| large | 5.47 GB |
| xlarge | 6.32 GB |

## Running MUKALMA

### Running the MUKALMA model

Note: Ensure you have selected your desired preset for MUKALMA's model size

```sh
cd src/api
set FLASK_APP=app.py
flask run
```

### Running the sample frontend

```sh
cd src/front_end
npm install
npm start
```

### Evaluating Output

To evaluate Mukalma's output , we have used a free tool named nlg-eval made available by Maluuba Inc. , an Artificial Intelligence Company that has been acquired by Microsoft. To acquire and setup nlg-eval , please use the following link : 
 
 https://github.com/Maluuba/nlg-eval
 

nlg-eval runs comparisons between actual and expected output of NLG on several unsupervised , automated metrics. The Gold standard we have used to compare our output to is the Wizards of Wikipedia Dialogue Dataset , which can be found at this link : 

https://drive.google.com/drive/folders/1yYCOeMwm-8d9Q6KlM3vTx3vzjCNTeAF7?usp=sharing

These are some of the metrics that nlg-eval produces results for : 

BLEU-1
METEOR
ROUGE-L
Skip Thoughts Cosine Similarity
Embedding Average Cosine Similarity
Vector Extrema Cosine Similarity
Greedy Matching Score


## License

GNU General Public License v3.0

## Contact us
- [Farjad Ilyas](mailto:ilyasfarjad@gmail.com?subject=[GitHub]%20Source%20Han%20Sans)
- [Nabeel Danish](mailto:nabeelben@gmail.com?subject=[GitHub]%20Source%20Han%20Sans)
- [Saad Saqlain](mailto:i180694@nu.edu.pk?subject=[GitHub]%20Source%20Han%20Sans)

