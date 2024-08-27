from nltk.corpus import stopwords

NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E',
    'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
    'SSC', 'HSC', 'A.A', 'AA', 'A.A.', 
    'BA', 'B.A.', 'BS', 'B.S.', 'B.E.', 'BEd', 'BFA', 'BBA', 'BArch', 'BScEng',
    'BCom', 'BMus', 'BTech', 'BSocSc', 'MA', 'M.A.', 'MS', 'M.S.', 'MBA', 'MEd',
    'MFA', 'MPH', 'MPA', 'MScEng', 'MSW', 'MCom', 'MPhil', 'MTech', 'LLM', 'MD',
    'MCA', 'PhD', 'EdD', 'DSc', 'JD', 'DBA', 'EngD', 'DDS', 'DVM', 'DO', 'PharmD',
    'DMin', 'PsyD', 'DNP'
]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'

NUMBER = r'\d+'

MONTHS_SHORT = r'''(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)
                   |(aug)|(sep)|(oct)|(nov)|(dec)'''
MONTHS_LONG = r'''(january)|(february)|(march)|(april)|(may)|(june)|(july)|
                   (august)|(september)|(october)|(november)|(december)'''
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'

STOPWORDS = set(stopwords.words('english'))

RESUME_SECTIONS = [
    'experience',
    'education',
    'interests',
    'professional experience',
    'publications',
    'skills',
    'certifications',
    'objective',
    'summary of skills',
    'career objective',
    'summary',
    'leadership',
    'accomplishments',
    'projects',
    'references',
    'work experience'
]