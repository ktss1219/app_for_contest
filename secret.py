#to Firebase Admin SDK Module 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('serviceAccountKey.json')  # Firebase Admin SDKの秘密鍵へのパス
#Firebase admin sdk 初期化
firebase_admin.initialize_app(cred)
db = firestore.client()

#ここでユーザの秘密を保存✨✨
def save_to_firestore(user_input):
    doc_ref = db.collection('user').document('useId')  # 'user_messages'という名前の新しいコレクションを作成
    doc_ref.set({
        'private': user_input
    })
