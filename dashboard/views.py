from django.shortcuts import render, redirect
from .forms import ExperimentDataForm
from .models import ExperimentData, Deadline
from datetime import date
from .forms import ExperimentSearchForm
from .forms import DeadlineForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from .forms import TemplateForm
import pandas as pd
import os
from django.conf import settings
import matplotlib.pyplot as plt
# Create your views here.
def home(request):
    return render(request, 'home.html')

def upload(request):
    if request.method == 'POST':
        form = ExperimentDataForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Replace with the name of your home view
    else:
        form = ExperimentDataForm()
    return render(request, 'upload.html', {'form': form})

def download(request):
    # form = ExperimentSearchForm()
    # experiments = None
    
    # if 'experiment_number' in request.GET:
    #     experiment_number = request.GET['experiment_number']
    #     matrikel_number = request.GET.get('matrikel_number', '')
        
    #     experiments = ExperimentData.objects.filter(
    #         experiment_number=experiment_number
    #     )
        
    #     if matrikel_number:
    #         experiments = experiments.filter(matrikel_number__icontains=matrikel_number)
            
    # return render(request, 'download.html', {
    #     'form': form,
    #     'experiments': experiments
    # })
    form = ExperimentSearchForm(request.GET or None)
    experiments = ExperimentData.objects.all()

    if form.is_valid():
        experiment_number = form.cleaned_data.get("experiment_number")
        matrikel_number = form.cleaned_data.get("matrikel_number")
        semester = form.cleaned_data.get("semester")
        
        if experiment_number:
            experiments = experiments.filter(experiment_number=experiment_number)
        if matrikel_number is not None:
            experiments = experiments.filter(matrikel_number=matrikel_number)
        if semester:
            experiments = experiments.filter(semester=semester)

    context = {
        "form": form,
        "experiments": experiments
    }
    return render(request, "download.html", context)
def analyze(request):
    return render(request, 'analyze.html')

def input_experiment(request):
    if request.method == 'POST':
        form = DeadlineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Replace with the name of your home view
    else:
        form = DeadlineForm()
    return render(request, 'input_experiment.html', {'form': form})

def upload_template(request):
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a confirmation page or the main page
    else:
        form = TemplateForm()
    return render(request, 'upload_template.html', {'form': form})



@login_required
# def my_submissions(request):
#     experiments = ExperimentData.objects.filter(matrikel_number=request.user.username)
#     deadlines = {obj.experiment_name: obj.experiment_deadline for obj in Deadline.objects.all()}
#     today = date.today()

#     for experiment in experiments:
#         deadline = deadlines.get(experiment.experiment_number, None)
#         if deadline:
#             # Assuming deadline is a datetime object
#             deadline_date = deadline.date()
#             experiment.show_update_delete = False if today > deadline_date else True
#         else:
#             experiment.show_update_delete = True
    
#     context = {
#         'experiments': experiments,
#     }
#     return render(request, 'my_submissions.html',  context)
def my_submissions(request):
    experiments = ExperimentData.objects.filter(matrikel_number=request.user.username)
    today = datetime.now()
    today = timezone.now()

    for experiment in experiments:
        # Try to get the deadline for the experiment, matrikel_number, and semester
        try:
            deadline_obj = Deadline.objects.get(
                experiment_name=experiment.experiment_number,
                matrikel_number=request.user.username,
                semester=experiment.semester  # Assuming semester is a field in ExperimentData
            )
            deadline = deadline_obj.experiment_deadline
        except Deadline.DoesNotExist:
            deadline = None

        if deadline:
            experiment.show_update_delete = today <= deadline
        else:
            experiment.show_update_delete = True
    
    context = {
        'experiments': experiments,
    }
    return render(request, 'my_submissions.html', context)

@login_required
def update_experiment(request, experiment_id):
    experiment = ExperimentData.objects.get(id=experiment_id)
    if request.method == 'POST':
        form = ExperimentDataForm(request.POST, request.FILES, instance=experiment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('my_submissions'))
    else:
        form = ExperimentDataForm(instance=experiment)
    return render(request, 'update_experiment.html', {'form': form})


@login_required
def delete_experiment(request, experiment_id):
    experiment = ExperimentData.objects.get(id=experiment_id)
    experiment.delete()
    return HttpResponseRedirect(reverse('my_submissions'))

def analyze(request):
    form = ExperimentSearchForm()
    experiments = None
    analysis_data = None
    plots = {}
    
    if request.method == 'GET':
        form = ExperimentSearchForm(request.GET)
        if form.is_valid():
            experiment_number = form.cleaned_data['experiment_number']
            matrikel_number = form.cleaned_data['matrikel_number']
            semester = form.cleaned_data['semester']

            experiments = ExperimentData.objects.all()

            if experiment_number:
                experiments = experiments.filter(experiment_number=experiment_number)
            if matrikel_number:
                experiments = experiments.filter(matrikel_number=matrikel_number)
            if semester:
                experiments = experiments.filter(semester=semester)

            if 'analyze_id' in request.GET:
                analyze_id = request.GET['analyze_id']
                experiment_to_analyze = ExperimentData.objects.get(id=analyze_id)
                file_path = experiment_to_analyze.raw_data.path
                
                plot_dir = os.path.join(settings.MEDIA_ROOT, 'plots')
                
                if not os.path.exists(plot_dir):
                    os.makedirs(plot_dir)

                if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    xls = pd.ExcelFile(file_path)
                    analysis_data = {}
                    sheet_titles = []
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name)
                        sheet_title = df.columns[0]
                        #analysis_data[sheet_name] = df.to_dict()
                        analysis_data[sheet_name] = {'data': df.to_dict(), 'sheet_title': sheet_title}
                        sheet_titles.append(sheet_title)
                        # Check if the sheet has exactly 2 columns
                        if len(df.columns) == 2:
                            # Convert data to float and plot
                            plt.figure()
                            second_row_data = df.iloc[0, :] 
                            plt.plot(df.iloc[2:, 0].astype(float), df.iloc[2:, 1].astype(float))
                            # plt.xlabel(df.columns[0])
                            # plt.ylabel(df.columns[1])
                            plt.xlabel(str(second_row_data[0]))
                            plt.ylabel(str(second_row_data[1]))
                            plt.title(sheet_name)
                            img_path = os.path.join(plot_dir, f"{sheet_name}.png")
                            plt.savefig(img_path)
                            # Store the relative path
                            relative_img_path = os.path.join('plots', f"{sheet_name}.png")
                            plots[sheet_name] = relative_img_path


    return render(request, 'analyze.html', {
        'form': form,
        'experiments': experiments,
        'analysis_data': analysis_data,
        'plots': plots,
        'sheet_titles': sheet_titles
    })

# def analyze(request):
#     form = ExperimentSearchForm()
#     experiments = None
#     analysis_data = None
#     plots = {}
#     if request.method == 'GET':
#         form = ExperimentSearchForm(request.GET)
#         if form.is_valid():
#             # ... (your existing code)
#             experiment_number = form.cleaned_data['experiment_number']
#             matrikel_number = form.cleaned_data['matrikel_number']
#             semester = form.cleaned_data['semester']

#             experiments = ExperimentData.objects.all()

#             if experiment_number:
#                 experiments = experiments.filter(experiment_number=experiment_number)
#             if matrikel_number:
#                 experiments = experiments.filter(matrikel_number=matrikel_number)
#             if semester:
#                 experiments = experiments.filter(semester=semester)
#             if 'analyze_id' in request.GET:
#                 analyze_id = request.GET['analyze_id']
#                 experiment_to_analyze = ExperimentData.objects.get(id=analyze_id)
#                 file_path = experiment_to_analyze.raw_data.path
#                 plot_dir = 'static/plots/'
#                 if not os.path.exists(plot_dir):
#                     os.makedirs(plot_dir)

#                 if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
#                     xls = pd.ExcelFile(file_path)
#                     analysis_data = {}
#                     plots = {}
#                     for sheet_name in xls.sheet_names:
#                         df = pd.read_excel(xls, sheet_name)
#                         analysis_data[sheet_name] = df.to_dict()
#                         print(df.dtypes)
#                         # Check if the sheet has exactly two columns
#                         if len(df.columns) == 2:
#                             # Assume the data is plottable for now
#                             import matplotlib.pyplot as plt
#                             plt.figure()
#                             plt.plot(df.iloc[1:, 0].astype(float), df.iloc[1:, 1].astype(float))
#                             plt.xlabel(df.columns[0])
#                             plt.ylabel(df.columns[1])
#                             plt.title(sheet_name)
#                             img_path = f"static/plots/{sheet_name}.png"
#                             plt.savefig(img_path)
#                             plots[sheet_name] = img_path

#     return render(request, 'analyze.html', {
#         'form': form,
#         'experiments': experiments,
#         'analysis_data': analysis_data,
#         'plots': plots
#     })
    #         if 'analyze_id' in request.GET:
    #             analyze_id = request.GET['analyze_id']
    #             experiment_to_analyze = ExperimentData.objects.get(id=analyze_id)
    #             file_path = experiment_to_analyze.raw_data.path

    #             if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    #                 xls = pd.ExcelFile(file_path)
    #                 analysis_data = {}
    #                 for sheet_name in xls.sheet_names:
    #                     df = pd.read_excel(xls, sheet_name)
    #                     analysis_data[sheet_name] = df.to_dict(orient='records')  # This line is changed

    # return render(request, 'analyze.html', {
    #     'form': form,
    #     'experiments': experiments,
    #     'analysis_data': analysis_data
    # })

# def analyze(request):
#     form = ExperimentSearchForm()
#     experiments = None
#     analysis_data = None
    
#     if request.method == 'GET':
#         form = ExperimentSearchForm(request.GET)
#         if form.is_valid():
#             experiment_number = form.cleaned_data['experiment_number']
#             matrikel_number = form.cleaned_data['matrikel_number']
#             semester = form.cleaned_data['semester']

#             experiments = ExperimentData.objects.all()

#             if experiment_number:
#                 experiments = experiments.filter(experiment_number=experiment_number)
#             if matrikel_number:
#                 experiments = experiments.filter(matrikel_number=matrikel_number)
#             if semester:
#                 experiments = experiments.filter(semester=semester)

#             if 'analyze_id' in request.GET:
#                 analyze_id = request.GET['analyze_id']
#                 experiment_to_analyze = ExperimentData.objects.get(id=analyze_id)
#                 file_path = experiment_to_analyze.raw_data.path

#                 if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
#                     xls = pd.ExcelFile(file_path)
#                     analysis_data = {}
#                     for sheet_name in xls.sheet_names:
#                         df = pd.read_excel(xls, sheet_name)
#                         analysis_data[sheet_name] = df.to_dict()

#     return render(request, 'analyze.html', {
#         'form': form,
#         'experiments': experiments,
#         'analysis_data': analysis_data
#     })
