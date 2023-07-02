from django.test import TestCase
from django.utils import timezone
import datetime
from .models import Question
from django.urls import reverse


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a `pub_date` in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a `pub_date` in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionModelTests(TestCase):
    def test_was_published_in_day_with_more_than_day_old_question(self):
        day_plus_second_difference = datetime.timedelta(days=1, seconds=1)
        small_difference_time = timezone.now() - day_plus_second_difference
        small_difference_question = Question(pub_date=small_difference_time)
        self.assertIs(small_difference_question.was_published_in_day(), False)

        thirty_day_difference = datetime.timedelta(days=30)
        thirty_day_difference_time = timezone.now() - thirty_day_difference
        thirty_day_difference_question = Question(pub_date=thirty_day_difference_time)
        self.assertIs(thirty_day_difference_question.was_published_in_day(), False)

    def test_was_published_in_day_with_less_than_day_old_question(self):
        day_minus_second_difference = datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        day_minus_second_time = timezone.now() - day_minus_second_difference
        correct_question = Question(pub_date=day_minus_second_time)
        self.assertIs(correct_question.was_published_in_day(), True)

        now_time = timezone.now()
        now_question = Question(pub_date=now_time)
        self.assertIs(now_question.was_published_in_day(), True)

    def test_was_published_in_day_with_future_question(self):
        day_plus_second_difference = datetime.timedelta(days=1, seconds=1)
        day_plus_second_difference_time = timezone.now() + day_plus_second_difference
        day_plus_second_difference_question = Question(
            pub_date=day_plus_second_difference_time
        )
        self.assertIs(day_plus_second_difference_question.was_published_in_day(), False)

        second_difference = datetime.timedelta(seconds=1)
        second_difference_time = timezone.now() + second_difference
        second_difference_question = Question(pub_date=second_difference_time)
        self.assertIs(second_difference_question.was_published_in_day(), False)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
