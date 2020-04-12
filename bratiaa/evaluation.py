"""
Functions for computing the difference between two sets of annotations.
"""
from collections import namedtuple, Counter
import sys

import bratsubset.annotation as bs

Annotation = namedtuple('Annotation', ['type', 'id','label', 'offsets'])

AttAnnotation = namedtuple('AttAnnotation', ['type', 'id', 'target', 'value'])

FinalAnnotation = namedtuple('Annotation', ['type','label', 'attribute'])

def exact_match_instance_evaluation(ann_path_1, ann_path_2, tokens=None):
    exp = set(_read_textbound_annotations(ann_path_1))
    pred = set(_read_textbound_annotations(ann_path_2))
    tp = exp.intersection(pred)
    return tp, exp, pred


def _read_textbound_annotations(ann_path):
    with bs.Annotations(ann_path.as_posix(), read_only=True) as annotations:
        text_ann = Annotation
        att_ann = AttAnnotation
        for annotation in annotations.get_textbounds():
            yield Annotation('T', annotation.type, tuple(annotation.spans))
            

def exact_match_instance_polarity_evaluation(ann_path_1, ann_path_2, tokens=None):
    exp = list(_read_attributebound_annotations(ann_path_1))
    exp_set = set(exp)
#     print("List = ", exp)
#     print("Set = ", exp_set)
#     print("------")
    pred = list(_read_attributebound_annotations(ann_path_2))
    pred_set = set(pred)
#     print("List = ", pred)
#     print("Set = ", pred_set)
    tp = exp_set.intersection(pred_set)
#     print("Tp = ",tp)
    
#     print("*****************************************")
#     return (),(),()    
    return tp, exp_set, pred_set


def _read_attributebound_annotations(ann_path):
    with bs.Annotations(ann_path.as_posix(), read_only=True) as annotations:
        polarity_ann = AttAnnotation
        aspect_ann = Annotation
        final_ann = FinalAnnotation
        aspect_list = []
        polarity_list = []
        for annotation in annotations.get_textbounds():
            aspect_ann=Annotation('T', annotation.id, annotation.type, tuple(annotation.spans))
            if aspect_ann.label in ['GENERAL', 'PROFANITY', 'VIOLENCE', 'FEEDBACK']:
                aspect_list.append(aspect_ann)

        for annotation in annotations.get_attributes():
            att_ann=AttAnnotation('A', annotation.id, annotation.target, annotation.value)
            if att_ann.value in ['0', '1']:
                polarity_list.append(att_ann)
          
        for each_aspect in aspect_list:
            for each_polarity in polarity_list:
                if each_aspect.id == each_polarity.target:
                    final_ann = FinalAnnotation('T', each_aspect.label, each_polarity.value)
                    yield final_ann
                    


def exact_match_token_evaluation(ann_path_1, ann_path_2, tokens=None):
    """
    Annotations are split into token-sized bits before evaluation.

    Sub-token annotations are expanded to full tokens. Long annotations will influence the results more than short
    annotations. Boundary errors for adjacent annotations with the same label are ignored!
    """
    exp_list = list(_read_token_annotations(ann_path_1, tokens))
#     print(exp_list)
#     print("**********************************************************")
    pred_list = list(_read_token_annotations(ann_path_2, tokens))
#     print(pred_list)
#     print("**********************************************************")
    tp = counter2list(Counter(exp_list) & Counter(pred_list))
    return tp, exp_list, pred_list


def counter2list(c):
    for elem, cnt in c.items():
        for i in range(cnt):
            yield (elem)


def _read_token_annotations(ann_path, tokens):
    """
    Yields a new annotation for each token overlapping with an annotation. If annotations are overlapping each other,
    there will be multiple annotations for a single token.
    """
    for annotation in set(_read_textbound_annotations(ann_path)):
        for start, end in annotation.offsets:
            for ts, te in tokens.overlapping_tokens(start, end):
                yield Annotation(annotation.type, annotation.label, ((ts, te),))
