# 🤖 STYLO – Image Search Service (CNN)

AI microservice cung cấp chức năng **tìm kiếm sản phẩm bằng hình ảnh**
cho hệ thống **Stylo – Fashion Store Management System**.
Service này cho phép tìm ra các sản phẩm tương tự dựa trên hình ảnh đầu vào
thông qua việc trích xuất đặc trưng bằng mạng nơ-ron tích chập (CNN).

---

## 📦 System Context

Repo này là một **AI service độc lập**, được Backend API gọi thông qua REST API
để xử lý các yêu cầu tìm kiếm sản phẩm bằng hình ảnh.

Luồng hoạt động tổng quát:

```text
Backend API
     ↓
AI Image Search Service
     ↓
Danh sách sản phẩm tương tự
````

Service không giao tiếp trực tiếp với frontend.

---

## 🎯 Responsibilities

* Nhận và tiền xử lý hình ảnh đầu vào
* Trích xuất đặc trưng hình ảnh bằng CNN
* Lưu trữ và quản lý vector embedding
* Truy vấn các sản phẩm tương tự dựa trên độ tương đồng
* Trả kết quả về cho backend dưới dạng dữ liệu chuẩn hóa

---

## 🧠 Model & Techniques

### CNN (Convolutional Neural Network)

* Sử dụng CNN để trích xuất đặc trưng thị giác từ hình ảnh sản phẩm
* Vector embedding được lấy từ các layer cuối của mô hình

### Similarity Search

* Vector Database: FAISS
* Similarity Metric: Cosine Similarity

### Rationale

* CNN phù hợp cho bài toán trích xuất đặc trưng hình ảnh
* FAISS cho phép tìm kiếm nhanh trên không gian vector nhiều chiều
* Cosine Similarity giúp so sánh mức độ tương đồng hình ảnh hiệu quả

---

## 📊 Data Processing Pipeline

1. Nhận hình ảnh đầu vào từ backend
2. Resize và chuẩn hóa ảnh
3. Trích xuất vector embedding bằng CNN
4. So khớp embedding với FAISS index
5. Tính độ tương đồng bằng Cosine Similarity
6. Trả về danh sách sản phẩm tương tự nhất

---

## 🔌 API

### POST `/search-by-image`

Tìm kiếm các sản phẩm tương tự dựa trên hình ảnh đầu vào.

#### Request

* Content-Type: `multipart/form-data`
* Body:

  * `image`: file ảnh sản phẩm

#### Response Example

```json
{
  "results": [
    {
      "product_id": 3,
      "similarity_score": 0.91
    },
    {
      "product_id": 8,
      "similarity_score": 0.86
    }
  ]
}
```

---

## 🛠 Tech Stack

* **Language**: Python
* **Framework**: FastAPI
* **Deep Learning**: TensorFlow
* **Vector Database**: FAISS
* **Similarity Metric**: Cosine Similarity
* **API Style**: RESTful API

---

## 🚀 Run Locally

### Prerequisites

* Python 3.9+

### Setup & Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Service sẽ chạy mặc định tại:

```
http://localhost:8000
```

---

## 📁 Project Structure

```text
app/
 ├─ models/         # CNN model & weights
 ├─ services/       # Image processing & search logic
 ├─ utils/          # Tiện ích xử lý ảnh
 ├─ data/           # FAISS index & metadata
 └─ main.py         # Entry point
```

---

## ⚠️ Limitations

* Độ chính xác phụ thuộc vào chất lượng dữ liệu huấn luyện
* Chưa phân biệt tốt các thuộc tính trừu tượng (giới tính, phong cách)
* Hiệu năng có thể giảm khi dữ liệu tăng mạnh nếu chưa tối ưu index

---

## 🔮 Future Improvements

* Fine-tune CNN với dữ liệu chuyên biệt theo danh mục thời trang
* Sử dụng embedding từ các mô hình sâu hơn (ResNet, EfficientNet)
* Kết hợp metadata (category, color) để cải thiện kết quả tìm kiếm
* Tối ưu FAISS index cho tập dữ liệu lớn hơn
Bạn muốn phần AI tìm kiếm ảnh này thiên về **tối ưu độ chính xác** hay **tối ưu tốc độ truy vấn**?
