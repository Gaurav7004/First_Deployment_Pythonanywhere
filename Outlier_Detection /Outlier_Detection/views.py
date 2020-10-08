from django.shortcuts import render
import numpy as np
import pandas as pd, os, glob
import codecs
from django.http import HttpResponse
from .functions import handle_uploaded_file
from .forms import UploadForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as djangoSettings
# evaluate model performance with outliers removed using isolation forest
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error
# file storage on disks
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def home(request):
    #import pdb; pdb.set_trace()
    global path_of_uploaded_csv
    if request.method == 'POST':
            UploadedData = UploadForm(request.POST, request.FILES)
            if UploadedData.is_valid():
                # Dataframe
                try :
                    dataframe = pd.read_csv(request.FILES['file'])
                except :
                    return render(request,'home.html', {'message': True})
                    
                    
                No_of_Rows = dataframe.shape[0]

                d_frame = request.FILES['file']
                # import pdb; pdb.set_trace()

                #File Storage on Disks
                fs = FileSystemStorage()
                fs.save(d_frame.name ,d_frame)

                #list of columns
                df = dataframe.select_dtypes(exclude=["bool_","object_"])
                list_for_pop = df.columns
                import csv
                path_of_uploaded_csv = request.FILES['file']

                import json
                json_object = {list_for_pop.get_loc(c): c for idx, c in enumerate(list_for_pop)}

                path_of_uploaded_csv.flush()
                return render(request, 'home.html', {'DataFrame': dataframe, 'item':list_for_pop, 'path':path_of_uploaded_csv, 'json_response':json_object, 'noOfRows':No_of_Rows})

            elif(request.POST.get):
                #Dependent dropdown
                try:
                    dpost_list = request.POST.getlist('dropdown1')
                except :
                    return render(request,'home.html', {'warning1': True})
                    
                print(dpost_list)
                
                #Independent Dropdown
                try:
                    ipost_list = request.POST.getlist('dropdown2')
                except :
                    return render(request,'home.html', {'warning2': True})
                
                z = request.POST.getlist('2std')
                w = request.POST.getlist('3std')
                # import pdb; pdb.set_trace()

                df_path = request.POST.get('path')
                # print(df_path + '============= df_path ===================')
                dataframe = pd.read_csv(df_path)
                
                try :
                    var1 = toInitializeOutlierDetection(dpost_list, ipost_list, dataframe)
                except :
                    return render(request,'home.html', {'warning3': True})

                #var3 = (z[0] == '2 Standard Deviation') if True Conn_CheckBox1(var1) else Conn_CheckBox2(var1)
                try :
                    var3 = Conn_CheckBox1(var1) if (z == '2 Standard Deviation' is True) else Conn_CheckBox2(var1)
                except :
                    return render(request,'home.html', {'warning4': True})
                
                var4 = detectOutliers()
                from django.conf import settings
                from django.conf.urls.static import static
                import os
                path = "/home/gaurav/Desktop/Outlier Detection Website/Outlier_Detection/static"
                var4.to_csv('/home/gaurav/Desktop/Outlier Detection Website/Outlier_Detection/static/Final_Outliers.csv', encoding='utf-8')
                
                # flushing dataset
                if(os.path.isfile(df_path)):
                    os.remove(df_path)
                    
                return render(request, 'home.html', {'DataFrame': var4, 'path':path })

            elif(request.POST.get):
                converted_to_csv = var4.to_csv(df_path, 'Final_Outliers.csv', sep=',', encoding='utf-8', index=False,header=True)


    else:
        UploadedData = UploadForm()
        return render(request,"home.html",{'form':UploadedData })

@csrf_exempt
def selected_data(request):
    if request.method == 'POST':
        #import pdb;pdb.set_trace()
        return render(request,"home.html")
    return render(request,"home.html")


def toInitializeOutlierDetection(dpost_list, ipost_list, dataframe):
    global df
    # y1 is target dataframe coming from onSelectTargetCol
    y = pd.DataFrame(dataframe, columns=dpost_list)

    # selecting final columns selected by the user and passed into X as a dataframe
    X = pd.DataFrame(dataframe, columns=ipost_list)

    df = dataframe
    # split dataframe into X variable choosing multiple independent columns
    # it gets converted to matrix
    X = X.values

    # it gets converted to matrix
    y = y.values

    # identify outliers in the training dataset
    # contamination hyperparameter is fluctuating at (0.1201 to 0.1209)

    clf = IsolationForest(n_estimators=100, max_samples='auto', contamination='auto', max_features=1.0, bootstrap=False, verbose=0)
    clf.fit(X, y)

    df_anomalyScore = clf.decision_function(X)
    df['anomaly_scores'] = pd.DataFrame(df_anomalyScore)

    # finding STD Deviation
    Std = df['anomaly_scores'].std(axis = 0)

    # findinng Mean
    Mean = df['anomaly_scores'].mean(axis=0)

    df['outlier'] = 0
    df['Std'] = df['anomaly_scores'].std(axis = 0)
    df['Mean'] = df['anomaly_scores'].mean(axis=0)
    # return Mean and Standard Deviation
    return df

# Check Box 1 returning 2 Std Deviation
def Conn_CheckBox1(var1):
    #-----------
    global df
    df = var1
    #df = toInitializeOutlierDetection()

    df['outlier'] = np.where((df['anomaly_scores'] < (df['Mean']- (2*df['Std']))), 1, 0)
    df['outlier_1'] = np.where((df['anomaly_scores'] > (df['Mean']+ (2*df['Std']))), 1, 0)
    df.outlier =  df.outlier + df.outlier_1

    return df

# Check Box 2 returning 3 Std Deviation
def Conn_CheckBox2(var1):
    #-----------
    global df
    df = var1
    #df = toInitializeOutlierDetection()

    df['outlier'] = np.where((df['anomaly_scores'] < (df['Mean']- (3*df['Std']))), 1, 0)
    df['outlier_1'] = np.where((df['anomaly_scores'] > (df['Mean']+ (3*df['Std']))), 1, 0)
    df.outlier =  df.outlier + df.outlier_1

    return df

# Outlier Detection Function
def detectOutliers():

    global df
    # # dropping Std, Mean, Outlier_1
    del df['Std']
    del df['Mean']
    del df['outlier_1']
    del df['anomaly_scores']


    # Displaying in no. of outliers in lcdNumber_2
    outlier_list = df['outlier'].tolist()


    # Imputing yes with 1 and no with 0
    df['outlier'] = np.where(df['outlier'] == 1, 'Yes', 'No')
    return df

def exportToCSV(var4, df_path):
    print('=============not working =================')
    converted_to_csv = var4.to_csv('/static/Final_Outliers.csv', sep=',', encoding='utf-8', index=False,header=True)
    return converted_to_csv
