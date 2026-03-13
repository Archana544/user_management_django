# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class DocumentAPITest(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="testuser",
#             password="testpass"
#         )
#         # login and get token
#         response = self.client.post("/api/v1/token/", {
#             "username": "testuser",
#             "password": "testpass"
#         })
#         self.token = response.data["access"]
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

#     def test_list_documents(self):
#         response = self.client.get("/api/v1/documents/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_filter_by_file_type(self):
#         response = self.client.get("/api/v1/documents/?file_type=PDF")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for doc in response.data:
#             self.assertEqual(doc["file_type"], "PDF")

#     def test_rag_chat_disabled(self):
#         response = self.client.post("/api/v1/rag/chat/", {"query": "test"})
#         self.assertEqual(response.data["answer"], "RAG system is currently disabled.")