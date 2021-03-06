# Generated by Django 2.1.5 on 2019-04-05 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_questionnaire_data'),
        ('accounts', '0003_auto_20190401_1853'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileQuestionnaireAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_questionnaire_answers', to='common.ProfileQuestionAnswer', verbose_name='Answer')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionnaire_answers', to='accounts.UserProfile', verbose_name='User Profile')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_questionnaire_answers', to='common.ProfileQuestion', verbose_name='Question')),
            ],
            options={
                'verbose_name': 'User Questionnaire Answer',
                'verbose_name_plural': 'User Questionnaire Answers',
                'db_table': 'user_questionnaire_answer',
            },
        ),
    ]
