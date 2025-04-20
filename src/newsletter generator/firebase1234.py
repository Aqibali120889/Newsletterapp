# app/services/firebase.py
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, Any, List, Optional

class FirebaseService:
    def __init__(self):
        # Initialize Firebase
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    async def save_newsletter(self, user_id: str, title: str, content: str, 
                       topics: List[str]) -> str:
        """
        Save newsletter to Firestore
        """
        newsletter_ref = self.db.collection("newsletters").document()
        
        await newsletter_ref.set({
            "userId": user_id,
            "title": title,
            "content": content,
            "topics": topics,
            "createdAt": firestore.SERVER_TIMESTAMP
        })
        
        return newsletter_ref.id
    
    async def get_newsletter(self, newsletter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get newsletter from Firestore
        """
        doc = await self.db.collection("newsletters").document(newsletter_id).get()
        
        if doc.exists:
            return doc.to_dict()
        
        return None
    
    async def get_user_newsletters(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all newsletters for a user
        """
        query = await self.db.collection("newsletters").where("userId", "==", user_id).get()
        
        return [doc.to_dict() for doc in query]