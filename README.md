# <center>NeuraHealth: An Automated Screening Pipeline to Detect Undiagnosed Cognitive Impairment in Electronic Health Records using Deep Learning and Natural Language Processing</center>

## Author
Tanish Tyagi

## Abstract
Dementia related cognitive impairment (CI) is a neurodegenerative disorder, affecting over 55 million people worldwide and growing rapidly at the rate of one new case every 3 seconds. 75% cases go undiagnosed globally with up to 90% in low-and-middle-income countries, leading to an estimated annual worldwide cost of USD 1.3 trillion, forecasted to reach 2.8 trillion by 2030. With no cure, a recurring failure of clinical trials, and a lack of early diagnosis, the mortality rate is 100%. Information in electronic health records (EHRs) can provide vital clues for early detection of CI, but a manual review by experts is tedious and error prone. Several computational methods have been proposed, however, they lack an enhanced understanding of the linguistic context in complex language structures of EHRs. Therefore, I propose a novel and more accurate framework, NeuraHealth, to identify patients who had no earlier diagnosis. In NeuraHealth, using patient EHRs from Mass General Brigham BioBank, I trained a bi-directional attention-based deep learning natural language processing model to classify sequences. The sequence predictions were used to generate structured features as input for a patient level regularized logistic regression model. This two-step framework creates high dimensionality, outperforming all existing state-of-the-art computational methods as well as clinical methods. Further, I integrate the models into a real-world product, a web app, to create an automated EHR screening pipeline for scalable and high-speed discovery of undetected CI in EHRs, making early diagnosis viable in medical facilities and in regions with scarce health services.

## Navigating the Codebase
1. ```Models/``` - Houses all the code for the Machine Learning (```TFIDF/```) and Deep Learning (```Bert/```) models 
2. ```Preprocessing/``` - Houses the code for the EHR Preprocessing Pipeline 
3.  ```Submission/``` - Houses all Files for Submissions to Various Science Fairs and Conferences
	* ``Davidson/`` - Houses all files used in preparation for submission to Davidson Research Fellowship
	*  ```Martinos-Symposium/``` - Houses all files used in the preparation of a poster for the [Women in Science Symposium](https://wis.martinos.org/mcss/) on August 13th, 2021 
	* ```ML4H-Paper/```  -  Houses all files used in the preparation of my [accepted Extended Abstract paper subsmission](https://arxiv.org/abs/2111.09115) (30 accepted out of over 500 submissions) for the [ML4H Conference](https://ml4health.github.io/2021/papers.html) 
	* ```ML4H-Presentation/```  - Houses all files used in the preparation of my poster  presentation for the [ML4H Conference](https://ml4health.github.io/2021/papers.html) on December 5th, 2021 

Each folder will also contain a ```README.md``` file that goes into further detail regarding its contents. 

**Note**: 
1. All folders named "Old" house code that was created during previous iterations of the project. All files in these folders are not relevant to the material discussed in the paper and do not need to be examined. Thank you!
2. Unless otherwise stated, all the code in the attached files is written by me. I use Import statements to call functions from external libraries.
