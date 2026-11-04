import os
import sys
import django
import random
from django.db import transaction

# Setup Django Environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import ScholarshipExam, ExamQuestion, QuestionChoice
from scripts.questions_data.numerical import get_numerical_questions
from scripts.questions_data.verbal import get_verbal_questions
from scripts.questions_data.logical import get_logical_questions
from scripts.questions_data.technical import get_technical_questions
from scripts.questions_data.gk import get_gk_questions

def populate_database():
    print("=" * 60)
    print("KNOVA SCHOLARSHIP EXAM: 1,000 QUALITY QUESTIONS POPULATOR")
    print("=" * 60)

    exam, _ = ScholarshipExam.objects.get_or_create(id=1, defaults={'title': 'Full Scholarship Exam (100 Questions)'})
    exam.title = 'Full Scholarship Exam (100 Questions)'
    exam.total_marks = 100
    exam.duration_minutes = 120
    exam.save()

    categories = [
        ("Numerical Ability", get_numerical_questions()),
        ("Verbal Ability", get_verbal_questions()),
        ("Logical Reasoning", get_logical_questions()),
        ("Technical Skills", get_technical_questions()),
        ("General Knowledge", get_gk_questions()),
    ]

    total_loaded = 0
    total_choices = 0

    with transaction.atomic():
        print("Clearing previous questions for Exam 1...")
        ExamQuestion.objects.filter(exam=exam).delete()

        global_order = 1
        for sec_name, q_list in categories:
            print(f"Loading {len(q_list)} questions for '{sec_name}'...")
            assert len(q_list) == 200, f"Expected 200 questions for {sec_name}, got {len(q_list)}"

            for item in q_list:
                q_text = item["text"]
                choices = item["choices"]  # list of (text, is_correct) tuples

                question = ExamQuestion.objects.create(
                    exam=exam,
                    section_name=sec_name,
                    text=q_text,
                    marks=1,
                    order=global_order
                )
                global_order += 1
                total_loaded += 1

                # Randomize choice positions so correct answer is scattered between A, B, C, D
                shuffled_choices = list(choices)
                random.shuffle(shuffled_choices)

                for c_text, is_corr in shuffled_choices:
                    QuestionChoice.objects.create(
                        question=question,
                        text=c_text,
                        is_correct=is_corr
                    )
                    total_choices += 1

    print("=" * 60)
    print(f"SUCCESSFULLY POPULATED:")
    print(f" - Total Questions in Exam 1: {ExamQuestion.objects.filter(exam=exam).count()}")
    print(f" - Total Question Choices: {QuestionChoice.objects.filter(question__exam=exam).count()}")
    for sec_name, _ in categories:
        cnt = ExamQuestion.objects.filter(exam=exam, section_name=sec_name).count()
        print(f"   * {sec_name}: {cnt} questions")
    print("=" * 60)

if __name__ == "__main__":
    populate_database()
