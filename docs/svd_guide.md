# Phân rã ma trận SVD — hướng dẫn từ trực giác đến code

> Tài liệu tự học cho môn **Introduction to Data Science (PTIT)**, viết theo hướng
> "hiểu để dùng": mỗi công thức đều có ví dụ số cụ thể, mỗi ví dụ đều chạy lại được bằng
> [`docs/svd_demo.py`](svd_demo.py).
>
> ```bash
> python3 -m pip install numpy      # chỉ cần numpy
> python3 docs/svd_demo.py          # in toàn bộ 8 mục demo
> python3 docs/svd_demo.py --only 4 --save   # riêng phần nén ảnh, kèm ảnh PGM
> ```
>
> Số liệu in ra trong tài liệu này chính là output thật của lần chạy đó.

## Mục lục

1. [SVD là gì, trong một câu](#1-svd-là-gì-trong-một-câu)
2. [Phát biểu toán học và các mảnh ghép](#2-phát-biểu-toán-học-và-các-mảnh-ghép)
3. [Trực giác hình học](#3-trực-giác-hình-học)
4. [Ba cách "tìm ra" SVD](#4-ba-cách-tìm-ra-svd)
5. [Ví dụ tính tay đầy đủ (2×2)](#5-ví-dụ-tính-tay-đầy-đủ-22)
6. [Xấp xỉ hạng thấp — trái tim của ứng dụng](#6-xấp-xỉ-hạng-thấp--trái-tim-của-ứng-dụng)
7. [Chọn k như thế nào](#7-chọn-k-như-thế-nào)
8. [Ứng dụng: 5 bài toán đi kèm code](#8-ứng-dụng-5-bài-toán-đi-kèm-code)
9. [Code mẫu: numpy, scipy, sklearn](#9-code-mẫu-numpy-scipy-sklearn)
10. [Bẫy và lỗi thường gặp](#10-bẫy-và-lỗi-thường-gặp)
11. [Bài tập tự kiểm tra](#11-bài-tập-tự-kiểm-tra)
12. [Liên hệ với nội dung môn học](#12-liên-hệ-với-nội-dung-môn-học)

---

## 1. SVD là gì, trong một câu

**Mọi** ma trận $A$ kích thước $m\times n$ (không cần vuông, không cần đối xứng, không
cần khả nghịch) đều viết được thành:

$$
A = U\,\Sigma\,V^{\top}
$$

trong đó $U$ và $V$ là **ma trận trực giao** (các cột dài bằng 1, vuông góc nhau), còn
$\Sigma$ là ma trận **đường chéo** với các số không âm giảm dần
$\sigma_1 \ge \sigma_2 \ge \dots \ge 0$ gọi là **giá trị kỳ dị** (singular values).

Ba ý cần nhớ ngay:

| Ý | Nội dung |
| --- | --- |
| **Luôn tồn tại** | Không như phân rã trị riêng (chỉ có khi ma trận chéo hoá được), SVD có cho *mọi* ma trận thực/phức. |
| **Hai hệ cơ sở** | $U$ là cơ sở trực chuẩn của không gian đích $\mathbb{R}^m$, $V$ là cơ sở trực chuẩn của không gian nguồn $\mathbb{R}^n$. SVD nói: *"theo hai hệ cơ sở này, A chỉ là phép co giãn theo từng trục"*. |
| **Xếp hạng sẵn** | Số $\sigma_i > 0$ = hạng của $A$. $\sigma_i$ càng nhỏ thì hướng đó càng "ít thông tin" → cắt đi được. |

Vì sao môn KHDL quan tâm: SVD là công cụ *chuẩn* để **giảm chiều**, **khử nhiễu**,
**nén**, **tìm cấu trúc ẩn** trong dữ liệu bảng, văn bản, ảnh, và ma trận đánh giá
(recommender system).

---

## 2. Phát biểu toán học và các mảnh ghép

### 2.1 Hai phiên bản kích thước

Cho $A \in \mathbb{R}^{m\times n}$, giả sử $m \ge n$ (nếu không thì làm việc với $A^\top$).

| Kiểu | $U$ | $\Sigma$ | $V$ | Ghi chú |
| --- | --- | --- | --- | --- |
| **Full SVD** | $m\times m$ | $m\times n$ | $n\times n$ | numpy: `full_matrices=True` (mặc định) |
| **Economy / reduced** | $m\times r$ | $r\times r$ | $n\times r$ | $r=\min(m,n)$ — dùng trong thực tế, `full_matrices=False` |

Phần "dư" của full SVD chỉ là cơ sở của không gian null nên không mang thông tin về $A$;
vì vậy code thực tế luôn dùng bản reduced.

### 2.2 Các đại lượng đọc được từ sigma

| Đại lượng | Công thức | Ý nghĩa |
| --- | --- | --- |
| Hạng | $r = \#\{i: \sigma_i > 0\}$ (thực tế: $\sigma_i > \varepsilon$) | Số chiều thật của dữ liệu |
| Chuẩn Frobenius | $\lVert A\rVert_F = \sqrt{\sum_{ij} a_{ij}^2} = \sqrt{\sum_i \sigma_i^2}$ | "Năng lượng" toàn ma trận |
| Chuẩn phổ (spectral) | $\lVert A\rVert_2 = \sigma_1$ | Mức giãn lớn nhất |
| Chuẩn hạt nhân | $\lVert A\rVert_* = \sum_i \sigma_i$ | Dùng trong matrix completion |
| Số điều kiện | $\kappa(A) = \sigma_1/\sigma_r$ | Càng lớn càng "xấu", nghiệm càng nhạy nhiễu |
| Định thức (ma trận vuông) | $|\det A| = \prod_i \sigma_i$ | Thể tích bị biến đổi |
| Nghịch đảo (nếu khả nghịch) | $A^{-1} = V\Sigma^{-1}U^\top$ | Trường hợp riêng của giả nghịch đảo |

### 2.3 Liên hệ với trị riêng (rất hay bị hỏi)

$$
A^\top A = V\Sigma^2 V^\top, \qquad A A^\top = U\Sigma^2 U^\top
$$

Nói cách khác:

- **vector kỳ dị phải** $v_i$ = vector riêng của $A^\top A$ ứng với trị riêng $\sigma_i^2$;
- **vector kỳ dị trái** $u_i$ = vector riêng của $A A^\top$ ứng với trị riêng $\sigma_i^2$;
- và $u_i = \dfrac{A v_i}{\sigma_i}$ với $\sigma_i > 0$.

Điều này cho một *cách hiểu* SVD (và là cách tính tay ở mục 5), nhưng **không phải cách
tính số tốt**: lập $A^\top A$ làm số điều kiện bình phương ($\kappa(A^\top A)=\kappa(A)^2$),
sai số bị khuếch đại gấp đôi số chữ số. Thư viện thật dùng biến đổi Householder + Golub–Kahan
để đưa về dạng hai đường chéo rồi lặp QR — ổn định hơn nhiều.

### 2.4 SVD khác phân rã trị riêng ở đâu

| | $A = Q\Lambda Q^{-1}$ (eigen) | $A = U\Sigma V^\top$ (SVD) |
| --- | --- | --- |
| Điều kiện tồn tại | chỉ khi chéo hoá được | **luôn** |
| Ma trận biến đổi | $Q$ có thể không trực giao | $U, V$ **luôn** trực giao |
| Trị riêng | có thể âm/phức | $\sigma_i$ **luôn** thực, không âm |
| Ý nghĩa | hướng bất biến | hướng giãn mạnh nhất (không cần bất biến) |

Vì $\sigma_i \ge 0$ và có thứ tự, SVD cho phép **cắt bớt có kiểm soát** — điều mà phân rã
trị riêng không đảm bảo.

---

## 3. Trực giác hình học

Mọi ma trận là một **phép biến đổi tuyến tính**. SVD nói rằng phép biến đổi đó, dù méo mó
thế nào, cũng chỉ gồm **3 bước**:

```
        V^T                    Σ                     U
 vector  ──►  xoay/gương  ──►  co giãn theo trục  ──►  xoay/gương  ──►  kết quả
 (nguồn)      (về trục toạ độ)     (σ1, σ2, ...)        (về không gian đích)
```

Hệ quả hình học rất đẹp:

- Một **hình tròn đơn vị** trong không gian nguồn, qua $A$, biến thành **ellipse** có các
  bán trục đúng bằng $\sigma_1, \sigma_2, \dots$
- Các hướng bán trục đó là các cột của $U$.
- Vậy $\sigma_1$ = "A giãn mạnh nhất bao nhiêu lần", và hướng giãn mạnh nhất là $u_1$
  (ảnh của $v_1$).

Ví dụ 2×2: $A=\begin{bmatrix}1&2\\2&1\end{bmatrix}$ giãn theo hướng chéo $(1,1)$ gấp 3 lần
và theo hướng $(1,-1)$ đúng 1 lần (không giãn) — đúng bằng $\sigma = (3, 1)$ như mục 5.

> 💡 Cách nhớ: **SVD = "A chỉ là phép co giãn nếu ta chọn đúng hệ trục"**.

---

## 4. Ba cách "tìm ra" SVD

### 4.1 Cách đại số (để hiểu định lý)

1. Lập $A^\top A$ (đối xứng, nửa xác định dương).
2. Chéo hoá: $A^\top A = V\Lambda V^\top$, sắp $\lambda_1 \ge \dots \ge \lambda_n \ge 0$.
3. $\sigma_i = \sqrt{\lambda_i}$.
4. $u_i = A v_i / \sigma_i$ cho $\sigma_i > 0$; các $u_i$ ứng với $\sigma_i = 0$ bổ sung
   thành cơ sở trực chuẩn của phần bù.

Cách này chính là mục 2 của demo. Với $A=\begin{bmatrix}1&2\\2&1\end{bmatrix}$:

```
sigma dựng từ sqrt(eig(A^T A)): [3. 1.]
U dựng từ u_i = A v_i / sigma_i:  [[0.7071 0.7071]
                                   [0.7071 -0.7071]]
sai số dựng lại: 3.51e-16
```

### 4.2 Cách số (thư viện dùng)

- **Golub–Kahan**: Householder → dạng hai đường chéo → lặp QR. Độ phức tạp $O(mn\min(m,n))$
  cho ma trận dày đặc. Đây là `numpy.linalg.svd`, `LAPACK dgesdd`.
- **Lanczos / ARPACK** (`scipy.sparse.linalg.svds`): tốt khi cần **vài** $\sigma$ lớn nhất
  của ma trận **thưa**; độ phức tạp phụ thuộc số phần tử khác 0 và số lần lặp.
- **Randomized SVD** (Halko–Martinsson–Tropp): chiếu ngẫu nhiên xuống $k+p$ chiều rồi SVD
  nhỏ. Rất nhanh cho ma trận khổng lồ, sai số nhỏ với xác suất cao:

```python
def randomized_svd(A, k, p=10, q=2, rng=np.random.default_rng(0)):
    """Xấp xỉ k giá trị kỳ dị lớn nhất: nhanh hơn SVD đầy đủ khi A rất lớn."""
    m, n = A.shape
    omega = rng.standard_normal((n, k + p))
    Y = A @ omega
    for _ in range(q):                    # power iteration: làm cơ sở "bám" vào không gian chính
        Y = A @ (A.T @ Y)
    Q, _ = np.linalg.qr(Y)                # cơ sở trực chuẩn của không gian ảnh gần đúng
    B = Q.T @ A                           # ma trận nhỏ (k+p) x n
    Ub, s, vt = np.linalg.svd(B, full_matrices=False)
    return Q @ Ub[:, :k], s[:k], vt[:k]
```

- **Trực giao hoá lặp (power iteration)** cho vector kỳ dị lớn nhất — nền tảng của nhiều
  thuật toán recommender:

```python
def dominant_singular(A, iters=100):
    v = np.ones(A.shape[1]); v /= np.linalg.norm(v)
    for _ in range(iters):
        u = A @ v;       u /= np.linalg.norm(u)
        v = A.T @ u;     v /= np.linalg.norm(v)
    return u, float(u @ A @ v), v
```

---

## 5. Ví dụ tính tay đầy đủ (2×2)

Lấy $A=\begin{bmatrix}1 & 2\\ 2 & 1\end{bmatrix}$. Làm đúng từng bước như khi thi:

**Bước 1 — lập $A^\top A$**

$$
A^\top A=\begin{bmatrix}1&2\\2&1\end{bmatrix}\begin{bmatrix}1&2\\2&1\end{bmatrix}
=\begin{bmatrix}5&4\\4&5\end{bmatrix}
$$

**Bước 2 — trị riêng.** Với ma trận 2×2 đối xứng, dùng vết và định thức:

$$
\lambda_1+\lambda_2 = \operatorname{tr} = 10,\qquad
\lambda_1\lambda_2 = \det = 25-16 = 9
\;\Longrightarrow\; \lambda_1 = 9,\ \lambda_2 = 1
$$

**Bước 3 — giá trị kỳ dị.** $\sigma_1=\sqrt 9=3,\ \sigma_2=\sqrt 1=1$. Vậy
$\Sigma=\operatorname{diag}(3,1)$.

**Bước 4 — vector kỳ dị phải** (vector riêng của $A^\top A$):

- với $\lambda=9$: $(A^\top A-9I)v=0 \Rightarrow -4v_1+4v_2=0 \Rightarrow v_1=(1,1)/\sqrt2$.
- với $\lambda=1$: $\Rightarrow 4v_1+4v_2=0 \Rightarrow v_2=(1,-1)/\sqrt2$.

$$
V=\frac{1}{\sqrt2}\begin{bmatrix}1&1\\1&-1\end{bmatrix}
$$

**Bước 5 — vector kỳ dị trái** bằng $u_i = A v_i/\sigma_i$:

$$
u_1=\frac{1}{3}\cdot\frac{1}{\sqrt2}\begin{bmatrix}3\\3\end{bmatrix}
=\frac{1}{\sqrt2}\begin{bmatrix}1\\1\end{bmatrix},\qquad
u_2=\frac{1}{1}\cdot\frac{1}{\sqrt2}\begin{bmatrix}-1\\1\end{bmatrix}
=\frac{1}{\sqrt2}\begin{bmatrix}-1\\1\end{bmatrix}
$$

**Bước 6 — kiểm tra:**

$$
U\Sigma V^\top=
\frac{1}{\sqrt2}\begin{bmatrix}1&-1\\1&1\end{bmatrix}
\begin{bmatrix}3&0\\0&1\end{bmatrix}
\frac{1}{\sqrt2}\begin{bmatrix}1&1\\-1&1\end{bmatrix}
=\begin{bmatrix}1&2\\2&1\end{bmatrix}=A \quad ✅
$$

Chạy `python3 docs/svd_demo.py --only 1` cho đúng các con số này:

```
sigma: [3. 1.]
U Sigma V^T:
[[1. 2.]
 [2. 1.]]
sai số ||A - U Sigma V^T||_F: 1.71e-15
xấp xỉ hạng 1:
[[1.5 1.5]
 [1.5 1.5]]
sai số ||A - A_1||_F: 1.0     ← đúng bằng sigma_2
```

> ⚠️ **Dấu là tuỳ ý.** Nếu đổi dấu cả cột $u_i$ *và* cột $v_i$ thì $A$ không đổi. Vì vậy
> numpy có thể trả $u_2=(-1,1)/\sqrt2$ thay vì $(1,-1)/\sqrt2$ — cả hai đều đúng. Demo
> trong repo cố định dấu (phần tử lớn nhất của mỗi cột $U$ dương) để in ra giống bài tính tay,
> nhưng đừng bao giờ so sánh vector kỳ dị của hai lần chạy bằng dấu tuyệt đối.

---

## 6. Xấp xỉ hạng thấp — trái tim của ứng dụng

Cắt SVD ở $k$ thành phần đầu:

$$
A_k = \sum_{i=1}^{k}\sigma_i u_i v_i^\top
= U_k\Sigma_k V_k^\top
$$

### 6.1 Định lý Eckart–Young (1949)

$A_k$ là **xấp xỉ hạng $k$ tốt nhất** của $A$ theo chuẩn Frobenius (và cả chuẩn phổ):

$$
\lVert A-A_k\rVert_F=\sqrt{\sum_{i>k}\sigma_i^2},
\qquad
\lVert A-A_k\rVert_2=\sigma_{k+1}
$$

Hệ quả thực dụng:

- **Sai số tính được trước khi cắt** — chỉ cần xem $\sigma$.
- **Năng lượng giữ lại** $=\dfrac{\sum_{i\le k}\sigma_i^2}{\sum_i\sigma_i^2}$ (chính là tỉ lệ
  phương sai giải thích trong PCA).
- Không có cách nào chọn $k$ chiều khác tốt hơn — nên đây là chuẩn để đánh giá mọi thuật
  toán giảm chiều khác.

### 6.2 Ví dụ số (mục 3 của demo)

Ma trận $6\times4$ "gần hạng 2" cộng nhiễu nhỏ, $\sigma = (6.4669,\ 0.4550,\ 0.2189,\ 0.1637)$:

| $k$ | $\lVert A-A_k\rVert_F$ | sai số % | năng lượng giữ | số số phải lưu $k(m+n+1)$ |
| --- | --- | --- | --- | --- |
| 1 | 0.5308 | 8.18 % | 99.33 % | 11 (nén 2.18×) |
| 2 | 0.2734 | 4.21 % | 99.82 % | 22 (nén 1.09×) |
| 3 | 0.1637 | 2.52 % | 99.94 % | 33 (0.73× — phình ra) |
| 4 | 0.0000 | 0 % | 100 % | 44 (0.55×) |

Hai điều đáng chú ý:

1. Sai số in ra **khớp tuyệt đối** với $\sqrt{\sum_{i>k}\sigma_i^2}$ → kiểm chứng định lý.
2. **Giảm chiều không luôn = tiết kiệm chỗ.** Với ma trận $6\times4$, lưu $A_3$ tốn 33 số
   còn hơn lưu $A$ (24 số). SVD chỉ "nén" khi $\;k(m+n+1) < mn$, tức $k$ khá nhỏ so với
   $m,n$ — điều kiện dễ thoả với ma trận lớn (ảnh, ma trận từ–văn bản, ma trận đánh giá).

---

## 7. Chọn k như thế nào

Không có $k$ "đúng" duy nhất; chọn theo mục đích:

| Cách chọn | Khi nào dùng | Ghi chú |
| --- | --- | --- |
| **Đủ 90–95 % năng lượng** | giảm chiều tổng quát, nén | dễ giải thích trong báo cáo |
| **Elbow** (khuỷu tay trên đồ thị $\sigma_i$) | khi $\sigma$ tụt rõ | vẽ $\sigma_i$ theo $i$, tìm chỗ gãy |
| **Theo chất lượng đầu ra** (PSNR, accuracy, RMSE) | khi có bài toán cụ thể | trung thực nhất, cần chia train/valid |
| **Theo chi phí** $k(m+n+1) < mn$ | nén, lưu trữ | điều kiện số học thuần tuý |
| **Theo số nhóm ước lượng** | LSA, recommender | thường $k \approx$ số chủ đề/nhân tố ẩn |

Quy tắc thực hành: chọn $k$ nhỏ nhất mà chỉ số chất lượng còn nằm trong khoảng chấp nhận
được. $k$ quá lớn → giữ cả nhiễu, mất lợi ích nén/khử nhiễu; $k$ quá nhỏ → mất cấu trúc thật.

```python
def choose_k(s, target_energy=0.95):
    energy = np.cumsum(s**2) / np.sum(s**2)
    return int(np.searchsorted(energy, target_energy) + 1)
```

---

## 8. Ứng dụng: 5 bài toán đi kèm code

### 8.1 Nén ảnh

Ảnh xám = ma trận $m\times n$ (mỗi điểm ảnh một số). Lưu $U_k, \Sigma_k, V_k$ thay vì ảnh
gốc: cần $k(m+n+1)$ số thay cho $mn$.

Kết quả thật với ảnh 64×64 tổng hợp (mục 4 của demo, $mn=4096$):

| $k$ | số số phải lưu | tỉ lệ nén | PSNR (dB) | năng lượng giữ |
| --- | --- | --- | --- | --- |
| 1 | 129 | 31.75× | 21.48 | 98.28 % |
| 2 | 258 | 15.88× | 24.87 | 99.21 % |
| 5 | 645 | 6.35× | 29.44 | 99.72 % |
| 10 | 1290 | 3.18× | 32.77 | 99.87 % |
| 20 | 2580 | 1.59× | 36.66 | 99.95 % |
| 40 | 5160 | 0.79× | 44.65 | 99.99 % |

Đọc bảng: **năng lượng giữ 99 % mà mắt vẫn thấy xấu** (k=1, PSNR 21 dB) — vì năng lượng
Frobenius bị chi phối bởi các vùng phẳng, trong khi mắt nhạy với **cạnh**. Đây là lý do nén
ảnh thật (JPEG) dùng biến đổi khối + lượng tử hoá chứ không dùng SVD toàn ảnh.

```python
# img: ma trận 2 chiều, ví dụ ảnh xám 512 x 512 với giá trị 0..255
u, s, vt = np.linalg.svd(img, full_matrices=False)
k = 20
img_k = u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
compression_ratio = img.size / (k * (img.shape[0] + img.shape[1] + 1))
```

Chạy `python3 docs/svd_demo.py --only 4 --save` để ghi ảnh PGM ra `docs/svd_out/` và tự nhìn
khác biệt giữa $k=1,5,10,20$.

### 8.2 LSA / tìm kiếm ngữ nghĩa (mục 5 của demo)

Ma trận **từ × văn bản** (TF-IDF) rất thưa và nhiều chiều. SVD nén nó thành $k$ "chủ đề ẩn":

| Từ nặng nhất trong thành phần | $\sigma$ | Chủ đề lộ ra |
| --- | --- | --- |
| `cau_thu, bong_da, giai_dau, tran_dau` | 1.244 | bóng đá |
| `thi_truong, chung_khoan, co_phieu, dau_tu` | 1.224 | kinh tế |
| `du_lieu, mo_hinh, du_doan, nghien_cuu` | 1.180 | dữ liệu / học máy |

Không cần gán nhãn, SVD **tự tách 3 chủ đề** của 9 văn bản — đó là "latent semantic analysis".

Hiệu ứng rõ nhất: hai văn bản cùng chủ đề nhưng gần như **không chung từ nào**
(D1: `hoc_may …`, D2: `tri_tue_nhan_tao …`) có cosine gốc **0.21**, sau khi chiếu xuống
3 chiều thành **0.98**.

| cặp | cosine gốc | cosine $k=3$ |
| --- | --- | --- |
| D1–D2 | 0.21 | 0.98 |
| D1–D3 | 0.32 | 0.99 |
| D4–D5 | 0.25 | 0.98 |
| D1–D4 (khác chủ đề) | 0.14 | 0.23 |
| D4–D8 (khác chủ đề!) | 0.00 | **0.94** |

Dòng cuối là **mặt trái**: D4 (bóng đá) và D8 (kinh tế) bị kéo lại gần chỉ vì cùng chứa từ
chung `ket_qua`/`bao_cao` và $k=3$ không đủ chiều để tách. Giảm chiều vừa **khử nhiễu từ
vựng**, vừa **tạo tương đồng ảo** — luôn phải kiểm tra bằng mắt trên vài truy vấn.

Công thức "fold-in" một truy vấn mới (không cần tính lại SVD):

$$
\hat q = \Sigma_k^{-1}U_k^{\top}q
$$

trong đó $\hat q$ là toạ độ của câu hỏi trong không gian ẩn ($\Sigma_k^{-1}$ bù lại việc các
trục ẩn bị co giãn khác nhau). Sau đó chỉ cần so cosine của $\hat q$ với các cột của
$\Sigma_kV_k^{\top}$. Kết quả demo với truy vấn
`"mo_hinh du_lieu du_doan"`: D3 (1.00), D2 (1.00), D1 (0.99), các văn bản khác ≈ 0.

### 8.3 Gợi ý phim (recommender) (mục 6 của demo)

Ma trận đánh giá $R$ (người dùng × phim), ô trống = chưa xem. Mô hình:

$$
\hat R \approx \underbrace{\mu}_{\text{trung bình}} + U_k\Sigma_kV_k^{\top}
$$

Quy trình chuẩn (đơn giản hoá của "SVD++"/FunkSVD):

1. Trừ trung bình **theo người dùng** (mỗi người có thang điểm riêng: người chấm 3/5 là
   "thích", người khác chấm 3/5 là "bình thường").
2. Điền 0 vào ô trống **tạm thời** (tức "trung bình") — sai lệch này được xử lý bằng trọng số
   hoặc ALS trong hệ thống thật.
3. SVD, giữ $k$ chiều, dựng lại, cộng lại trung bình, cắt về $[1,5]$.
4. Ô trống có điểm dự đoán cao nhất = phim nên gợi ý.

Kết quả demo (6 người × 6 phim, $k=2$, RMSE 0.542 trên các ô đã biết):

| Người dùng | Gợi ý | Điểm dự đoán |
| --- | --- | --- |
| An | M6 | 3.63 |
| Binh | M4 | 3.67 |
| Chi | M6 | 4.07 |
| Dung | M5 | 2.44 |
| Giang | M5 | 3.02 |
| Hoa | M2 | 3.85 |

An và Binh có cùng sở thích (M1, M2 cao; M5 thấp) nên dự đoán gần như trùng nhau — đó chính là
"nhân tố ẩn" mà SVD phát hiện. Lưu ý: RMSE trên ô **đã biết** là đánh giá khả năng tái tạo,
không phải chất lượng gợi ý; muốn đánh giá thật phải **giữ lại (hold-out) một phần ô** rồi đo
trên phần đó.

### 8.4 PCA = SVD + trừ trung bình (mục 7 của demo)

Với dữ liệu $X$ ($n$ mẫu × $p$ đặc trưng):

1. Trừ trung bình từng cột: $X_c = X - \mathbf{1}\bar x^\top$ (bắt buộc!).
2. SVD: $X_c = U\Sigma V^\top$.
3. **Toạ độ mới** (scores) $= U\Sigma$, **hệ số** (loadings) $= V$.
4. Phương sai giải thích của thành phần $i$: $\sigma_i^2 / \sum_j \sigma_j^2$.

Demo với 200 điểm 2 chiều tương quan mạnh: $\sigma=(26.28, 8.99)$ → thành phần 1 giữ
**89.5 %** phương sai, thành phần 2 chỉ 10.5 %. Kiểm chứng chéo: trị riêng của `np.cov(X)`
là (3.4713, 0.4063), đúng bằng $\sigma_i^2/(n-1)$.

Nếu **quên** trừ trung bình, thành phần 1 giải thích 91.7 % nhưng thực chất nó chỉ đang mô tả
**vị trí trung bình của dữ liệu**, không phải hướng biến thiên. Đây là lỗi phổ biến nhất khi
tự code PCA.

> Phân biệt nhanh: `sklearn.decomposition.PCA` **trừ trung bình**;
> `sklearn.decomposition.TruncatedSVD` **không trừ** (dùng cho ma trận thưa như TF-IDF).
> Dùng sai loại là hỏng kết quả mà không báo lỗi.

### 8.5 Giả nghịch đảo và hồi quy (mục 8 của demo)

$$
A^{+} = V\Sigma^{+}U^{\top},\qquad \Sigma^{+}_{ii} =
\begin{cases}1/\sigma_i & \sigma_i > \varepsilon\\ 0 & \text{ngược lại}\end{cases}
$$

Nghiệm bình phương tối thiểu của $A\beta \approx y$ là $\hat\beta = A^{+}y$ — hoạt động cả
khi $A$ không vuông hoặc suy biến (khi đó nó cho nghiệm có chuẩn nhỏ nhất). Demo hồi quy
$y = 2 + 3x$ có nhiễu cho $\hat\beta = (1.832,\ 3.063)$, trùng khớp `np.linalg.lstsq`
đến từng chữ số.

Cắt bớt $\sigma$ nhỏ (đặt $1/\sigma_i = 0$) chính là **regularization**: chặn khuếch đại
nhiễu khi $A$ xấu điều kiện (liên hệ với ridge regression).

---

## 9. Code mẫu: numpy, scipy, sklearn

```python
import numpy as np

A = np.array([[1., 2.], [2., 1.]])
u, s, vt = np.linalg.svd(A, full_matrices=False)   # economy SVD
assert np.allclose(u @ np.diag(s) @ vt, A)
assert np.allclose(np.linalg.norm(A, "fro"), np.sqrt(np.sum(s**2)))
```

```python
# Ma trận lớn, thưa: chỉ lấy k giá trị kỳ dị lớn nhất (nhanh hơn nhiều)
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
X = csr_matrix(np.random.default_rng(0).random((5000, 3000)))
u, s, vt = svds(X, k=20)          # chú ý: svds trả s KHÔNG sắp xếp
order = np.argsort(s)[::-1]
u, s, vt = u[:, order], s[order], vt[order]
```

```python
# Giảm chiều văn bản (tf-idf thưa) — KHÔNG dùng PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
X = TfidfVectorizer().fit_transform(docs)
X_k = TruncatedSVD(n_components=100, random_state=0).fit_transform(X)

# Giảm chiều dữ liệu bảng thường (dày đặc) — dùng PCA (tự trừ trung bình)
from sklearn.decomposition import PCA
Z = PCA(n_components=2, random_state=0).fit_transform(features)
```

```python
# Kiểm tra nhanh mọi tính chất của một SVD vừa tính
def check_svd(A, u, s, vt, tol=1e-9):
    assert np.allclose(u.T @ u, np.eye(u.shape[1]), atol=tol), "U không trực giao"
    assert np.allclose(vt @ vt.T, np.eye(vt.shape[0]), atol=tol), "V không trực giao"
    assert np.allclose(u @ np.diag(s) @ vt, A, atol=tol), "dựng lại sai"
    assert np.all(np.diff(s) <= tol), "sigma phải giảm dần"
    rank = int(np.sum(s > tol * s[0]))
    return rank
```

---

## 10. Bẫy và lỗi thường gặp

| Bẫy | Hậu quả | Cách xử lý |
| --- | --- | --- |
| **Dấu vector kỳ dị tuỳ ý** | hai lần chạy ra "khác nhau" dù cùng dữ liệu | so sánh $u v^\top$ hoặc trị tuyệt đối; cố định dấu nếu cần hiển thị |
| **Trị riêng trùng nhau** | vector kỳ dị không xác định duy nhất (bất kỳ cơ sở nào của không gian đó cũng đúng) | đừng diễn giải từng vector riêng lẻ trong trường hợp này |
| **Quên trừ trung bình khi làm PCA** | "thành phần 1" chỉ là vị trí dữ liệu | luôn centering trước PCA |
| **Trừ trung bình khi làm LSA/TF-IDF** | phá tính thưa, kết quả vô nghĩa | dùng `TruncatedSVD`, không center |
| **Lập $A^\top A$ để tính SVD** | mất một nửa số chữ số chính xác | dùng `np.linalg.svd`, đừng tự lập $A^\top A$ |
| **Ô trống trong recommender** | SVD coi 0 = "điểm trung bình" → lệch | trừ trung bình, dùng ALS/SGD có trọng số, hoặc matrix completion |
| **Đánh giá trên dữ liệu đã dùng để fit** | RMSE đẹp giả tạo | chia train/test, đánh giá trên hold-out |
| **Chọn $k$ = hạng đầy đủ** | không nén, giữ cả nhiễu | xem mục 7 |
| **Diễn giải "thành phần" như nguyên nhân** | ngụy biện | SVD chỉ tìm hướng biến thiên, không phải quan hệ nhân quả |
| **Dữ liệu lệch thang đo** | đặc trưng có đơn vị lớn át hết | chuẩn hoá (z-score) trước SVD/PCA nếu đơn vị khác nhau |
| **So sánh tốc độ trên dữ liệu nhỏ** | kết luận sai | nêu rõ trong báo cáo; ma trận nhỏ thì SVD đầy đủ đã đủ nhanh |

---

## 11. Bài tập tự kiểm tra

**Bài 1.** Cho $A=\begin{bmatrix}0&2\\0&0\end{bmatrix}$. Tìm SVD và hạng của $A$.

<details><summary>Đáp án</summary>

$A^\top A=\begin{bmatrix}0&0\\0&4\end{bmatrix}$ → $\lambda=(4,0)$, $\sigma=(2,0)$,
$v_1=(0,1)$, $u_1=Av_1/2=(1,0)$. Vậy
$A=2\begin{bmatrix}1\\0\end{bmatrix}\begin{bmatrix}0&1\end{bmatrix}$. Hạng 1 (một $\sigma>0$).
</details>

**Bài 2.** $A$ là ma trận $100\times 100$ với $\sigma_1=10$ và $\sigma_{100}=0.001$.
Số điều kiện bằng bao nhiêu? Điều gì xảy ra nếu giải $Ax=b$ bằng máy tính 16 chữ số?

<details><summary>Đáp án</summary>

$\kappa = 10/0.001 = 10^4$. Ta mất khoảng $\log_{10}\kappa = 4$ chữ số chính xác, còn ~12
chữ số — vẫn ổn. Nếu $\kappa \approx 10^{16}$ thì nghiệm vô nghĩa.
</details>

**Bài 3.** Với ma trận $200\times 50$, cần $k$ bao nhiêu để SVD thực sự **tiết kiệm bộ nhớ**?

<details><summary>Đáp án</summary>

Cần $k(200+50+1) < 200\cdot 50 = 10000 \Rightarrow k < 39.8$, tức $k \le 39$.
</details>

**Bài 4.** Ma trận đánh giá 5 người × 100 phim, mỗi người mới xem ~10 phim. Có nên dùng SVD
trực tiếp trên ma trận đã điền 0?

<details><summary>Đáp án</summary>

Không nên. 90 % ô là "0 giả" sẽ chi phối kết quả (SVD học "0" chứ không học sở thích). Cần
trừ trung bình + trọng số (weighted ALS), hoặc dùng matrix completion chỉ tính trên ô quan sát
được.
</details>

**Bài 5.** Chứng minh $\lVert A\rVert_F^2=\sum_i\sigma_i^2$ từ $A=U\Sigma V^\top$.

<details><summary>Đáp án</summary>

$\lVert A\rVert_F^2=\operatorname{tr}(A^\top A)=\operatorname{tr}(V\Sigma U^\top U\Sigma V^\top)
=\operatorname{tr}(V\Sigma^2V^\top)=\operatorname{tr}(\Sigma^2V^\top V)=\operatorname{tr}(\Sigma^2)=\sum\sigma_i^2$.
Dùng $\operatorname{tr}(XY)=\operatorname{tr}(YX)$ và $U^\top U=I, V^\top V=I$.
</details>

**Bài 6.** Vì sao "SVD của ảnh giữ 99 % năng lượng" không có nghĩa "ảnh nhìn vẫn đẹp"?

<details><summary>Đáp án</summary>

Năng lượng Frobenius đo tổng bình phương sai khác, bị chi phối bởi các vùng phẳng/diện tích
lớn. Mắt lại nhạy với cạnh và chi tiết — chính là các thành phần có $\sigma$ nhỏ. Xem bảng
ở mục 8.1: $k=1$ giữ 98.28 % năng lượng nhưng PSNR chỉ 21.48 dB.
</details>

---

## 12. Liên hệ với nội dung môn học

Trong môn **Introduction to Data Science (PTIT)**, SVD xuất hiện ở các nhóm chủ đề:

| Chủ đề | Liên hệ SVD |
| --- | --- |
| Tiền xử lý & giảm chiều | PCA = SVD của dữ liệu đã centering; chọn số thành phần theo năng lượng |
| Hệ gợi ý | ma trận người dùng × sản phẩm, nhân tố ẩn, RMSE, cold start |
| Xử lý văn bản | TF-IDF → LSA, tìm kiếm ngữ nghĩa, tóm tắt |
| Khai phá dữ liệu ảnh/đa phương tiện | nén, khử nhiễu, trích đặc trưng (eigenfaces) |
| Đại số tuyến tính | chuẩn, hạng, điều kiện, giả nghịch đảo, least squares |

Ba câu nên trả lời được khi thi vấn đáp:

1. Phát biểu SVD và giải thích ý nghĩa hình học của $U,\Sigma,V$.
2. Vì sao $A_k$ là xấp xỉ hạng $k$ tốt nhất, và sai số bằng bao nhiêu?
3. Trình bày một ứng dụng (nén ảnh / LSA / recommender) và nêu **một** hạn chế của nó.

---

## Phụ lục: chạy lại toàn bộ tài liệu

```bash
python3 -m pip install numpy
python3 docs/svd_demo.py                 # 8 mục, ~250 dòng output
python3 docs/svd_demo.py --only 5        # chỉ xem LSA
python3 docs/svd_demo.py --only 4 --save # nén ảnh + ghi PGM để xem bằng mắt
```

Mọi con số trong tài liệu lấy từ lần chạy trên với numpy 2.x; nếu numpy đổi thuật toán, các
giá trị có thể lệch ở chữ số thứ 12 trở đi (dấu của vector kỳ dị có thể đổi — xem mục 10).
