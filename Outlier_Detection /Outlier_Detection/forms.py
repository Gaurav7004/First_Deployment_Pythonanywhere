from django import forms  

class UploadForm(forms.Form):  
    file =  forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"})) # for creating file input 
    

    
