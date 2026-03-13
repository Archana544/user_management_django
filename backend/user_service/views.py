from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.db import connection
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Document
from .serializers import DocumentSerializer, UserSerializer, TitleOnlySerializer
from utils.document_parser import extract_pdf_text, parse_csv
from utils.vector_store import search_similar_chunks
from utils.vector_store import add_document_to_index
from utils.rag_pipeline import build_rag_prompt
from utils.llm_service import generate_answer

User = get_user_model()
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserSerializer

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)

#         refresh_token = response.data.pop("refresh")  

#         response.set_cookie(
#             key="refresh_token",
#             value=refresh_token,
#             httponly=True,
#             secure=not settings.DEBUG,
#             samesite="Lax",
#             max_age=30 * 24 * 60 * 60,
#         )

#         return response  # body now only has { "access": "..." }


# class CustomTokenRefreshView(TokenRefreshView):

#     def post(self, request, *args, **kwargs):
#         refresh_token = request.COOKIES.get("refresh_token")

#         if not refresh_token:
#             return Response({"error": "Refresh token not found."}, status=401)

#         request.data["refresh"] = refresh_token

#         return super().post(request, *args, **kwargs)

class UserProfileView(viewsets.ViewSet):  
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):  
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Document.objects.filter(user=self.request.user)

        title           = self.request.query_params.get("title")
        doc_id          = self.request.query_params.get("id")
        file_type       = self.request.query_params.get("file_type")  
        status          = self.request.query_params.get("status") 
        uploaded_after  = self.request.query_params.get("uploaded_after")   
        uploaded_before = self.request.query_params.get("uploaded_before")  
        retry_count     = self.request.query_params.get("retry_count")

        if title:
           queryset = queryset.filter(title__icontains=title)
        if doc_id:
           queryset = queryset.filter(id=doc_id)
        if file_type:
           queryset = queryset.filter(file_type=file_type.upper())  
        if status:
           queryset = queryset.filter(status=status.upper())        
        if uploaded_after:
           queryset = queryset.filter(uploaded_at__gte=uploaded_after)
        if uploaded_before:
           queryset = queryset.filter(uploaded_at__lte=uploaded_before)
        if retry_count:
            queryset = queryset.filter(retry_count=retry_count)

        return queryset
    
    def get_serializer_class(self):
        if self.request.query_params.get("fields") == "title":
            return TitleOnlySerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save(
            user=self.request.user,
            file_type=serializer.validated_data["file"].name.split('.')[-1].upper(),
            status="UPLOADED",
            retry_count=0,      
            max_retries=3
        )

        file_path = document.file.path

        try:
            if document.file_type == "PDF":
                extracted_content = extract_pdf_text(file_path)

            elif document.file_type == "CSV":
                extracted_content = parse_csv(file_path)

            else:
                extracted_content = ""

            document.extracted_content = extracted_content
            document.status = "EMBEDDING_CREATED"
            document.save()

            add_document_to_index(document.id, extracted_content)
            document.status = "LLM_RESPONSE_GENERATED"
            document.save()

            document.status = "completed"
            document.save()

        except Exception as e:
            document.status = "failed"
            document.extracted_content = f"Extraction failed: {str(e)}"
            document.save()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def rag_chat(request):
    if not getattr(settings, "ENABLE_RAG", False):
        return Response({"answer": "RAG system is currently disabled."})

    try:
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query missing"}, status=400)

        context_chunks = search_similar_chunks(query, top_k=3)
        prompt = build_rag_prompt(query, context_chunks)
        answer = generate_answer(prompt)
        return Response({"answer": answer})

    except Exception as e:
        logger.error(str(e), exc_info=True)
        return Response({"error": "Internal server error"}, status=500)
    
