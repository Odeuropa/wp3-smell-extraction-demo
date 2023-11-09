import logging

import torch

logger = logging.getLogger(__name__)


class F1:
    def __init__(self, type_f1):
        self.tps = []
        self.fps = []
        self.fns = []
        self.type_f1 = type_f1
        self.str = 'f1_' + type_f1
        self.vocabulary = []
        self.vocabulary_dictionary = {}
        self.labels_mapping= {}
        self.metric_scores = {}

    def score(self, preds, golds, mask, vocabulary):
        # vocabulary = ['@@unkORpad@@', 'O', 'B-Time', 'I-Time','B-Quality','I-Quality']
        # self.vocabulary = ['@@unkORpad@@', 'O', 'B-Time', 'I-Time','B-Quality','I-Quality']
        # golds = torch.tensor([1,1,2,3,3,3,1,1,4,5,5]) 
        # preds = torch.tensor([1,1,1,2,3,3,1,1,1,4,5]) 

        self.vocabulary_dictionary = {k: v for v, k in enumerate(vocabulary)}
        
        
        for label in self.vocabulary_dictionary:
            if label.startswith("I-"):
                self.labels_mapping[self.vocabulary_dictionary[label]] = self.vocabulary_dictionary["B"+label[1:]]
            else:
                self.labels_mapping[self.vocabulary_dictionary[label]] = self.vocabulary_dictionary[label]
        
        # print(self.vocabulary)
        # print(self.vocabulary_dictionary)
        # print(self.labels_mapping)
        # print("----------")
        # print("----------")
        # print("----------")
        # print(golds)
        # print(preds)
        # print("----------")

        preds = preds.cpu()
        preds.apply_(lambda x: self.labels_mapping[x])
        preds = preds.cpu()

        golds = golds.cpu()
        golds.apply_(lambda x: self.labels_mapping[x])
        golds = golds.cpu()

        # print(golds)
        # print(preds)
        # print("++++++++++")
        # print("++++++++++")
        # vocabulary = ['@@unkORpad@@', 'O', 'B-Time','B-Quality']
        # self.vocabulary = ['@@unkORpad@@', 'O', 'B-Time','B-Quality']

        max_label = torch.max(torch.cat((preds, golds)))
        while len(self.tps) <= max_label:
            self.tps.append(0)
            self.fps.append(0)
            self.fns.append(0)

        self.vocabulary = vocabulary

        # Check whether to run the evaluation at the token- or sentence-level
        # TODO, it might be nicer to convert them to a similar shape?
        is_token_level = len(golds.shape) == 2

        for sent_idx in range(len(golds)):
            if is_token_level:
                for word_idx in range(len(golds[sent_idx])):
                    if mask[sent_idx][word_idx]:
                        gold = golds[sent_idx][word_idx]
                        pred = preds[sent_idx][word_idx]
                        if gold == pred:
                            self.tps[gold.item()] += 1
                        else:
                            self.fps[pred.item()] += 1
                            self.fns[gold.item()] += 1
            else:
                gold = golds[sent_idx]
                pred = preds[sent_idx]
                if gold == pred:
                    self.tps[gold.item()] += 1
                else:
                    self.fps[pred.item()] += 1
                    self.fns[gold.item()] += 1
        # print("tps",self.tps)
        # print("fps",self.fps)
        # print("fns",self.fns)

    def reset(self):
        self.tps = []
        self.fps = []
        self.fns = []
        self.total = 0

    def get_precision(self, tp, fp):
        return 0.0 if tp + fp == 0 else tp / (tp + fp)

    def get_recall(self, tp, fn):
        return 0.0 if tp + fn == 0 else tp / (tp + fn)

    def get_f1(self, precision, recall):
        return 0.0 if precision + recall == 0 else 2 * (precision * recall) / (precision + recall)

    def get_score(self):
        if self.type_f1 == 'micro':
            precision = self.get_precision(sum(self.tps), sum(self.fps))
            recall = self.get_recall(sum(self.tps), sum(self.fns))
            f1_score = self.get_f1(precision, recall)

            self.metric_scores["precision_" + self.type_f1] = precision
            self.metric_scores["recall_" + self.type_f1] = recall
            self.metric_scores[self.str] = f1_score
            self.metric_scores["sum"] = self.str


        elif self.type_f1 == 'macro':
            f1s = []
            precs = []
            recs = []

            for label_idx in range(1, len(self.tps)):
                label_name = self.vocabulary[label_idx]
                precision = self.get_precision(self.tps[label_idx], self.fps[label_idx])
                recall = self.get_recall(self.tps[label_idx], self.fns[label_idx])
                f1_score = self.get_f1(precision, recall)

                self.metric_scores["precision_" + label_name] = precision
                self.metric_scores["recall_" + label_name] = recall
                self.metric_scores["f1_" + label_name] = f1_score

                f1s.append(f1_score)
                precs.append(precision)
                recs.append(recall)

            self.metric_scores["precision_" + self.type_f1] = sum(precs) / len(precs)
            self.metric_scores["recall_" + self.type_f1] = sum(recs) / len(recs)
            self.metric_scores[self.str] = sum(f1s) / len(f1s)
            self.metric_scores["sum"] = self.str

        elif self.type_f1 == 'binary':
            if len(self.tps) > 3:
                logger.error('Choose F1 binary, but there are multiple classes, returning 0.0.')

                self.metric_scores["precision_" + self.type_f1] = 0.0
                self.metric_scores["recall_" + self.type_f1] = 0.0
                self.metric_scores[self.str] = 0.0
                self.metric_scores["sum"] = self.str

            else:    
                precision = self.get_precision(self.tps[1], self.fps[1])
                recall = self.get_recall(self.tps[1], self.fns[1])
                f1_score = self.get_f1(precision, recall)

                self.metric_scores["precision_" + self.type_f1] = precision
                self.metric_scores["recall_" + self.type_f1] = recall
                self.metric_scores[self.str] = f1_score
                self.metric_scores["sum"] = self.str

        else:
            logger.error('F1 type ' + self.type_f1 + ' not recognized, returning 0.0.')

            self.metric_scores["precision_" + self.type_f1] = 0.0
            self.metric_scores["recall_" + self.type_f1] = 0.0
            self.metric_scores[self.str] = 0.0
            self.metric_scores["sum"] = self.str
        # print(self.metric_scores)
        # print("xxxxxxxxxx")
        # print("xxxxxxxxxx")
        # print("xxxxxxxxxx")
        # exit()
        return self.metric_scores



# tensor([1, 1, 2, 3, 3, 3, 1, 1, 4, 5, 5])
# tensor([1, 1, 1, 2, 3, 3, 1, 1, 1, 4, 5])
# ----------
# tensor([1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4], device='cuda:0')
# tensor([1, 1, 1, 2, 2, 2, 1, 1, 1, 4, 4], device='cuda:0')
# ++++++++++
# ++++++++++
# tps [0, 4, 3, 0, 2]
# fps [0, 2, 0, 0, 0]
# fns [0, 0, 1, 0, 1]
# ['@@unkORpad@@', 'O', 'B-Time', 'I-Time', 'B-Quality', 'I-Quality']
# {'@@unkORpad@@': 0, 'O': 1, 'B-Time': 2, 'I-Time': 3, 'B-Quality': 4, 'I-Quality': 5}
# {0: 0, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4}
