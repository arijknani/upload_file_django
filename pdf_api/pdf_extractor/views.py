from django.shortcuts import render
from django.http import JsonResponse
import PyPDF2
from django.views.decorators.csrf import csrf_exempt
from .models import PDFFile
import io

def extract_technical_skills(pdf_text):

    # Find the starting index of the Technical Skills section
    technical_skills_header = 'Technical Skills'
    start_index = pdf_text.find(technical_skills_header)
    if start_index == -1:
        print('Technical Skills section not found')
        exit()

    # Find the ending index of the Technical Skills section
    soft_skills = 'Soft Skills'
    end_index = pdf_text.find(soft_skills, start_index)
    if end_index == -1:
        end_index = len(pdf_text) - 1
    # Extract the Technical Skills section
    technical_skills_section = pdf_text[start_index:end_index]
    # Split the section into lines
    lines = technical_skills_section.strip().split('\n')
    # Extract the lines after the "Soft Skills" header line
    Technical_skills_lines = [line.strip() for line in lines[1:] if line.strip()]
    # Print the Technical Skills lines
    return Technical_skills_lines

def get_pdf_text(request):
    if request.method == 'GET':
        # Get the PDF ID from the request object
        pdf_id = request.GET.get('pdf_id')
        if not pdf_id:
            return JsonResponse({'error': 'PDF ID parameter is missing.'}, status=400)
        
        # Get the PDF object from the database using the PDF ID
        try:
            pdf_obj = PDFFile.objects.get(id=pdf_id)
        except PDFFile.DoesNotExist:
            return JsonResponse({'error': 'PDF file not found in the database.'}, status=404)

        # Retrieve the text field from the PDF object
        pdf_text = pdf_obj.text

        # Extract the Technical Skills section from the PDF text
        technical_skills_section = extract_technical_skills(pdf_text)

        # Return the text field as a response
        return JsonResponse({'pdf_text': pdf_text, 'technical_skills': technical_skills_section})
    else:
        # Return an error response for non-GET requests
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def save_pdf(request):
    if request.method == 'POST':
        # Get the uploaded PDF file from the request object
        pdf_file = request.FILES['pdf_file']
        
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        num_pages = len(pdf_reader.pages)
        
        # Extract text from each page and concatenate into a single string
        text = ''
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

        # Save the PDF file to the database
        pdf_obj = PDFFile(file=pdf_file, text=text)
        pdf_obj.save()

        # Return a success response
        return JsonResponse({'message': 'PDF file saved successfully.'})
    else:
        # Return an error response for non-POST requests
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
