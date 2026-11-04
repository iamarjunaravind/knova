import csv
import io
import json
try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        def _delay(*args, **kwargs):
            return func(*args, **kwargs)
        func.delay = _delay
        return func

from django.utils import timezone
from .models import DataImportJob, University, Course, Scholarship, CourseCategory
from django.utils.text import slugify

@shared_task
def process_data_import_task(job_id):
    try:
        job = DataImportJob.objects.get(id=job_id)
    except DataImportJob.DoesNotExist:
        return
        
    job.status = 'PROCESSING'
    job.started_at = timezone.now()
    job.save()
    
    error_report = []
    successful_rows = 0
    failed_rows = 0
    duplicate_rows = 0
    
    try:
        # Read the file
        job.uploaded_file.open(mode='rb')
        content = job.uploaded_file.read().decode('utf-8')
        job.uploaded_file.close()
        
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        job.total_rows = len(rows)
        job.save()
        
        for index, row in enumerate(rows, start=1):
            try:
                if job.import_type == 'UNIVERSITY':
                    result = process_university_row(row)
                elif job.import_type == 'COURSE':
                    result = process_course_row(row)
                elif job.import_type == 'SCHOLARSHIP':
                    result = process_scholarship_row(row)
                else:
                    raise ValueError(f"Unknown import type {job.import_type}")
                    
                if result == 'CREATED' or result == 'UPDATED':
                    successful_rows += 1
                elif result == 'DUPLICATE':
                    duplicate_rows += 1
            except Exception as e:
                failed_rows += 1
                error_report.append({
                    'row': index,
                    'error': str(e),
                    'suggested': "Check your formatting or missing required fields."
                })
                
        job.successful_rows = successful_rows
        job.failed_rows = failed_rows
        job.duplicate_rows = duplicate_rows
        job.error_report = error_report
        
        if failed_rows > 0:
            job.status = 'COMPLETED_WITH_ERRORS'
        else:
            job.status = 'COMPLETED'
            
    except Exception as e:
        job.status = 'FAILED'
        job.error_report = [{'row': 0, 'error': str(e), 'suggested': 'Invalid file format or system error.'}]
        
    job.completed_at = timezone.now()
    job.save()

def process_university_row(row):
    name = row.get('name', '').strip()
    if not name:
        raise ValueError("Missing university name")
        
    slug = row.get('slug', '').strip() or slugify(name)
    website = row.get('website', '').strip()
    
    # Try to find duplicate by slug
    uni = University.objects.filter(slug=slug).first()
    if uni:
        return 'DUPLICATE'
        
    University.objects.create(
        name=name,
        slug=slug,
        website=website,
        is_approved=True
    )
    return 'CREATED'

def process_course_row(row):
    name = row.get('name', '').strip()
    uni_name = row.get('university', '').strip()
    level = row.get('level', '').strip()
    
    if not name or not uni_name:
        raise ValueError("Missing course name or university")
        
    uni = University.objects.filter(name__iexact=uni_name).first()
    if not uni:
        raise ValueError(f"University '{uni_name}' not found")
        
    # Find existing course
    course = Course.objects.filter(university=uni, name__iexact=name, level__iexact=level).first()
    if course:
        return 'DUPLICATE'
        
    Course.objects.create(
        university=uni,
        name=name,
        level=level,
        duration=row.get('duration', '').strip(),
        tuition_fee=row.get('tuition_fee', '').strip()
    )
    return 'CREATED'

def process_scholarship_row(row):
    name = row.get('name', '').strip()
    uni_name = row.get('university', '').strip()
    amount = row.get('amount', '').strip()
    
    if not name or not uni_name:
        raise ValueError("Missing scholarship name or university")
        
    uni = University.objects.filter(name__iexact=uni_name).first()
    if not uni:
        raise ValueError(f"University '{uni_name}' not found")
        
    schol = Scholarship.objects.filter(university=uni, name__iexact=name).first()
    if schol:
        return 'DUPLICATE'
        
    Scholarship.objects.create(
        university=uni,
        name=name,
        amount=amount,
        eligibility=row.get('eligibility', '').strip(),
        description=row.get('description', '').strip()
    )
    return 'CREATED'
