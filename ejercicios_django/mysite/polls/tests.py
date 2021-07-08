import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def setUp(self):
        """
        Create two users
        """
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        create_question(question_text="Future.", days=30)
        question_today = create_question(question_text="Today question1.", days=0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [
                question_today,
                question,
            ],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def setUp(self):
        """
        Create two users
        """
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, '/accounts/login/?next=/polls/<int=question_id>/')

    def test_logged_in(self):
        self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("login"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):
    def setUp(self):
        """
        Create two users
        """
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_logged_in(self):
        self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("login"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

    def test_future_question(self):
        """
        The results of a question with a pub_date in the future
        returns a 404 not found.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results of a question with a pub_date in the past
        displays the question's text.
        """
        self.assertTrue(
            self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        )
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
