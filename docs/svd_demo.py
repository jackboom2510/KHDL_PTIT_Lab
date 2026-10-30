#!/usr/bin/env python3
"""Demo phân rã SVD — đi kèm `docs/svd_guide.md`.

Mỗi mục in ra đúng những con số được trích trong tài liệu, nên chạy lại file này là
cách kiểm tra tài liệu còn khớp với code hay không.

    python3 -m pip install numpy          # chỉ cần numpy
    python3 docs/svd_demo.py              # in toàn bộ demo
    python3 docs/svd_demo.py --save       # thêm ảnh minh hoạ nén ảnh (docs/svd_out/*.pgm)
    python3 docs/svd_demo.py --only 4     # chỉ chạy mục 4

Không dùng dữ liệu ngoài, không cần mạng: mọi ma trận đều dựng bằng tay hoặc bằng
`numpy.random.default_rng(seed)` để tái lập được kết quả.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - hướng dẫn cho người mới
    raise SystemExit(
        "Cần numpy để chạy demo SVD:\n"
        "    python3 -m pip install numpy\n"
        "(các lab SQL/MongoDB trong repo không cần numpy, chỉ file demo này cần)"
    )

np.set_printoptions(precision=4, suppress=True, linewidth=110)


# --------------------------------------------------------------------------------------
# Tiện ích in
# --------------------------------------------------------------------------------------
def title(text: str) -> None:
    print()
    print("=" * 78)
    print(text)
    print("=" * 78)


def show(name: str, value: np.ndarray | float) -> None:
    if isinstance(value, np.ndarray):
        print(f"{name} (shape={value.shape}):")
        print(value)
    else:
        print(f"{name}: {value}")


def fro(a: np.ndarray) -> float:
    return float(np.linalg.norm(a, "fro"))


def svd_canonical(a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """SVD + cố định dấu: phần tử lớn nhất (theo trị tuyệt đối) của mỗi cột U dương.

    Dấu của cặp (u_i, v_i) là tuỳ ý về mặt toán học; cố định lại chỉ để in ra
    giống phần tính tay trong tài liệu.
    """
    u, s, vt = np.linalg.svd(a, full_matrices=False)
    for i in range(s.size):
        if u[np.argmax(np.abs(u[:, i])), i] < 0:
            u[:, i] *= -1
            vt[i, :] *= -1
    return u, s, vt


def cosine_cols(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Ma trận cosine giữa các cột của a và các cột của b (đã chuẩn hoá cột)."""
    na = np.linalg.norm(a, axis=0, keepdims=True)
    nb = np.linalg.norm(b, axis=0, keepdims=True)
    a = a / np.where(na == 0, 1, na)
    b = b / np.where(nb == 0, 1, nb)
    return a.T @ b


# --------------------------------------------------------------------------------------
# 1. Ví dụ tính tay 2x2
# --------------------------------------------------------------------------------------
def part1_hand_example() -> None:
    title("1. Ví dụ tính tay: A = [[1, 2], [2, 1]]")
    a = np.array([[1.0, 2.0], [2.0, 1.0]])

    # Bước 1: A^T A
    ata = a.T @ a
    show("A^T A", ata)

    # Bước 2: trị riêng của A^T A bằng tay (trace = 10, det = 9)
    lam = np.linalg.eigvalsh(ata)[::-1]  # giảm dần
    show("trị riêng của A^T A (lambda)", lam)
    show("giá trị kỳ dị sigma = sqrt(lambda)", np.sqrt(lam))

    # Bước 3: SVD của numpy (cố định dấu để khớp phần tính tay)
    u, s, vt = svd_canonical(a)
    show("U", u)
    show("sigma", s)
    show("V^T", vt)

    # Bước 4: kiểm tra dựng lại
    a_rec = u @ np.diag(s) @ vt
    show("U Sigma V^T", a_rec)
    show("sai số ||A - U Sigma V^T||_F", fro(a - a_rec))
    show("||A||_F", fro(a))

    # Bước 5: hạng 1 tốt nhất (Eckart-Young)
    k = 1
    a1 = u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
    show("xấp xỉ hạng 1", a1)
    show("sai số ||A - A_1||_F", fro(a - a1))
    show("sigma_2 (đúng bằng sai số trên)", s[1])


# --------------------------------------------------------------------------------------
# 2. Tự tìm SVD từ A^T A (để thấy định lý, không dùng cho số thực)
# --------------------------------------------------------------------------------------
def part2_from_eigen() -> None:
    title("2. Tự dựng SVD từ trị riêng của A^T A (minh hoạ lý thuyết)")
    a = np.array([[1.0, 2.0], [2.0, 1.0]])
    ata = a.T @ a
    lam, v = np.linalg.eigh(ata)
    order = np.argsort(lam)[::-1]
    lam, v = lam[order], v[:, order]
    s = np.sqrt(np.clip(lam, 0.0, None))

    # u_i = A v_i / sigma_i (chỉ tính cho sigma > 0)
    u_cols = []
    for i, sigma in enumerate(s):
        if sigma > 1e-12:
            u_cols.append((a @ v[:, i]) / sigma)
    u = np.column_stack(u_cols)

    show("sigma dựng từ sqrt(eig(A^T A))", s)
    show("U dựng từ u_i = A v_i / sigma_i", u)
    show("kiểm tra A @ V = U @ Sigma", a @ v)
    show("                           ", u @ np.diag(s))
    show("sai số dựng lại", fro(a - u @ np.diag(s) @ v.T))
    print("Ghi chú: cách này sai số lớn khi A xấu (điều kiện bình phương),")
    print("         thư viện thật dùng Golub-Kahan chứ không lập A^T A.")


# --------------------------------------------------------------------------------------
# 3. Xấp xỉ hạng thấp + bảng sai số / năng lượng
# --------------------------------------------------------------------------------------
def part3_low_rank() -> None:
    title("3. Xấp xỉ hạng thấp: sai số và năng lượng giữ lại")
    rng = np.random.default_rng(7)
    # ma trận 6x4 "gần hạng 2" + nhiễu nhỏ (vì nhiễu nên hạng đầy đủ = 4)
    base = np.array(
        [
            [3.0, 1.0, 2.0, 1.0],
            [2.0, 1.0, 1.5, 1.0],
            [1.0, 0.5, 1.0, 0.5],
            [2.5, 1.2, 1.8, 1.0],
            [0.5, 0.2, 0.4, 0.2],
            [1.5, 0.8, 1.2, 0.6],
        ]
    )
    a = base + 0.05 * rng.standard_normal(base.shape)
    u, s, vt = np.linalg.svd(a, full_matrices=False)

    show("A (6x4)", a)
    show("sigma", s)
    show("hạng đầy đủ (nhiễu làm sigma khác 0)", int(np.sum(s > 1e-12)))
    show("hạng số (sigma > 5% sigma_1)", int(np.sum(s > 0.05 * s[0])))
    show("điều kiện sigma_1 / sigma_r", float(s[0] / s[-1]))

    print(f"\n{'k':>3} {'||A-A_k||_F':>12} {'sai số %':>10} {'năng lượng %':>13}")
    total = float(np.sum(s**2))
    for k in range(1, len(s) + 1):
        ak = u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
        err = fro(a - ak)
        energy = 100 * float(np.sum(s[:k] ** 2)) / total
        print(f"{k:>3} {err:>12.4f} {100 * err / fro(a):>9.2f}% {energy:>12.2f}%")

    print("\nSai số lý thuyết sqrt(tổng sigma_i^2, i>k):")
    for k in range(1, len(s) + 1):
        print(f"  k={k}: {float(np.sqrt(np.sum(s[k:] ** 2))):.4f}")

    print("\nDung lượng lưu trữ (ma trận 6x4 = 24 số):")
    for k in range(1, len(s) + 1):
        print(
            f"  k={k}: k*(m+n+1) = {k * (a.shape[0] + a.shape[1] + 1):>3} số"
            f"  -> tỉ lệ {24 / (k * (a.shape[0] + a.shape[1] + 1)):.2f}x"
        )


# --------------------------------------------------------------------------------------
# 4. Nén ảnh
# --------------------------------------------------------------------------------------
def make_test_image(n: int = 64, seed: int = 11) -> np.ndarray:
    """Ảnh xám tổng hợp n x n (0..255): gradient + cạnh + hình tròn + vân mịn + nhiễu."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n] / (n - 1)
    img = 60 + 90 * x + 40 * y                       # gradient -> vài thành phần đầu
    img += 50 * (y < 0.5)                            # cạnh ngang sắc
    circle = (x - 0.55) ** 2 + (y - 0.45) ** 2 < 0.05
    img[circle] = 230                                # hình tròn
    img[:, 8:12] = 25                                # vạch dọc đậm
    img += 18 * np.sin(22 * x + 3 * y) * np.cos(17 * y)   # vân mịn
    img += rng.normal(0, 6, size=(n, n))             # nhiễu -> ma trận hạng đầy đủ
    return np.clip(np.round(img), 0, 255)


def write_pgm(path: Path, img: np.ndarray) -> None:
    h, w = img.shape
    data = np.clip(np.round(img), 0, 255).astype(np.uint8)
    with path.open("wb") as f:
        f.write(f"P5\n{w} {h}\n255\n".encode())
        f.write(data.tobytes())


def psnr(original: np.ndarray, approx: np.ndarray) -> float:
    """PSNR trên ảnh 8 bit đã làm tròn (thực tế lưu ảnh là số nguyên)."""
    a = np.clip(np.round(original), 0, 255)
    b = np.clip(np.round(approx), 0, 255)
    mse = float(np.mean((a - b) ** 2))
    return float("inf") if mse == 0 else 10 * np.log10(255**2 / mse)


def part4_image(save: bool) -> None:
    title("4. Nén ảnh bằng SVD (ảnh xám 64x64 tổng hợp)")
    a = make_test_image(64)
    m, n = a.shape
    u, s, vt = np.linalg.svd(a, full_matrices=False)
    show("kích thước ảnh", f"{m}x{n} = {m * n} byte (8 bit/điểm ảnh)")
    show("8 sigma đầu", s[:8])
    show("sigma cuối", s[-8:])

    print(f"\n{'k':>3} {'số số phải lưu':>15} {'tỉ lệ nén':>10} {'PSNR (dB)':>10} {'giữ năng lượng':>15}")
    for k in (1, 2, 5, 10, 20, 40):
        ak = u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
        stored = k * (m + n + 1)
        energy = 100 * float(np.sum(s[:k] ** 2)) / float(np.sum(s**2))
        print(
            f"{k:>3} {stored:>15} {m * n / stored:>9.2f}x "
            f"{psnr(a, ak):>10.2f} {energy:>14.2f}%"
        )
    print("\nPSNR: <20 dB ảnh rất xấu, 30 dB coi là tốt, >40 dB gần như không phân biệt được.")

    if save:
        out = Path(__file__).parent / "svd_out"
        out.mkdir(exist_ok=True)
        write_pgm(out / "goc.pgm", a)
        for k in (1, 5, 10, 20):
            ak = u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
            write_pgm(out / f"k{k}.pgm", ak)
        print(f"\nĐã ghi ảnh P5 vào {out} (mở bằng GIMP/IrfanView/xnview).")
    else:
        print("\n(chạy với --save để ghi ảnh PGM ra docs/svd_out/)")


# --------------------------------------------------------------------------------------
# 5. LSA: tìm kiếm ngữ nghĩa trên ma trận từ - văn bản
# --------------------------------------------------------------------------------------
LSA_DOCS = [
    "hoc_may du_lieu mo_hinh thuat_toan du_doan nghien_cuu ket_qua",
    "tri_tue_nhan_tao mang_noron hoc_sau du_lieu huan_luyen nghien_cuu",
    "thong_ke hoi_quy du_lieu mo_hinh du_doan sai_so phuong_phap",
    "bong_da tran_dau cau_thu ban_thang giai_dau ket_qua",
    "the_thao clb chuyen_nhuong cau_thu tran_dau bao_cao",
    "hlv chien_thuat bong_da cau_thu giai_dau chuc_vo_dich",
    "kinh_te chung_khoan dau_tu thi_truong co_phieu so_lieu",
    "lam_phat lai_suat ngan_hang chinh_sach tien_te bao_cao",
    "dau_tu co_phieu thi_truong chung_khoan rui_ro loi_nhuan phan_tich",
]
LSA_LABELS = [f"D{i + 1}" for i in range(len(LSA_DOCS))]
LSA_TOPIC = ["dữ liệu/học máy", "bóng đá/thể thao", "kinh tế/tài chính"]


def build_term_doc(docs: list[str]) -> tuple[np.ndarray, list[str]]:
    """Ma trận từ-văn bản TF-IDF, chuẩn hoá L2 theo cột (như scikit-learn)."""
    tokens = [doc.split() for doc in docs]
    vocab = sorted({t for toks in tokens for t in toks})
    index = {t: i for i, t in enumerate(vocab)}
    tf = np.zeros((len(vocab), len(docs)))
    for j, toks in enumerate(tokens):
        for t in toks:
            tf[index[t], j] += 1
    df = np.sum(tf > 0, axis=1, keepdims=True)
    idf = np.log(len(docs) / df) + 1          # làm mượt, tránh chia 0
    m = tf * idf
    norms = np.linalg.norm(m, axis=0, keepdims=True)
    return m / np.where(norms == 0, 1, norms), vocab


def print_sim(mat: np.ndarray, name: str) -> None:
    print(f"\n{name}")
    print("       " + " ".join(f"{lab:>5}" for lab in LSA_LABELS))
    for i, lab in enumerate(LSA_LABELS):
        row = " ".join(f"{val:>5.2f}" for val in mat[i])
        print(f"{lab:>5}  {row}")


def part5_lsa() -> None:
    title("5. LSA: SVD trên ma trận từ - văn bản (TF-IDF)")
    m, vocab = build_term_doc(LSA_DOCS)
    show("số từ vựng x số văn bản", f"{m.shape[0]} x {m.shape[1]}")
    show("hạng của ma trận", int(np.linalg.matrix_rank(m)))

    u, s, vt = np.linalg.svd(m, full_matrices=False)
    show("sigma", s)
    print("\nChủ đề thật của 9 văn bản: D1-D3 =", LSA_TOPIC[0],
          "| D4-D6 =", LSA_TOPIC[1], "| D7-D9 =", LSA_TOPIC[2])

    k = 3
    print(f"\nCác từ 'nặng' nhất trong {k} thành phần ẩn (theo |U|):")
    for i in range(k):
        top = np.argsort(np.abs(u[:, i]))[::-1][:4]
        print(f"  thành phần {i + 1} (sigma={s[i]:.3f}): " + ", ".join(vocab[t] for t in top))

    sim_full = cosine_cols(m, m)
    doc_k = np.diag(s[:k]) @ vt[:k, :]
    sim_k = cosine_cols(doc_k, doc_k)

    print_sim(sim_full, f"Cosine - không gian gốc ({m.shape[0]} chiều, mỗi văn bản chỉ có ~7 từ):")
    print_sim(sim_k, f"Cosine - không gian ẩn (k={k}):")
    print("\nĐọc bảng: các văn bản cùng chủ đề nhưng gần như không chung từ (D1-D2 = "
          f"{sim_full[0, 1]:.2f})")
    print(f"được kéo lại gần nhau trong không gian ẩn (D1-D2 = {sim_k[0, 1]:.2f}).")
    print("D4 và D8 lại 'dính' nhau vì cùng dùng từ chung 'ket_qua/bao_cao' "
          f"({sim_k[3, 7]:.2f}) — mặt trái của việc giảm chiều.")

    pairs = [(0, 1), (0, 2), (0, 3), (3, 4), (3, 7), (6, 8)]
    print(f"\n{'cặp':>8} {'gốc':>8} {'k=3':>8}")
    for i, j in pairs:
        print(f"{LSA_LABELS[i] + '-' + LSA_LABELS[j]:>8} {sim_full[i, j]:>8.2f} {sim_k[i, j]:>8.2f}")

    # --- Truy vấn: chiếu câu hỏi xuống không gian ẩn rồi so cosine
    query = "mo_hinh du_lieu du_doan"
    q = np.zeros((len(vocab), 1))
    for t in query.split():
        if t in vocab:
            q[vocab.index(t), 0] += 1
    q /= np.linalg.norm(q)
    score_full = cosine_cols(m, q).ravel()
    # q_hat = Sigma_k^{-1} U_k^T q  (folding-in)
    q_k = np.linalg.pinv(np.diag(s[:k])) @ u[:, :k].T @ q
    score_k = cosine_cols(doc_k, q_k).ravel()

    print(f"\nTruy vấn: '{query}'")
    print(f"{'văn bản':>8} {'điểm gốc':>10} {'điểm k=3':>10}")
    for i in np.argsort(score_k)[::-1]:
        print(f"{LSA_LABELS[i]:>8} {score_full[i]:>10.3f} {score_k[i]:>10.3f}")


# --------------------------------------------------------------------------------------
# 6. Gợi ý phim (recommender) bằng SVD
# --------------------------------------------------------------------------------------
RATINGS = np.array(
    [
        [5, 4, 0, 0, 1, 0],
        [4, 5, 0, 0, 1, 0],
        [5, 4, 1, 0, 0, 0],
        [0, 1, 4, 5, 0, 1],
        [1, 0, 5, 4, 0, 2],
        [0, 0, 4, 5, 1, 4],
    ],
    dtype=float,
)
USERS = ["An", "Binh", "Chi", "Dung", "Giang", "Hoa"]
MOVIES = ["M1", "M2", "M3", "M4", "M5", "M6"]


def part6_recommender() -> None:
    title("6. Gợi ý phim: SVD trên ma trận đánh giá đã trừ trung bình người dùng")
    r = RATINGS
    mask = r > 0
    n_users, n_items = r.shape

    mean_u = np.array([r[i, mask[i]].mean() if mask[i].any() else 0 for i in range(n_users)])
    centered = np.where(mask, r - mean_u[:, None], 0.0)  # ô trống tạm coi là 0 = "trung bình"

    show("ma trận đánh giá (0 = chưa xem)", r)
    show("trung bình từng người dùng", mean_u)

    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    show("sigma", s)
    k = 2
    pred = mean_u[:, None] + u[:, :k] @ np.diag(s[:k]) @ vt[:k, :]
    pred = np.clip(pred, 1, 5)
    show(f"Dự đoán (k={k})", pred)

    print("\nPhim chưa xem, dự đoán cao nhất cho mỗi người:")
    for i in range(n_users):
        unseen = np.where(~mask[i])[0]
        best = unseen[np.argmax(pred[i, unseen])]
        print(f"  {USERS[i]:>5}: {MOVIES[best]} ~ {pred[i, best]:.2f}")

    # RMSE trên chính các ô đã biết (đánh giá khả năng tái tạo, không phải kiểm định thật)
    known = pred[mask]
    true = r[mask]
    print(f"\nRMSE trên {mask.sum()} ô đã biết (fit, không phải hold-out): "
          f"{float(np.sqrt(np.mean((known - true) ** 2))):.3f}")
    print("Lưu ý: k càng lớn RMSE càng giảm nhưng càng dễ học thuộc -> cần chia train/test.")
    print("Các ô trống bị coi là 0 nên SVD 'hiểu' là trung bình; thực tế dùng ALS/SGD có trọng số.")


# --------------------------------------------------------------------------------------
# 7. PCA = SVD sau khi chuẩn hoá
# --------------------------------------------------------------------------------------
def part7_pca() -> None:
    title("7. PCA chính là SVD của dữ liệu đã trừ trung bình")
    rng = np.random.default_rng(0)
    n = 200
    cov = np.array([[2.0, 1.6], [1.6, 2.0]])
    x = rng.multivariate_normal([5.0, -3.0], cov, size=n)

    show("trung bình từng cột", x.mean(axis=0))
    xc = x - x.mean(axis=0)

    u, s, vt = np.linalg.svd(xc, full_matrices=False)
    explained = s**2 / np.sum(s**2)
    show("sigma", s)
    show("phương sai giải thích / thành phần", explained)
    show("vector riêng của ma trận hiệp phương sai", vt.T)

    # đối chiếu với numpy.cov
    lam, _ = np.linalg.eigh(np.cov(x, rowvar=False))
    order = np.argsort(lam)[::-1]
    show("trị riêng của cov(x)", lam[order])
    show("trị riêng/(n-1) so với sigma^2/(n-1)", s**2 / (n - 1))

    # dữ liệu chiếu xuống 1 chiều
    scores = xc @ vt.T
    print(f"\nNếu chỉ giữ 1 thành phần: giữ {explained[0] * 100:.1f}% phương sai,")
    print(f"mất {100 - explained[0] * 100:.1f}%.")
    print("Chiếu 3 điểm đầu:", np.round(scores[:3, :1].ravel(), 2))

    # nếu quên centering
    _, s2, _ = np.linalg.svd(x, full_matrices=False)
    print(f"\nNếu KHÔNG centering: thành phần 1 giải thích "
          f"{100 * s2[0] ** 2 / np.sum(s2 ** 2):.1f}% -> chỉ đo 'vị trí trung bình', sai.")


# --------------------------------------------------------------------------------------
# 8. Bình phương tối thiểu / giả nghịch đảo
# --------------------------------------------------------------------------------------
def part8_least_squares() -> None:
    title("8. Giả nghịch đảo A+ = V Sigma+ U^T dùng cho hồi quy bình phương tối thiểu")
    # y = 2 + 3x, có nhiễu
    rng = np.random.default_rng(3)
    x = np.linspace(0, 4, 12)
    y = 2 + 3 * x + rng.normal(0, 0.4, size=x.size)
    a = np.column_stack([np.ones_like(x), x])  # cột 1 = hệ số tự do

    u, s, vt = np.linalg.svd(a, full_matrices=False)
    s_inv = np.array([1 / si if si > 1e-12 else 0 for si in s])
    a_pinv = vt.T @ np.diag(s_inv) @ u.T
    beta = a_pinv @ y
    show("sigma", s)
    show("hệ số [chặn, dốc] theo A+", beta)
    show("hệ số theo numpy.linalg.lstsq", np.linalg.lstsq(a, y, rcond=None)[0])
    print(f"mô hình: y = {beta[0]:.3f} + {beta[1]:.3f} x  (đúng: 2 và 3)")


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
PARTS = {
    1: ("ví dụ tính tay 2x2", lambda: part1_hand_example()),
    2: ("dựng SVD từ A^T A", lambda: part2_from_eigen()),
    3: ("xấp xỉ hạng thấp", lambda: part3_low_rank()),
    4: ("nén ảnh", None),  # cần cờ --save
    5: ("LSA", lambda: part5_lsa()),
    6: ("gợi ý phim", lambda: part6_recommender()),
    7: ("PCA", lambda: part7_pca()),
    8: ("giả nghịch đảo", lambda: part8_least_squares()),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo SVD kèm tài liệu docs/svd_guide.md")
    parser.add_argument("--save", action="store_true", help="ghi ảnh PGM minh hoạ nén ảnh")
    parser.add_argument(
        "--only",
        type=int,
        choices=sorted(PARTS),
        help="chỉ chạy một mục (1..8)",
    )
    args = parser.parse_args()

    for idx, (_, fn) in PARTS.items():
        if args.only is not None and idx != args.only:
            continue
        if idx == 4:
            part4_image(args.save)
        else:
            assert fn is not None
            fn()

    title("Xong")
    print("Tài liệu lý thuyết: docs/svd_guide.md")


if __name__ == "__main__":
    main()
