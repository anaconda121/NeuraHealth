
## An Automated Electronic Health Records Scanning Pipeline to Detect Undiagnosed Cognitive Impairment with Deep Learning and Natural Language Processing

## Author
Tanish Tyagi

## Abstract
Because of the subtle onset with symptoms closely resembling that of normal aging, dementia related cognitive impairment is difficult to detect by health care professionals. With only one in four patients getting diagnosed, dementia’s underdiagnosis causes a significant public health concern, as millions are left behind without the necessary care and support for their chronic condition. Information relevant to dementia related cognitive impairment is often found in the electronic health records (EHR), but a manual review by physicians is time consuming and error-prone.

In my research, I developed natural language processing (NLP) models to create an automated EHR scanning pipeline that can detect patients with dementia related cognitive impairment. The deep learning model understands the linguistic context in the EHRs and outperforms current clinical methods to identify patients who had no earlier diagnosis, dementia-related diagnosis code, or dementia-related medications in their EHR. These cases would otherwise have gone undetected or been detected too late.

To make the EHR scanning pipeline accessible and affordable, I also developed a web application that can be used on mobile or desktop devices by primary care physicians for accurate and real-time detection.

With 55 million dementia patients worldwide and growing rapidly at the rate of one new case every 3 seconds, early intervention is the key to reducing financial burden and improving clinical outcomes. My research tackles this global public health challenge and provides mechanisms for early detection of dementia and its related diseases, including Alzheimer's, Parkinson’s, Lewy Body and others.

## Navigating the Codebase
1. ```Models/``` - Houses all the code for the Machine Learning (```TFIDF/```) and Deep Learning (```Bert/```) models 
2. ```Preprocessing/``` - Houses the code for the EHR Preprocessing Pipeline 
3.  ```Submission/``` - Houses all Files for Submissions to Various Science Fairs and Conferences
	*  ```Martinos-Symposium/``` - Houses all files used in the preparation of a poster for the [Women in Science Symposium](https://wis.martinos.org/mcss/) on August 13th, 2021 
	* ```ML4H-Paper/```  -  Houses all files used in the preparation of my [accepted Extended Abstract paper subsmission](https://arxiv.org/abs/2111.09115) (30 accepted out of over 500 submissions) for the [ML4H Conference](https://ml4health.github.io/2021/papers.html) 
	* ```ML4H-Presentation/```  - Houses all files used in the preparation of my poster  presentation for the [ML4H Conference](https://ml4health.github.io/2021/papers.html) on December 5th, 2021 

Each folder will also contain a ```README.md``` file that goes into further detail regarding its contents. 

**Note**: All folders named "Old" house code that was created during previous iterations of the project. All files in these folders are not relevant to the material discussed in the paper and do not need to be examined. Thank you!
