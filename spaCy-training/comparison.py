from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobdesc_parser import job_desc_details
from resume_parser import parser


def to_percentage(value):
    percentage = value * 100
    return "{:.2f}".format(percentage)

def matching_result_wrapper(jd, resume):
    job_skills = job_desc_details(jd)['skills']
    resumes_skills = parser(resume)['skills']
    name = parser(resume)['name']
    score1,score2,score3 = simple_intersection_score(job_skills, resumes_skills, name), cosine_similarity_with_tfidf(job_skills, resumes_skills, name), jaccard_similarity_score(job_skills, resumes_skills, name)
    return score1,score2,score3,name

def simple_intersection_score(job_skills, resumes_skills, name):
    rank = []
    job_skills_set = set(job_skills)
    resume_skills_set = set(resumes_skills)
    common_skills = job_skills_set.intersection(resume_skills_set)
    score = len(common_skills) / len(job_skills_set)
    rank.append({'name': name, 'score': to_percentage(score)})
    return rank


def cosine_similarity_with_tfidf(job_skills, resumes_skills, name):
    rank = []
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([" ".join(job_skills), " ".join(resumes_skills)])
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])
    score = cosine_sim[0, 0]
    rank.append({'name': name, 'score': to_percentage(score)})
    return rank

def jaccard_similarity_score(job_skills, resumes_skills, name):
    rank = []
    job_skills_set = set(job_skills)
    resume_skills_set = set(resumes_skills)
    intersection = job_skills_set.intersection(resume_skills_set)
    union = job_skills_set.union(resume_skills_set)
    score = len(intersection) / len(union)
    rank.append({'name': name, 'score': to_percentage(score)})
    return rank 

def total_score(jd, resume):
    name = parser(resume)['name']
    intersection,similarity,jaccard,name = matching_result_wrapper(jd, resume)
    total_score = round(((float(intersection[0]['score']) + float(similarity[0]['score']) + float(jaccard[0]['score'])) / 3), 2)
    return total_score, name, intersection[0]['score'], similarity[0]['score']