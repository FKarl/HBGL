#!/usr/bin/env python
# coding:utf-8

import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer


def _precision_recall_f1(right, predict, total):
    """
    :param right: int, the count of right prediction
    :param predict: int, the count of prediction
    :param total: int, the count of labels
    :return: p(precision, Float), r(recall, Float), f(f1_score, Float)
    """
    p, r, f = 0.0, 0.0, 0.0
    if predict > 0:
        p = float(right) / predict
    if total > 0:
        r = float(right) / total
    if p + r > 0:
        f = p * r * 2 / (p + r)
    return p, r, f


def evaluate(epoch_predicts, epoch_labels, id2label, threshold=0.5, top_k=None, as_sample=False):
    """
    :param epoch_labels: List[List[int]], ground truth, label id
    :param epoch_predicts: List[List[Float]], predicted probability list
    :param vocab: data_modules.Vocab object
    :param threshold: Float, filter probability for tagging
    :param top_k: int, truncate the prediction
    :return:  confusion_matrix -> List[List[int]],
    Dict{'precision' -> Float, 'recall' -> Float, 'micro_f1' -> Float, 'macro_f1' -> Float}
    """
    assert len(epoch_predicts) == len(epoch_labels), 'mismatch between prediction and ground truth for evaluation'
    # label2id = vocab.v2i['label']
    # id2label = vocab.i2v['label']
    # epoch_gold_label = list()
    # # get id label name of ground truth
    # for sample_labels in epoch_labels:
    #     sample_gold = []
    #     for label in sample_labels:
    #         assert label in id2label.keys(), print(label)
    #         sample_gold.append(id2label[label])
    #     epoch_gold_label.append(sample_gold)

    epoch_gold = epoch_labels

    # initialize confusion matrix
    confusion_count_list = [[0 for _ in range(len(id2label))] for _ in range(len(id2label))]
    right_count_list = [0 for _ in range(len(id2label))]
    gold_count_list = [0 for _ in range(len(id2label))]
    predicted_count_list = [0 for _ in range(len(id2label))]
    # TODO added
    total_predict_label_list = []

    for sample_predict, sample_gold in zip(epoch_predicts, epoch_gold):
        # region TODO added
        np_sample_predict = np.array(sample_predict, dtype=np.float32)
        sample_predict_descent_idx = np.argsort(-np_sample_predict)
        sample_predict_id_list = []
        if top_k is None:
            top_k = len(sample_predict)
        for j in range(top_k):
            if np_sample_predict[sample_predict_descent_idx[j]] > threshold:
                sample_predict_id_list.append(sample_predict_descent_idx[j])

        sample_predict_label_list = [id2label[i] for i in sample_predict_id_list]

        total_predict_label_list.append(sample_predict_label_list)
        # endregion

        if as_sample:
            sample_predict_id_list = sample_predict
        else:
            np_sample_predict = np.array(sample_predict, dtype=np.float32)
            sample_predict_descent_idx = np.argsort(-np_sample_predict)
            sample_predict_id_list = []
            if top_k is None:
                top_k = len(sample_predict)
            for j in range(top_k):
                if np_sample_predict[sample_predict_descent_idx[j]] > threshold:
                    sample_predict_id_list.append(sample_predict_descent_idx[j])

        for i in range(len(confusion_count_list)):
            for predict_id in sample_predict_id_list:
                confusion_count_list[i][predict_id] += 1

        # count for the gold and right items
        for gold in sample_gold:
            gold_count_list[gold] += 1
            for label in sample_predict_id_list:
                if gold == label:
                    right_count_list[gold] += 1

        # count for the predicted items
        for label in sample_predict_id_list:
            predicted_count_list[label] += 1

    precision_dict = dict()
    recall_dict = dict()
    fscore_dict = dict()
    right_total, predict_total, gold_total = 0, 0, 0

    for i, label in id2label.items():
        label = label + '_' + str(i)
        precision_dict[label], recall_dict[label], fscore_dict[label] = _precision_recall_f1(right_count_list[i],
                                                                                             predicted_count_list[i],
                                                                                             gold_count_list[i])
        right_total += right_count_list[i]
        gold_total += gold_count_list[i]
        predict_total += predicted_count_list[i]

    # Macro-F1
    precision_macro = sum([v for _, v in precision_dict.items()]) / len(list(precision_dict.keys()))
    recall_macro = sum([v for _, v in recall_dict.items()]) / len(list(precision_dict.keys()))
    macro_f1 = sum([v for _, v in fscore_dict.items()]) / len(list(fscore_dict.keys()))
    # Micro-F1
    precision_micro = float(right_total) / predict_total if predict_total > 0 else 0.0
    recall_micro = float(right_total) / gold_total
    micro_f1 = 2 * precision_micro * recall_micro / (precision_micro + recall_micro) if (
                                                                                                precision_micro + recall_micro) > 0 else 0.0

    # TODO region changed from original:
    # sklearn metrics
    # calc metrics with sklearn for multilabel classification

    epoch_gold_label = list()
    # get id label name of ground truth
    for sample_labels in epoch_labels:
        sample_gold = []
        for label in sample_labels:
            assert label in id2label.keys(), print(label)
            sample_gold.append(id2label[label])
        epoch_gold_label.append(sample_gold)

    print(epoch_labels)
    print(epoch_predicts)

    mlb = MultiLabelBinarizer()
    y_true = mlb.fit_transform(epoch_gold_label)
    y_pred = mlb.transform(total_predict_label_list)
    skl_micro_f1 = f1_score(y_true, y_pred, average='micro')
    skl_macro_f1 = f1_score(y_true, y_pred, average='macro')
    skl_samples_f1 = f1_score(y_true, y_pred, average='samples')
    skl_accuracy = accuracy_score(y_true, y_pred)

    print(
        f'skl_micro_f1: {skl_micro_f1}, skl_macro_f1: {skl_macro_f1}, skl_samples_f1: {skl_samples_f1}, skl_accuracy: {skl_accuracy}')
    print(f'f1_score (HBGL): micro: {micro_f1}, macro: {macro_f1}')

    # endregion

    return {'precision': precision_micro,
            'recall': recall_micro,
            'micro_f1': micro_f1,
            'macro_f1': macro_f1,
            'full': [precision_dict, recall_dict, fscore_dict, right_count_list, predicted_count_list, gold_count_list]}


def evaluate_seq2seq(batch_predicts, batch_labels, id2label):
    """_summary_

    Args:
        batch_predicts (_type_): one batch of predicted graph e.g [[0,0,1...],[0,1,...]],index is the corresponding label_id
        batch_labels (_type_): _description_ same as top,but the ground true label
        id2label (_type_): _description_

    Returns:
        _type_: _description_ return de micro,macro,precision and recall
    """
    assert len(batch_predicts) == len(batch_labels), 'mismatch between prediction and ground truth for evaluation'
    np_pred, np_labels = np.array(batch_predicts), np.array(batch_labels)
    np_right = np.bitwise_and(np_pred, np_labels)
    # [1]是True的索引,[0]是batch的索引，使用[1]就足够了
    pred_label_id = np.nonzero(np_pred)[1].tolist()
    labels_label_id = np.nonzero(np_labels)[1].tolist()
    right_label_id = np.nonzero(np_right)[1].tolist()

    # initialize confusion matrix
    confusion_count_list = [[0 for _ in range(len(id2label))] for _ in range(len(id2label))]
    right_count_list = [0 for _ in range(len(id2label))]
    gold_count_list = [0 for _ in range(len(id2label))]
    predicted_count_list = [0 for _ in range(len(id2label))]

    for x in pred_label_id: predicted_count_list[x] += 1
    for x in labels_label_id: gold_count_list[x] += 1
    for x in right_label_id: right_count_list[x] += 1

    precision_dict = dict()
    recall_dict = dict()
    fscore_dict = dict()
    right_total, predict_total, gold_total = 0, 0, 0

    for i, label in id2label.items():
        label = label + '_' + str(i)
        precision_dict[label], recall_dict[label], fscore_dict[label] = _precision_recall_f1(right_count_list[i],
                                                                                             predicted_count_list[i],
                                                                                             gold_count_list[i])
        right_total += right_count_list[i]
        gold_total += gold_count_list[i]
        predict_total += predicted_count_list[i]

    # Macro-F1
    precision_macro = sum([v for _, v in precision_dict.items()]) / len(list(precision_dict.keys()))
    recall_macro = sum([v for _, v in recall_dict.items()]) / len(list(precision_dict.keys()))
    macro_f1 = sum([v for _, v in fscore_dict.items()]) / len(list(fscore_dict.keys()))
    # Micro-F1
    precision_micro = float(right_total) / predict_total if predict_total > 0 else 0.0
    recall_micro = float(right_total) / gold_total
    micro_f1 = 2 * precision_micro * recall_micro / (precision_micro + recall_micro) if (
                                                                                                precision_micro + recall_micro) > 0 else 0.0

    return {'precision': precision_micro,
            'recall': recall_micro,
            'micro_f1': micro_f1,
            'macro_f1': macro_f1,
            }
