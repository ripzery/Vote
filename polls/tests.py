from django.test import TestCase
import datetime

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Question


# Create your tests here.


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return false from question whose pub_date is in the future.
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whos pub_date is within 1 day
        :return:
        """
        time = timezone.now() - datetime.timedelta(hours=23)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
        Creates a question with the given `question_text` and published the
        given number of `days` offset to now (negative for questions published
        in the past, positive for questions that have yet to be published).
        """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Question with pub_date in the past should be display in the index page.
        :return:
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Question with pub_date both in the past and the future should be display only past question
        :return:
        """
        create_question(question_text="Future question.", days=30)
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_index_view_with_two_past_questions(self):
        """
        The question index page may display multiple questions.
        :return:
        """
        create_question(question_text="Past question1.", days=-30)
        create_question(question_text="Past question2.", days=-29)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question2.>',
                                                                            '<Question: Past question1.>'])


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_future_question(self):
        """
        The detail view of the question with a pub_date in the future should be return a 404 not found.
        :return:
        """
        future_question = create_question("Future questions.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_past_question(self):
        """
        The detail view of the question with a pub_date in the past should be return the question's text
        :return:
        """
        past_question = create_question("Past question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
