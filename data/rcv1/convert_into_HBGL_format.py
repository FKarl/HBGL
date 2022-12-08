import json

from sklearn.model_selection import train_test_split

"""
This script converts our NYT json file into the format of the HBGL framework.
"""

if __name__ == '__main__':
    # test data
    with open('test_data.json', 'r') as test_file:
        test_data = json.load(test_file)
    with open('rcv1_test_all.json', 'w') as out_file:
        for i in range(len(test_data)):
            line = json.dumps(
                {'token': test_data[i]['text'], 'label': test_data[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')

    # train data
    with open('train_data.json', 'r') as train_file:
        train_data = json.load(train_file)

    # split train data into train and val
    train, val = train_test_split(train_data, test_size=0.1, random_state=0)

    with open('rcv1_train_all.json', 'w') as out_file:
        for i in range(len(train)):
            line = json.dumps(
                {'token': train[i]['text'], 'label': train[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')

    # val data
    with open('rcv1_val_all.json', 'w') as out_file:
        for i in range(len(val)):
            line = json.dumps(
                {'token': val[i]['text'], 'label': val[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')
