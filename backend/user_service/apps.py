from django.apps import AppConfig

class DocumentsConfig(AppConfig):
    name = "user_service"

    def ready(self):
        # create pgvector table on app startup
        # only runs once when Django starts
        from utils.vector_store import setup_vector_table
        try:
            setup_vector_table()
        except Exception as e:
            print(f"Vector table setup warning: {e}")


# from django.apps import AppConfig

# class UserServiceConfig(AppConfig):
#     name = "user_service"

#     def ready(self):
#         try:
#             from .models import Document
#             from utils.vector_store import add_document_to_index

#             docs = Document.objects.filter(
#                 status="completed",
#                 extracted_content__isnull=False
#             )
#             for doc in docs:
#                 add_document_to_index(doc.id, doc.extracted_content)
#         except Exception:
#             pass  