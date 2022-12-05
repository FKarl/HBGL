import json

"""
This script converts our NYT json file into the format of the HBGL framework.
"""

if __name__ == '__main__':
    # test data
    with open('nyt_test_all.json', 'r') as test_file:
        test_data = json.load(test_file)
    with open('idnewnyt_test.json', 'w') as out_file:
        for i in range(len(test_data)):
            line = json.dumps(
                {'token': test_data[i]['text'], 'label': test_data[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')

    # train data
    with open('nyt_train_all.json', 'r') as train_file:
        train_data = json.load(train_file)
    with open('idnewnyt_train.json', 'w') as out_file:
        for i in range(len(train_data)):
            line = json.dumps(
                {'token': train_data[i]['text'], 'label': train_data[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')

    # val data
    with open('nyt_val_all.json', 'r') as val_file:
        val_data = json.load(val_file)
    with open('idnewnyt_val.json', 'w') as out_file:
        for i in range(len(val_data)):
            line = json.dumps(
                {'token': val_data[i]['text'], 'label': val_data[i]['labels'], 'doc_topic': [], 'doc_keyword': []})
            out_file.write(line + '\n')
