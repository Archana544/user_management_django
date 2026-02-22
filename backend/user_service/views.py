from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from utils.free_rag import retrieve_relevant_context
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Document
from PyPDF2 import PdfReader
from .serializers import UserSerializer, DocumentSerializer
import csv
import os
import openai
# from utils.rag_pipeline import index_document

User = get_user_model()
openai.api_key = os.getenv("OPENAI_API_KEY")

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserSerializer

class UserProfileView(viewsets.ViewSet):  
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):  
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

def extract_pdf_text(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
        print("EXTRACTED TEXT:", text)
    return text

def parse_csv(file_path):
    extracted_data = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Process each row here
            extracted_data.append(row)

    return extracted_data

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        document = serializer.save(
            user=self.request.user,
            file_type=serializer.validated_data["file"].name.split('.')[-1].upper()
        )

        file_path = document.file.path

        try:
            if document.file_type == "PDF":
                extracted_content = extract_pdf_text(file_path)

            elif document.file_type == "CSV":
                extracted_content = str(parse_csv(file_path))

            else:
                extracted_content = None

            document.extracted_content = extracted_content
            document.status = "completed"

        except Exception as e:
            document.extracted_content = f"Extraction failed: {str(e)}"
            document.status = "failed"
        document.save()


        # index_document(document.id, extracted_content)

@api_view(["POST"])
def rag_chat(request):

    query = request.data.get("query")

    context = retrieve_relevant_context(query)

    prompt = f"""
    Answer using the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a document assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return Response({
        "answer": response["choices"][0]["message"]["content"]
    })        