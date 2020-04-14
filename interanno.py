'''
    To check inter-annotator agreement
    on token-level, polarity-level, relation-level
    
    How to run:
        # relation-level
        python interanno.py relation
        
        # polarity-level
        python interanno.py polarity
        
        # instance-level (exact matching)
        python interanno.py instance
        
        # instance-level (subword matching)
        python interanno.py        
'''

import sys
import re

# sys.path.insert(1, '../thirdparty/bratiaa/')
from bratiaa import agree as biaa
from bratiaa.evaluation import *

project = '../../agreement_version/agreement/brat_annotator/'

agreement_type = sys.argv[1] if len(sys.argv) > 1 else None

def token_func(text):
    # word level
#     token = re.compile("\S+")
    # character level
    token = re.compile('\w+|[^\w\s]+')
    for match in re.finditer(token, text):
        yield match.start(), match.end()

if agreement_type == 'polarity':
    f1_agreement = biaa.compute_f1_agreement(project, eval_func=exact_match_instance_polarity_evaluation)
elif agreement_type == 'relation':
    f1_agreement = biaa.compute_f1_agreement(project, eval_func=exact_match_instance_relation_evaluation)     
elif agreement_type == 'instance':
    f1_agreement = biaa.compute_f1_agreement(project) 
else:    
    f1_agreement = biaa.compute_f1_agreement(project, token_func=token_func)    

# print agreement report to stdout
biaa.iaa_report(f1_agreement)

# agreement per label
label_mean, label_sd = f1_agreement.mean_sd_per_label()

# agreement per document
doc_mean, doc_sd = f1_agreement.mean_sd_per_document() 

# total agreement
total_mean, total_sd = f1_agreement.mean_sd_total()
print("Total mean =", total_mean)
#print("Kappa =", f1_agreement.compute_kappa_score())

print("************************************************************")




# token-level agreement
#f1_agreement = biaa.compute_f1_agreement(project, token_func=token_func)

#biaa.iaa_report(f1_agreement)

# agreement per label
#label_mean, label_sd = f1_agreement.mean_sd_per_label()

# agreement per document
#doc_mean, doc_sd = f1_agreement.mean_sd_per_document() 

# total agreement
#total_mean, total_sd = f1_agreement.mean_sd_total()
#print(f1_agreement.compute_kappa_score())
