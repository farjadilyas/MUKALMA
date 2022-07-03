import json
import requests
  

# Opening JSON file
f = open('test_topic_split.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)

fr = open("wizard_statements.txt", "w")

# Wizard statements

for i in range(len(data)):
    
    for j in range(len(data[i]['dialog'])):
        if(j != 0 and ("Wizard" in data[i]['dialog'][j]['speaker'])):
            Unencoded = str(data[i]['dialog'][j]['text'].encode('utf-8'))
            Unencoded = Unencoded[2:-1]
            fr.write(Unencoded)
            fr.write('\n')

fr.close()

fr2 = open("apprentice_statements.txt", "w")

# Apprentice statements

#for i in range(len(data)):
    #for j in range(len(data[i]['dialog'])):
        #if(j%2 == 1):
            #print(data[i]['dialog'][j]['text'])  
            #fr2.write(data[i]['dialog'][j]['text'])
            #fr2.write('\n')
    #print('\n')

for i in range(len(data)):
    
    for j in range(len(data[i]['dialog'])):
        if(("Apprentice" in data[i]['dialog'][j]['speaker'])):
            Unencoded = str(data[i]['dialog'][j]['text'].encode('utf-8'))
            Unencoded = Unencoded[2:-1]
            fr2.write(Unencoded)
            fr2.write('\n')

fr2.close()

f.close()

# Reset the mukalma_output file for this test run
with open('mukalma_output.txt', 'w'):
    pass

# Taking each line of the Apprentice as input , sending to Mukalma and recording the response

url = input("Enter the endpoint url of the model being evaluated (Enter for default): ")
if not url:
    url = 'http://2b54-206-84-141-137.ngrok.io/reply'

input = open('apprentice_statements.txt' , 'r')
for x in input:
    line = x

    #Sending Apprentice Statement to Mukalmaa
    #Remember : Link can change , but add /reply to the end
    data = { "message" : line,
  "async": False,
  "m_id":0}

    res = requests.post(url, json=data)
    print(res.text)

    #Store the response from Mukalma as the Output
    output = open('mukalma_output.txt','a')
    output.write(json.loads(res.text)["response"].strip())
    output.write('\n')
    output.close()