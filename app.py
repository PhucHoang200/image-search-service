import io
import os
import numpy as np
import pandas as pd
import faiss

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.utils import load_img, img_to_array

from database import (
    get_products_by_ids,
    get_all_sanpham_ids,
    get_fallback_products_same_category,
    get_category_by_sanpham_id
)

# 1. KHỞI TẠO FASTAPI 
app = FastAPI(title="Image Similarity API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # DEV OK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "OK", "message": "Image Similarity API is running"}

# 2. LOAD DATA & MODEL (LOAD 1 LẦN KHI START)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "image_similarity")

EMB_PATH = os.path.join(MODEL_DIR, "embeddings_norm.npy")
STYLES_PATH = os.path.join(MODEL_DIR, "styles_processed.csv")
FAISS_PATH = os.path.join(MODEL_DIR, "faiss_index.idx")

if not all(map(os.path.exists, [EMB_PATH, STYLES_PATH, FAISS_PATH])):
    raise RuntimeError("❌ Thiếu file model trong image_similarity")

print(" Loading embeddings & metadata...")
embeddings_norm = np.load(EMB_PATH)
styles = pd.read_csv(STYLES_PATH)

print("✔ embeddings:", embeddings_norm.shape)
print("✔ styles:", styles.shape)

print(" Loading FAISS index...")
index = faiss.read_index(FAISS_PATH)
print("✔ FAISS size:", index.ntotal)

if len(styles) != embeddings_norm.shape[0]:
    raise RuntimeError("❌ embeddings & styles không khớp")

IMG_SIZE = 224

print(" Loading EfficientNetB0...")
cnn_model = EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    pooling="avg"
)
cnn_model.trainable = False
print("✔ CNN ready")

# 3. HELPER FUNCTIONS

def extract_embedding_from_bytes(image_bytes: bytes) -> np.ndarray:
    img = load_img(io.BytesIO(image_bytes), target_size=(IMG_SIZE, IMG_SIZE))
    arr = img_to_array(img)
    arr = np.expand_dims(arr, 0)
    arr = preprocess_input(arr)

    emb = cnn_model.predict(arr, verbose=0)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    return emb.astype("float32")


def recommend_from_embedding(emb_norm, top_k=10, exclude_id=None):
    D, I = index.search(emb_norm, top_k + 1)

    results = []
    for idx, score in zip(I[0], D[0]):
        sp_id = int(styles.iloc[idx]["id"])

        if exclude_id and sp_id == exclude_id:
            continue

        results.append({"SanPhamID": sp_id, "similarity": float(score)})
        if len(results) == top_k:
            break

    return results

# 4. API SEARCH BY IMAGE
@app.post("/search-by-image")
async def search_by_image(file: UploadFile = File(...), k: int = 10):

    if k <= 0:
        raise HTTPException(400, "k phải > 0")

    try:
        image_bytes = await file.read()
        emb = extract_embedding_from_bytes(image_bytes)

        query_id = None
        name = os.path.splitext(file.filename)[0]
        if name.isdigit():
            query_id = int(name)

        faiss_results = recommend_from_embedding(emb, top_k=50)

        valid_ids = set(get_all_sanpham_ids())

        danh_muc_id, phan_loai_id = (None, None)
        if query_id and query_id in valid_ids:
            danh_muc_id, phan_loai_id = get_category_by_sanpham_id(query_id)

        filtered_ids = []
        for r in faiss_results:
            sp_id = r["SanPhamID"]

            if sp_id not in valid_ids:
                continue
            if query_id and sp_id == query_id:
                continue

            if phan_loai_id:
                _, pl = get_category_by_sanpham_id(sp_id)
                if pl != phan_loai_id:
                    continue

            filtered_ids.append(sp_id)
            if len(filtered_ids) == k:
                break

        products = get_products_by_ids(filtered_ids)

        if len(products) < k:
            products.extend(
                get_fallback_products_same_category(
                    phan_loai_id,
                    exclude_ids=filtered_ids,
                    limit=k - len(products)
                )
            )

        return {"count": len(products), "products": products}

    except Exception as e:
        raise HTTPException(500, str(e))

# 5. RUN SERVER
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
