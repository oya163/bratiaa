# bratiaa

Inter-annotator agreement for [Brat](https://brat.nlplab.org/) annotation projects. For a quick overview of the output generated by `bratiaa`, have a look at the [example files](https://github.com/kldtz/bratiaa/tree/master/example-files). So far only text-bound annotations are supported, all other annotation types are ignored.

## Installation

Clone the repository. Install the package via pip.

```shell
git clone https://github.com/kldtz/bratiaa.git
pip install bratiaa
```

## Project Structure

By default `bratiaa` expects that each first-level subdirectory of the annotation project contains the files of one annotator. It will automatically determine the set of files annotated by each annotator (files with the same relative path starting from the different annotators' directories). Here is a simple example:

```shell
example-project/
├── annotation.conf
├── annotator-1
│   ├── doc-1.ann
│   ├── doc-1.txt
│   ├── doc-3.ann
│   ├── doc-3.txt
│   └── second
│       ├── doc-2.ann
│       └── doc-2.txt
└── annotator-2
    ├── doc-3.ann
    ├── doc-3.txt
    ├── doc-4.ann
    ├── doc-4.txt
    └── second
        ├── doc-2.ann
        └── doc-2.txt
```
In this example, we have two agreement documents: 'second/doc-2.txt' and 'doc-3.txt'. The other two documents are only annotated by a single annotator.

If you have a different project setup, you need to provide your own `input_generator` function, yielding document objects with paths to the plain text and all corresponding ANN files (cf. `bratiaa.agree.py`). 

## Usage

You can either use `bratiaa` as a Python library or as a command-line tool.


### Python Interface
```python
import bratiaa as biaa

project = '/path/to/brat/project'

# instance-level agreement
f1_agreement = biaa.compute_f1_agreement(project)

# print agreement report to stdout
biaa.iaa_report(f1_agreement)

# agreement per label
label_mean, label_sd = f1_agreement.mean_sd_per_label()

# agreement per document
doc_mean, doc_sd = f1_agreement.mean_sd_per_document() 

# total agreement
total_mean, total_sd = f1_agreement.mean_sd_total()
```

For the token-level evaluation, please use your own tokenization function. This function should yield (start, end) offset tuples for any given string like the example function below.

```python
import re
import bratiaa as biaa

def token_func(text):
    token = re.compile('\w+|[^\w\s]+')
    for match in re.finditer(token, text):
        yield match.start(), match.end()

# token-level agreement
f1_agreement = biaa.compute_f1_agreement('/path/to/brat/project' , token_func=token_func)
```

### CLI
Help message: `brat-iaa -h`

```shell
# instance-level agreement and heatmap
brat-iaa /path/to/brat/project --heatmap instance-heatmap.png > instance-agreement.md

# token-level agreement (not recommended)
brat-iaa /path/to/brat/project -t --heatmap token-heatmap.png > token-agreement.md
```

The token-based evaluation of the command-line interface uses the generic pattern `'\S+'` to identify tokens (splitting on whitespace) and hence is not recommended. Please use the Python interface with a language- and task-specific  tokenizer instead.

For the output formats generated by the above commands, have a look at the [example files](https://github.com/kldtz/bratiaa/tree/master/example-files).


## Agreement Measures

For each multiply annotated document, we compute the number of true positives (*TP*), false positives (*FP*) and false negatives (*FN*) for each 2-combination of annotators, where each annotator contributes one set of annotations, via basic (multi)set operations. These numbers can later be aggregated along two dimensions: *documents* and/or *labels*. Based on the aggregated numbers we compute `F1 = (2*TP) / (2*TP + FP + FN)` for each annotator pair. From these pair-wise F-scores, mean and standard deviation are reported (see <a href="#hripcsak-2005">Hripcsak & Rothschild, 2005</a>).


### Instance-Based Agreement

An annotation instance pertaining to a certain document consists of a label and one or more start-end offset tuples (multiple start-end tuples in the case of discontinuous annotations). Two instances are considered identical if label and offset tuples match. Identical instances from a single annotator (on the same document) are considered as accidental - only unqiue annotation instances are used for calculating agreement.

### Token-Based Agreement

Each annotation instance is split up into its overlapping tokens, e.g. if our tokenizer splits on whitespace, "\[<sub>ORG</sub> Human Rights Watch\]" and "\[<sub>ORG</sub> Human Rights Wat\]ch" both become "\[<sub>ORG</sub> Human\] \[<sub>ORG</sub> Rights\] \[<sub>ORG</sub> Watch\]". These split annotations are then treated as instances in the way described above with the only exception that we are dealing with **multisets** instead of sets, allowing for multiple token-based annotations with the same label and offsets in the case of overlapping annotations of the same type. For example, in "\[<sub>LOC</sub> University of \[<sub>LOC</sub> Jena\]\]" we have two overlapping location annotations resulting in four token-based annotations of which two are identical ("\[<sub>LOC</sub> Jena\]").

Be aware that "\[<sub>ORG</sub> Human\] \[<sub>ORG</sub> Rights Watch\]" and "\[<sub>ORG</sub> Human Rights\] \[<sub>ORG</sub> Watch\]" both become "\[<sub>ORG</sub> Human\] \[<sub>ORG</sub> Rights\] \[<sub>ORG</sub> Watch\]", that is, boundary errors between adjacent annotations of the same type are ignored!


## References

<a name="hripcsak-2005">Hripcsak, G., & Rothschild, A. S. (2005).</a> Agreement, the f-measure, and reliability in information retrieval. Journal of the American Medical Informatics Association, 12(3), 296-298.


## License

This software is provided under the [MIT-License](https://github.com/kldtz/bratiaa/blob/master/LICENSE). The code contains a modified subset of brat, which is available under the same permissive [license](https://github.com/kldtz/bratiaa/blob/master/bratsubset/BRAT_LICENSE.md).