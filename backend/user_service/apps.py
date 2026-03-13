from django.apps import AppConfig

class UserServiceConfig(AppConfig):
    name = "user_service"

    def ready(self):
        try:
            from .models import Document
            from utils.vector_store import add_document_to_index

            docs = Document.objects.filter(
                status="completed",
                extracted_content__isnull=False
            )
            for doc in docs:
                add_document_to_index(doc.id, doc.extracted_content)
        except Exception:
            pass  