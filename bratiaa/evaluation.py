
"""
Functions for computing the difference between two sets of annotations.
"""
from collections import namedtuple, Counter
import sys

import bratsubset.annotation as bs

AspAnnotation = namedtuple('AspAnnotation', ['type','label', 'offsets'])

Annotation = namedtuple('Annotation', ['type', 'id','label', 'offsets'])

AttAnnotation = namedtuple('AttAnnotation', ['type', 'id', 'target', 'value'])

FinalAnnotation = namedtuple('Annotation', ['type','label', 'attribute'])

RelAnnotation = namedtuple('RelAnnotation', ['type', 'label', 'source_id', 'target_id'])

FinalRelAnnotation = namedtuple('FinalRelAnnotation', ['type', 'label', 'source', 'target'])

def exact_match_instance_evaluation(ann_path_1, ann_path_2, tokens=None):
    exp = list(_read_textbound_annotations(ann_path_1))
    exp_set = set(exp)
#     print("List = ", exp)
#     print("Set = ", exp_set)
#     print("------")
    pred = list(_read_textbound_annotations(ann_path_2))
    pred_set = set(pred)
#     print("List = ", pred)
#     print("Set = ", pred_set)
    tp = exp_set.intersection(pred_set)
#     print("Tp = ",tp)
#     print("*****************************************")
    return tp, exp, pred


def _read_textbound_annotations(ann_path):
    with bs.Annotations(ann_path.as_posix(), read_only=True) as annotations:
        for annotation in annotations.get_textbounds():
            # Annotation spans will make is unique even in a list
            aspect_ann=AspAnnotation('T', annotation.type, tuple(annotation.spans))
            # We don't want NUM to be calculated for now
            if aspect_ann.label not in ['NUM']:
                yield aspect_ann
            
'''
    Get polarity level tp
    Checks on (aspect category, polarity value)
'''
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
#     tp = exp_set.intersection(pred_set)
    tp = list((Counter(exp) & Counter(pred)).elements())    
#     print("Tp = ",tp)
#     print("*****************************************")
    return tp, exp, pred


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
                    

'''
    Get relation level tp
    Checks on (targeted/untargeted, aspect_category, target_entity)
'''                    
def exact_match_instance_relation_evaluation(ann_path_1, ann_path_2, tokens=None):
    exp_list = list(_read_relationbound_annotations(ann_path_1))
    exp_set = set(exp_list)
#     print("List = ", exp_list)
#     print("Set = ", exp_set)
#     print("------")
    pred_list = list(_read_relationbound_annotations(ann_path_2))
    pred_set = set(pred_list)
#     print("List = ", pred_list)
#     print("Set = ", pred_set)
#     tp = exp_set.intersection(pred_set)
    tp = list((Counter(exp_list) & Counter(pred_list)).elements())
#     print("Tp = ",tp)
#     print("*****************************************")
#     return (),(),()    
#     return tp, exp_set, pred_set
    # Using list instead of set because there might be
    # duplicate tagging in a same sentence
    # For example, there can be two GENERAL in same sentence
    return tp, exp_list, pred_list


def _read_relationbound_annotations(ann_path):
    with bs.Annotations(ann_path.as_posix(), read_only=True) as annotations:
        rel_ann = RelAnnotation
        aspect_ann = Annotation
        final_rel_ann = FinalRelAnnotation
        polarity_ann = AttAnnotation
        polarity_list = []        
        aspect_list = []
        relation_list = []
        
        for annotation in annotations.get_textbounds():
            aspect_ann=Annotation('T', annotation.id, annotation.type, tuple(annotation.spans))
            aspect_list.append(aspect_ann)
                
        # # Get untargeted aspect terms, with value 'YES'
        for annotation in annotations.get_attributes():
            att_ann=AttAnnotation('A', annotation.id, annotation.target, annotation.value)
            if att_ann.value in ['YES']:
                polarity_list.append(att_ann)
            
        for annotation in annotations.get_relations():
            rel_ann=RelAnnotation('R', annotation.type, annotation.arg1, annotation.arg2)
            relation_list.append(rel_ann)
        
        # Get targeted aspect terms
        for each_rel in relation_list:
            source_label = [x.label for x in aspect_list if x.id == each_rel.source_id]
            target_label = [x.label for x in aspect_list if x.id == each_rel.target_id]
            final_ann = FinalRelAnnotation('R', 'targeted', source_label[0], target_label[0])
            yield final_ann

        # Get untargeted aspect terms
        for each_att in polarity_list:
            source_label = [x.label for x in aspect_list if x.id == each_att.target]
            target_label = ['NULL']
            final_ann = FinalRelAnnotation('R', 'untargeted', source_label[0], target_label[0])
            yield final_ann            
                    
def exact_match_token_evaluation(ann_path_1, ann_path_2, tokens=None):
    """
    Annotations are split into token-sized bits before evaluation.
    Sub-token annotations are expanded to full tokens. Long annotations will influence the results more than short
    annotations. Boundary errors for adjacent annotations with the same label are ignored!
    """
    exp_list = list(_read_token_annotations(ann_path_1, tokens))
#     print("Exp = ", exp_list)
#     print("-----------")
    pred_list = list(_read_token_annotations(ann_path_2, tokens))
#     print("Pred = ", pred_list)
    tp = counter2list(Counter(exp_list) & Counter(pred_list))
#     print("Tp = ", list(tp))
#     print("**********************************************************")
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
                yield AspAnnotation(annotation.type, annotation.label, ((ts, te),))