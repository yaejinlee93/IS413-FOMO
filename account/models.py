from django.db import models


class Question(models.Model):
    # slower, but unlimited amount of text
    # WIN-WIN!!! Postgresql is faster here (and unlimited)
    question_text = models.TextField(blank=True, null=True)
    # much faster, but length limited
    # question_text = models.CharField(max_length=200, blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(null=True)


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
