# Generated by Django 2.1.5 on 2019-04-05 03:21

from django.db import migrations

POLLUTANTS = [
    {
        "abbreviation": "pm2.5",
        "name": "Particle Matter under 2.5 microns"
    },
    {
        "abbreviation": "pm10",
        "name": "Particle Matter under 10 microns"
    },
    {
        "abbreviation": "so2",
        "name": "Sulfur Dioxide"
    },
    {
        "abbreviation": "no2",
        "name": "Nitrogen Dioxide"
    },
    {
        "abbreviation": "o3",
        "name": "Ozone"
    },
    {
        "abbreviation": "co",
        "name": "Carbon Monoxide"
    }
]

PROFILE_QUESTIONS = [
    {
        "q": "How do you commute to work?",
        "a": ["By own car", "By public transport", "By bike", "By walk", "None of the options"],
        "i": {
            "no2": [0,1,2,2,0],
            "o3": [0,1,2,2,0],
            "pm2.5": [0,1,2,2,0]
        }
    }, {
        "q": "Is your age between 18 and 65?",
        "a": ["yes", "no"],
        "i": {
            "no2": [0,3],
            "o3": [0,3],
            "pm2.5": [0,3]
        }
    }, {
        "q": "Which proportion of your working/studying hours do you spend outdoors?",
        "a": ["More than 75%", "Between 50% to 75%", "Less than 50%", "I do not work/study", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0,0,0],
            "o3": [3,2,1,0,0],
            "pm2.5": [0,0,0,0,0]
        }
    }, {
        "q": "Which proportion of your working/studying hours do you spend in sitting position?",
        "a": ["More than 75%", "Between 50% to 75%", "Less than 50%", "I do not work/study", "I do not know/Not sure"],
        "i": {
            "no2": [2,1,0,0,0],
            "o3": [2,1,0,0,0],
            "pm2.5": [3,2,1,0,0]
        }
    }, {
        "q": "How often do you do physical exercises?",
        "a": ["I do not exercise", "Less than once a week", "1-2 times a week", "3-5 times a week", "More than 5 times a week", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0,1,2,0],
            "o3": [0,0,0,1,2,0],
            "pm2.5": [3,2,1,0,0,0]
        }
    }, {
        "q": "How often do you eat fast food?",
        "a": ["I do not eat fast food", "Less than once a week", "1-2 times a week", "3-5 times a week", "More than 5 times a week", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0,1,2,0],
            "o3": [0,0,0,1,2,0],
            "pm2.5": [0,0,1,2,3,0]
        }
    }, {
        "q": "How often do you smoke?",
        "a": ["I do not smoke", "Less than once a day", "1-2 times a day", "3-5 times a day", "More than 5 times a day", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,1,2,3,0],
            "o3": [0,0,1,2,3,0],
            "pm2.5": [0,0,0,0,0,0]
        }
    }, {
        "q": "Does anyone in your family smoke?",
        "a": ["Yes, I live with a smoking person", "No, I live with non-smokers", "I do not know/Not sure"],
        "i": {
            "no2": [2,0,0],
            "o3": [2,0,0],
            "pm2.5": [0,0,0]
        }
    }, {
        "q": "How often do you consume alcohol drinks?",
        "a": ["I do not drink alcohol", "Less than once a week", "1-2 times a week", "3-5 times a week", "More than 5 times a week", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,1,2,3,0],
            "o3": [0,0,1,2,3,0],
            "pm2.5": [0,0,1,2,3,0]
        }
    }, {
        "q": "How would you assess your health conditions in terms of breathlessness?",
        "a": ["No breathlessness except with strenuous exercise", "Short of breath when hurrying or walking up a slight hill", "Walk slower on flat ground than friends/have to stop for breath when walking at your own pace", "Stop for breath after walking for a few minutes on the flat", "Breathless when dressing/undressing or too breathless to leave the house sometimes", "Breathless when sitting still"],
        "i": {
            "no2": [0,1,2,3,4,4],
            "o3": [0,1,2,3,4,4],
            "pm2.5": [0,1,2,3,4,4]
        }
    }, {
        "q": "Does anyone in your family have lung diseases?",
        "a": ["My parent(s)", "My sibling(s)", "My spouse", "My child(ren)", "No", "I do not know/Not sure"],
        "i": {
            "no2": [1,1,1,0,0,0],
            "o3": [1,1,1,0,0,0],
            "pm2.5": [0,0,0,0,0,0]
        }
    }, {
        "q": "Does anyone in your family have heart diseases?",
        "a": ["My parent(s)", "My sibling(s)", "My spouse", "My child(ren)", "No", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0,0,0,0],
            "o3": [0,0,0,0,0,0],
            "pm2.5": [1,1,1,0,0,0]
        }
    }, {
        "q": "The LAST time you had your blood pressure checked, was it normal or high?",
        "a": ["High", "Normal", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0],
            "o3": [0,0,0],
            "pm2.5": [3,0,0]
        }
    }, {
        "q": "The LAST time you had your cholesterol checked, was it normal or high?",
        "a": ["High", "Normal", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0],
            "o3": [0,0,0],
            "pm2.5": [3,0,0]
        }
    }, {
        "q": "Do you have asthma?",
        "a": ["Yes", "No", "I do not know/Not sure"],
        "i": {
            "no2": [4,0,0],
            "o3": [4,0,0],
            "pm2.5": [4,0,0]
        }
    }, {
        "q": "Do you have allergy to pollen?",
        "a": ["Yes", "No", "I do not know/Not sure"],
        "i": {
            "no2": [3,0,0],
            "o3": [3,0,0],
            "pm2.5": [3,0,0]
        }
    }, {
        "q": "Do you have diabetes?",
        "a": ["Yes", "No", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0],
            "o3": [0,0,0],
            "pm2.5": [3,0,0]
        }
    }, {
        "q": "Are you aware of any heart diseases (hypertension, coronary artery disease, etc.) you have?",
        "a": ["Yes, I am aware. And I have heart diseases", "Yes, I am aware. And I do not have any heart diseases", "I do not know/Not sure"],
        "i": {
            "no2": [0,0,0],
            "o3": [0,0,0],
            "pm2.5": [4,0,0]
        }
    }, {
        "q": "Are you aware of any lung diseases (chronic bronchitis, emphysema, chronic obstructive pulmonary disease, etc.) you have?",
        "a": ["Yes, I am aware. And I have lung diseases", "Yes, I am aware. And I do not have any lung diseases", "I do not know/Not sure"],
        "i": {
            "no2": [4,0,0],
            "o3": [4,0,0],
            "pm2.5": [4,0,0]
        }
    }, {
        "q": "If you are female, are you pregnant?",
        "a": ["Yes", "No", "I am not female"],
        "i": {
            "no2": [3,0,0],
            "o3": [3,0,0],
            "pm2.5": [3,0,0]
        }
    }
]


def insert_pollutants(apps, schema_editor):
    Pollutant = apps.get_model('common', 'Pollutant')
    for obj in POLLUTANTS:
        Pollutant.objects.get_or_create(**obj)


def insert_questions(apps, schema_editor):
    ProfileQuestion = apps.get_model('common', 'ProfileQuestion')
    ProfileQuestionAnswer = apps.get_model('common', 'ProfileQuestionAnswer')
    ProfileAnswerPollutantIndex = apps.get_model(
        'common', 'ProfileAnswerPollutantIndex')
    for order, q in enumerate(PROFILE_QUESTIONS):
        question, created = ProfileQuestion.objects.get_or_create(
            order=order + 1, defaults={"text": q['q']})
        for a_order, a in enumerate(q['a']):
            answer, a_created = ProfileQuestionAnswer.objects.get_or_create(
                order=a_order + 1, question=question, defaults={"text": a})
            for k, v in q['i'].items():
                ProfileAnswerPollutantIndex.objects.get_or_create(
                    answer=answer, pollutant_id=k, defaults={
                        "index": v[a_order]})


def revert_pollutants(apps, schema_editor):
    Pollutant = apps.get_model('common', 'Pollutant')
    Pollutant.objects.all().delete()


def revert_questions(apps, schema_editor):
    ProfileQuestion = apps.get_model('common', 'ProfileQuestion')
    ProfileQuestionAnswer = apps.get_model('common', 'ProfileQuestionAnswer')
    ProfileAnswerPollutantIndex = apps.get_model(
        'common', 'ProfileAnswerPollutantIndex')
    ProfileAnswerPollutantIndex.objects.all().delete()
    ProfileQuestionAnswer.objects.all().delete()
    ProfileQuestion.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_questionnaire_models'),
    ]

    operations = [
        migrations.RunPython(insert_pollutants, revert_pollutants),
        migrations.RunPython(insert_questions, revert_questions)
    ]
