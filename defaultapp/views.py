from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import GroupForm, GroupEditForm, UploadFileForm, TaskForm, NicknameForm, MessageForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.db.models import Count
from .models import Group, File, Task, Profile, Message, GroupJoinRequest
import boto3

# GENERAL VIEWS

# Call function to direct user to home page is signed in, else takes them to sign-in page 
def index(request):
    user = request.user
    if user.is_authenticated:
        return to_home(request)
    return render(request,'start.html')

# View to connect user to appropriate home page according to "clearance" 
def to_home(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('home-guest')
    elif user.groups.filter(name = "PMA administrator").exists():
        return redirect('home-pma')
    elif user.groups.filter(name = 'Common user').exists():
        return redirect('home-common')
    else:
        return home_guest(request)

# View to display "card gallery" of existing available groups to join (inclus)
def group_explore(request):
    user = request.user
    user_group_requests = GroupJoinRequest.objects.filter(user=user)
    requested_group_ids = user_group_requests.values_list('group__id', flat=True)
    
    user_context = {
        'all_groups' : Group.objects.exclude(owner=user).exclude(members=user), 
        'requested_group_ids': list(requested_group_ids),
    }
    return render(request, "group-explore.html", user_context)
# GUEST SPECIFIC VIEWS
# View to load guest home (needed context is just the existing groups)
def home_guest(request):
    context = {
        'all_groups': Group.objects.all(),
    }
    return render(request, "home-guest.html", context)

# COMMON USER SPECIFIC VIEWS
# View to load common user home (needed context is all group and files, and those specifically made/uploaded by the user)
@login_required
def home_common(request):
    user = request.user
    if user.groups.filter(name="PMA administrator").exists():
        return redirect('home-pma')
    display_name = user.profile.nickname if user.profile.nickname else user.get_full_name() or user.username

    # Fetch groups owned by the user
    user_groups = Group.objects.filter(owner=user).annotate(
        join_request_count=Count('groupjoinrequest')
    )
    member_groups = Group.objects.filter(members=user).annotate(
        join_request_count=Count('groupjoinrequest')  # If members want to see requests
    )  # Adjust this line based on your Group model

    all_groups = Group.objects.all()
    user_files = File.objects.filter(owner=user)
    files = File.objects.all()
    
    
    context = {
        'name': display_name,
        'user_groups': user_groups,  # Include groups in the context
        'member_groups': member_groups,  # Groups where user is a member
        'all_groups': all_groups,
        'user_files': user_files,
        'files': files,
    }
    return render(request, "home-common.html", context)

# View to create a new group (interacts with GroupForm) 
@login_required
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user  # Associate the group with the logged-in user
            group.save()
            return redirect('home-common')  # Redirect to a group list or detail view
    else:
        form = GroupForm()
    return render(request, 'group-create.html', {'form': form})

# View to edit existing group (interacts with GroupEditForm)
@login_required
def group_edit(request, group_id):
    current_group = get_object_or_404(Group, id=group_id, owner=request.user)
    members = current_group.members.exclude(id=current_group.owner.id)  # Exclude the owner from the members list


    if request.method == 'POST':
        form = GroupEditForm(request.POST, instance=current_group)
        if form.is_valid():
            form.save()
            return redirect('home-common')
    else:
        form = GroupEditForm(instance=current_group)
    return render(request, 'group-edit.html', {'form': form, 'group': current_group,  'members': members})

@login_required
def group_page(request, group_id):
    current_group = get_object_or_404(Group, id=group_id)
    files = current_group.files.all()
    tasks = current_group.tasks.all()
    messages = current_group.messages.all()
    members=current_group.members.all()

    if request.method == 'POST':
        task_form = TaskForm(request.POST)
        message_form = MessageForm(request.POST)
        if task_form.is_valid():
            task_instance = Task(group=current_group,
                                 name=task_form.cleaned_data['name'],
                                 completed=task_form.cleaned_data['completed'],)
            task_instance.save()
            return redirect('group-page', group_id=group_id)
        if message_form.is_valid():
            message_instance = Message(group=current_group,
                                       subject=message_form.cleaned_data['subject'],
                                       message=message_form.cleaned_data['message'],)
            message_instance.save()
            return redirect('group-page', group_id=group_id)
    else:
        task_form = TaskForm()
        message_form = MessageForm()
    file_keywords = {file.id: file.keywords for file in files}

    context = {
        'group' : current_group,
        'files' : files,
        'tasks' : tasks,
        'messages' : messages,
        'task_form' : task_form,
        'message_form' : message_form,
        'member_count': members.count(),
    }
    return render(request, 'group-page.html', context)

# Function to update task completion
def update_task(request, task_id, group_id):
    current_group = get_object_or_404(Group, id=group_id)
    task = get_object_or_404(current_group.tasks, id=task_id)
    task.completed = not task.completed  # Toggle completion status
    task.save()
    return redirect('group-page', group_id=group_id)

# deletes task from db
def delete_task(request, task_id, group_id):
    task = get_object_or_404(Task, id=task_id, group_id=group_id)
    task.delete()
    return redirect('group-page', group_id=group_id)

# deletes message from db
def delete_message(request, message_id, group_id):
    message = get_object_or_404(Message, id=message_id, group_id=group_id)
    message.delete()
    return redirect('group-page', group_id=group_id)

# View to upload a new file (current with no 'linked' group, but need to add support)
@login_required
def upload_file(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # This saves the file directly to S3
            file = form.cleaned_data['upload']
            file_name = default_storage.save(file.name, file)
            file_instance = File(upload=file_name, 
                        group=group,
                        owner=request.user,
                        description=form.cleaned_data['description'],
                        keywords=form.cleaned_data['keywords'])
            file_instance.save()  # Save the File instance
            return redirect('group-page', group_id=group_id)  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def delete_file(request, file_id):
    current_file = get_object_or_404(File, id=file_id, owner=request.user)
    group_id = current_file.group.id
    s3=boto3.client('s3')
    bucket_name = 'a09-static'
    file_key = 'media/' + current_file.upload.name

    try:
        s3.delete_object(Bucket=bucket_name, Key=file_key)
    except Exception as e:
        print(f"Error deleting file: {e}")
        return redirect('home-common')
    
    current_file.delete()
    return redirect('group-page', group_id=group_id)

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)
    s3 = boto3.client('s3')
    bucket_name = 'a09-static'

    # delete all files
    for file in group.files.all():
        try:
            file_key = 'media/' + file.upload.name
            s3.delete_object(Bucket=bucket_name, Key=file_key)

            file.delete()
        except Exception as e:
            print(f"Error deleting file {file.upload.name}: {e}")
            messages.error(request, f"Error deleting file {file.upload.name}. Some files might not have been deleted.")
            return redirect('home-common')
        
    # delete all tasks
    group.tasks.all().delete()
    
    # delete all messages
    group.messages.all().delete()
    
    group.delete()
    messages.success(request, f"The group {group.name} has been successfully deleted.")
    return redirect('home-common')
  
# PMA ADMINISTRATOR SPECIFIC VIEWS
# View to load PMA admin home (needed context is all group and account name)
@login_required
def home_pma(request):
    user = request.user
    if user.groups.filter(name = 'Common user').exists():
        return redirect('home-common')
    
    all_groups = Group.objects.all()
    
    context = {
        'name': request.user.get_full_name() or request.user.username,  # Use full name if available, else username
        'all_groups': all_groups,
    }
    return render(request, "home-pma.html", context)

@login_required
def delete_file_pma(request, file_id):
    current_file = get_object_or_404(File, id=file_id)
    group_id = current_file.group.id
    s3=boto3.client('s3')
    bucket_name = 'a09-static'
    file_key = 'media/' + current_file.upload.name

    try:
        s3.delete_object(Bucket=bucket_name, Key=file_key)
    except Exception as e:
        print(f"Error deleting file: {e}")
        return redirect('home-pma')
    
    current_file.delete()
    return redirect('home-pma')

@login_required
def delete_group_pma(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    s3 = boto3.client('s3')
    bucket_name = 'a09-static'

    for file in group.files.all():
        try:
            file_key = 'media/' + file.upload.name
            s3.delete_object(Bucket=bucket_name, Key=file_key)

            file.delete()
        except Exception as e:
            print(f"Error deleting file {file.upload.name}: {e}")
            messages.error(request, f"Error deleting file {file.upload.name}. Some files might not have been deleted.")
            return redirect('home-pma')
    
    # delete all tasks
    group.tasks.all().delete()
    
    # delete all messages
    group.messages.all().delete()
    
    group.delete()
    messages.success(request, f"The group {group.name} has been successfully deleted.")
    return redirect('home-pma')

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        if not GroupJoinRequest.objects.filter(user=request.user, group=group).exists():
            GroupJoinRequest.objects.create(user=request.user, group=group)
    return redirect('group-explore')

@login_required
def manage_join_requests(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.owner != request.user:  # Assuming `owner` is a field on Group
        return redirect('group-explore')  

    join_requests = GroupJoinRequest.objects.filter(group=group)

    if request.method == 'POST':
        action = request.POST.get('action')  # 'approve' or 'reject'
        request_id = request.POST.get('request_id')
        join_request = get_object_or_404(GroupJoinRequest, id=request_id)

        if action == 'approve':
            group.members.add(join_request.user)
            group.save()
            join_request.delete()  
        elif action == 'reject':
            join_request.delete()  

    return render(request, 'manage-requests.html', {'group': group, 'join_requests': join_requests})

@login_required
def approve_request(request, group_id, request_id):
    group = get_object_or_404(Group, id=group_id)
    if group.owner != request.user:  # Ensure only the owner can approve requests
        return redirect('group-explore')

    join_request = get_object_or_404(GroupJoinRequest, id=request_id, group=group)
    group.members.add(join_request.user)
    group.save()
    join_request.delete()  # Remove the join request after approval

    return redirect('manage-requests', group_id=group_id)

@login_required
def reject_request(request, group_id, request_id):
    group = get_object_or_404(Group, id=group_id)
    if group.owner != request.user:  
        return redirect('group-explore')

    join_request = get_object_or_404(GroupJoinRequest, id=request_id, group=group)
    join_request.delete()  # Simply delete the join request

    return redirect('manage-requests', group_id=group_id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Ensure the user is a member of the group
    if request.user in group.members.all():
        group.members.remove(request.user)  # Adjust this line based on your Group membership model
        # Optionally add a success message here, e.g., using Django messages framework
        # messages.success(request, "You have left the group successfully.")
    return redirect('home-common')  # Redirect to wherever appropriate after leaving the group


def profile_view(request):
    user = request.user

    # Ensure Profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = NicknameForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your nickname has been updated!")
            return redirect('user-info')  # Matches URL name in urls.py
    else:
        form = NicknameForm(instance=profile)

    context = {
        'form': form,
        'google_name': user.get_full_name(),
        'email': user.email,
        'nickname': profile.nickname,
        'profile': profile,
    }
    return render(request, 'user-info.html', context)




def remove_member_from_group(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)

    # Ensure the user is the group owner
    if request.user == group.owner:
        # Get the user to remove
        remove_user = get_object_or_404(User, id=user_id)

        # Ensure the user is a member of the group before removing
        if remove_user in group.members.all():
            if remove_user!=group.owner:
                group.members.remove(remove_user)  # Remove the user from the group
            # Optionally add a success message
            # messages.success(request, f"{remove_user.username} has been removed from the group.")
        else:
            # Optionally, add an error message if the user is not in the group
            # messages.error(request, f"{remove_user.username} is not a member of the group.")
            pass
        members = group.members.exclude(id=group.owner.id)  # Exclude the owner from the members list

        if request.method == 'POST':
            form = GroupEditForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect('home-common')
        else:
            form = GroupEditForm(instance=group)
    return render(request, 'group-edit.html', {'form': form, 'group': group, 'members': members})

