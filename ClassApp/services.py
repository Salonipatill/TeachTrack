from django.contrib.auth import get_user_model
from django.db import transaction
from .models import (Notification,Profile,Student,Faculty,Director,AuthenticatedStudent,Teacher)


def preserve_resource_file(resource):
    """Keep locally uploaded resource bytes available to other app instances."""
    from .models import Resource,ResourceFile
    with transaction.atomic():
        current=Resource.objects.select_for_update().get(pk=resource.pk)
        with current.file.open('rb') as source:
            content=source.read(30*1024*1024+1)
        if len(content)>30*1024*1024:
            raise ValueError('Resource files must be at most 30 MB.')
        saved,_=ResourceFile.objects.update_or_create(resource=current,defaults={
            'storage_name':current.file.name,'content':content,
        })
    return saved

def notify(users,title,message='',link=''):
    Notification.objects.bulk_create([Notification(recipient_id=pk,title=title,message=message,link=link)
        for pk in set(u.pk if hasattr(u,'pk') else u for u in users)],batch_size=500)
def audience_users(audience='all'):
    qs=get_user_model().objects.filter(is_active=True)
    return qs if audience=='all' else qs.filter(profile__role=audience)

def ensure_legacy(user,role=None):
    """Link new Django accounts to the original role tables and complaint wrappers."""
    role=role or Profile.objects.get(user=user).role
    name=user.get_full_name() or user.username
    if role=='student':
        item,_=Student.objects.get_or_create(user=user,defaults={'sname':name[:100],'semail':user.email,'unm':user.username[:50],'sen':'','sphone':''})
        AuthenticatedStudent.objects.get_or_create(user=user,defaults={'name':name[:100]})
    elif role=='faculty':
        email=user.email if user.email and not Faculty.objects.filter(femail__iexact=user.email).exists() else None
        item,_=Faculty.objects.get_or_create(user=user,defaults={'fname':name[:100],'femail':email,'unm':f'account_{user.pk}','fphone':''})
        Teacher.objects.get_or_create(user=user,defaults={'name':name[:100]})
    else:
        email=user.email
        if not email or Director.objects.filter(demail__iexact=email).exists():email=f'account-{user.pk}@example.invalid'
        item,_=Director.objects.get_or_create(user=user,defaults={'dname':name[:100],'demail':email,'unm':f'account_{user.pk}','dphone':''})
    return item
