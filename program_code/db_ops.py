import csv 
import pandas as pd
import sys 
sys.path.insert(0, 'spaCy-training') 
import resume_parser, jobdesc_parser, comparison
from pathlib import Path

def database(cv, jobdesc, directory): 
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    cv_doc = resume_parser.parser(cv)
    desc_doc = jobdesc_parser.job_desc_details(jobdesc)

    parsed_resume = pd.DataFrame([cv_doc])
    parsed_description = pd.DataFrame([desc_doc])

    intersection, similarity, jaccard, name = comparison.matching_result_wrapper(jobdesc, cv)
    comparative_data = {
        "Intersection": [intersection], 
        "Similarity": [similarity], 
        "Jaccard": [jaccard],
    }
    comparative_list = pd.DataFrame(comparative_data)

    parsed_resume.to_csv(directory / 'resumes.csv', mode='a', index=True, header=not (directory / 'resumes.csv').exists())
    parsed_description.to_csv(directory / 'descriptions.csv', mode='a', index=True, header=not (directory / 'descriptions.csv').exists())
    comparative_list.to_csv(directory / 'comparisons.csv', mode='a', index=True, header=not (directory / 'comparisons.csv').exists())
