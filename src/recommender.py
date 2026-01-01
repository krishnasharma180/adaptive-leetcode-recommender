
"""
LeetCode Personalized Recommender System 

This module builds a personalized recommendation session
based on topic mastery, difficulty preference, and controlled exploration.

"""

import pandas as pd
import ast
import math
from datetime  import datetime,timezone
import random


'''
progress contains the data for all the solved questions
questions contains the data for all available questons on leetcode

'''

progress=pd.read_csv('./data/progress.csv')
questions=pd.read_csv('./data/questions.csv')

progress.drop(progress.columns[0],axis=1,inplace=True)
questions.drop(questions.columns[0],axis=1,inplace=True)

'''
Encoding difficulty column and converting topicTags to type list

'''


progress['difficulty']=progress['difficulty'].replace({
    'EASY':1,
    'MEDIUM':2,
    'HARD':3,
})

questions['difficulty']=questions['difficulty'].replace({
    'EASY':1,
    'MEDIUM':2,
    'HARD':3,
})

def to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        return ast.literal_eval(x)
    return []

questions['topicTags'] = questions['topicTags'].apply(to_list)
progress['topicTags']=progress['topicTags'].apply(to_list)


'''
Creating dict for topics that have done till now with the topic score

'''

topics = {}
def time_decay(x):
    return math.exp(-x/30)

progress['lastSubmittedAt']=pd.to_datetime(progress['lastSubmittedAt'],utc=True)
now=datetime.now(timezone.utc)
progress['days_ago']=(now - progress['lastSubmittedAt']).dt.days

for _, row in progress.iterrows():
    decay=time_decay(row['days_ago'])

    difficulty_weight = (row['difficulty'] / row['numSubmitted'])*decay 
    for topic in row['topicTags']:
        slug = topic['slug']
        topics[slug] = topics.get(slug, 0) + difficulty_weight



topic_mastery_series = pd.Series(topics)

CORE_PERCENTILE = 60
CORE_THRESHOLD = topic_mastery_series.quantile(CORE_PERCENTILE / 100)

core_topics = set(
    topic_mastery_series[
        topic_mastery_series >= CORE_THRESHOLD
    ].index
)

'''
Introducing topic_count column for number of topics in a particular question

'''
candidates = questions[questions['status'] != 'SOLVED'].copy()

topics_set = core_topics

candidates['topic_count'] = candidates['topicTags'].apply(
    lambda tags: sum(1 for t in tags if t['slug'] in topics_set)
)

candidates=candidates[candidates['topic_count']>=1]

candidates['new_topic_count']=candidates['topicTags'].apply(
    lambda tags:sum(1 for t in tags if t['slug'] not in topics_set)
)



def novelty_penalty(num_new):

    '''
    This function gives a penalty for a number of new topic in question as more new topics mean more penalty so less reommendation

    '''
    if num_new==0:
        return 0.0
    elif num_new==1:
        return 0.5
    else:
        return 2
    
candidates['novelty_penalty']=candidates['new_topic_count'].apply(novelty_penalty)


current_level=progress['difficulty'].median()

def difficulty_weight(diff):
    '''
    This function gives a difficulty weight to question the weight depends on the current difficulty level --(here it is medium/2 )

    '''
    if diff == current_level:
        return 1.0
    elif diff == current_level+1:
        return 0.8
    elif diff == current_level-1:
        return 0.3
    else:
        return 0
    
candidates['difficulty_weight']=candidates['difficulty'].apply(difficulty_weight)



def topic_relevance(tags,topics):
    '''
    This function gives a relevence for each question based on number of topics and sum their topic scores and creates a new feature topic_score

    '''
    return sum(topics.get(t['slug'],0) for t in tags)

candidates['topic_score']=candidates['topicTags'].apply(
    lambda tags: topic_relevance(tags,topics)
)


def bucket(x):
    '''
    This function helps to introduce a new feature that gives idea about the condition of a question and return safe,stretch and explore according to num of new topics in a question

    '''
    if x==0:
        return "safe"
    elif x==1:
        return "stretch"
    else:
        return "explore"
    
candidates['bucket']=candidates['new_topic_count'].apply(bucket)

candidates['final_score']=candidates['topic_score']*candidates['difficulty_weight']-candidates['novelty_penalty']


probs={
    'reinforce':0.3,
    'progress':0.6,
    'challenge':0.1
    }

def difficulty_bucket(x):
    # The function difficulty_bucket gives names based on wheather the question is easy:reinforce, medium:progress , hard:challenge
    if(x==1):
        return 'reinforce'
    elif(x==2):
        return 'progress'
    else:
        return 'challenge'
    
def sample_selection(k=5):
    # The function sample_selection is used to randomly choose difficulty buckets that will introduce randomness for difficulty in question
    
    buckets=list(probs.keys())
    weights=list(probs.values())
    return random.choices(buckets,weights,k=k)
    
    
candidates['diff_bucket']=candidates['difficulty'].apply(difficulty_bucket)
x=sample_selection()


topic_bucket=['safe','safe','safe','stretch','explore']


def difficulty_match_score(actual, desired):
    # The function difficulty_match_score is used to select the desire question if present else the next best question
    
    if actual == desired:
        return 1.0
    if actual == 'progress':
        return 0.7
    return 0.3


def select_question(candidates, topic_bucket, difficulty_bucket):
    # The function select_question is used to selct question based on given topic_bucket and difficulty bucket
    
    pool = candidates[candidates['bucket'] == topic_bucket]

    if pool.empty:
        return None

    pool = pool.copy()
    pool['difficulty_match'] = pool['diff_bucket'].apply(
        lambda d: difficulty_match_score(d, difficulty_bucket)
    )

    pool['combined_score'] = pool['final_score'] * pool['difficulty_match']

    return pool.sort_values('combined_score', ascending=False).iloc[0]



def build_session(candidates, topic_plan, difficulty_plan):
    # The function build_session is used to create top 5 recommendation and select questions using the above two functions 
    
    session = []
    remaining = candidates.copy()

    for t_bucket, d_bucket in zip(topic_plan, difficulty_plan):
        q = select_question(remaining, t_bucket, d_bucket)

        if q is None:
            continue

        session.append(q)
        remaining = remaining.drop(q.name)

    return session

recommendations=build_session(candidates,topic_bucket,x)
recommendations=pd.DataFrame(recommendations)
print(recommendations)