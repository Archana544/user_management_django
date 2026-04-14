from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.http import JsonResponse
from django.db import connection
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

from .models import Document
from .serializers import (
    DocumentSerializer,
    UserSerializer,
    TitleOnlySerializer
)
from utils.document_parser import extract_pdf_text, parse_csv
from utils.vector_store import search_similar_chunks, add_document_to_index
from utils.rag_pipeline import build_rag_prompt
from utils.llm_service import generate_answer
from utils.kafka_producer import publish_document_uploaded, publish_document_processed, publish_document_failed

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)

        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,          
                secure=not settings.DEBUG, 
                samesite="Lax",          
                max_age=7 * 24 * 60 * 60, 
                path="/api/token/refresh/" 
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found. Please login again."},
                status=401
            )

        request.data["refresh"] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)
            new_refresh = response.data.pop("refresh", None)

            if new_refresh:
                response.set_cookie(
                    key="refresh_token",
                    value=new_refresh,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    max_age=7 * 24 * 60 * 60,
                    path="/api/token/refresh/"
                )

            return response

        except TokenError as e:
            return Response(
                {"error": "Session expired. Please login again."},
                status=401
            )

@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

    except TokenError:
        pass

    response = Response({"message": "Logged out successfully."})
    response.delete_cookie(
        key="refresh_token",
        path="/api/token/refresh/"
    )

    return response

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

        publish_document_uploaded(document.id, self.request.user.id)

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


            publish_document_processed(document.id, self.request.user.id)

        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}", exc_info=True)
            document.status = "failed"
            document.extracted_content = f"Extraction failed: {str(e)}"
            document.save()

            publish_document_failed(document.id, self.request.user.id, str(e))


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def rag_chat(request):
    if not getattr(settings, "ENABLE_RAG", False):
        return Response({"answer": "RAG system is currently disabled."})

    try:
        query = request.data.get("query")
        document_id = request.data.get("document_id")  
        if not query:
            return Response({"error": "Query missing"}, status=400)
        if not document_id:
            return Response({"error": "Document ID missing"}, status=400)

        print(f"[RAG] Query received: {query} | Document ID: {document_id}")


        context_chunks = search_similar_chunks(query, top_k=3, document_id=document_id)
        print(f"[RAG] Chunks found: {len(context_chunks)}")
        print(f"[RAG] Chunks content: {context_chunks}")

        if not context_chunks:
            return Response({
                "answer": "No relevant documents found in the database.",
                "debug": "0 chunks retrieved — document may not be indexed"
            })

        prompt = build_rag_prompt(query, context_chunks)
        print(f"[RAG] Prompt built: {prompt[:200]}")

        answer = generate_answer(prompt)
        print(f"[RAG] Answer: {answer}")

        return Response({
            "answer": answer,
            "chunks_used": len(context_chunks),
        })

    except Exception as e:
        logger.error(str(e), exc_info=True)
        return Response({"error": str(e)}, status=500)