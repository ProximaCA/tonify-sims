# data/ — sim4: синтетическая двудольная матрица user×artist

Артефакты `sim4/bipartite_gen.py` (seed=42, N=20 000 артистов, ~1.1M юзеров,
~21.8M ненулевых пар). Формат: `scipy.sparse` CSR, shape `(U, N)`,
`M[u, i]` = прослушивания юзера `u` артиста `i` за период.

| Файл | Режим (SPEC §3) |
|---|---|
| `matrix_a_seed42.npz` | (a) эргодический контроль: `P_u ≡ 2048`, целые |
| `matrix_b_seed42.npz` | (b) гетерогенный: LN-полотно, рескейл к мишеням `s_i` (суммо-точный) |
| `matrix_c_gm03_seed42.npz` | (c) сопряжение γ = −0.3 |
| `matrix_c_gp03_seed42.npz` | (c) сопряжение γ = +0.3 |
| `matrix_sample.csv` | первые 10 000 троек `(user_id, artist_id, plays)` режима (b) |

`.npz` не в гите (~сотни МБ) — генерируются `python3 sim4/bipartite_gen.py`
(~6 мин) или всем прогоном `python3 run_all.py`.

## Загрузка

```python
from scipy import sparse

def load_matrix(mode="b", path="data"):
    """CSR user×artist; mode ∈ {'a','b','c_gm03','c_gp03'}."""
    return sparse.load_npz(f"{path}/matrix_{mode}_seed42.npz")
```

## Пример (10 строк)

```python
import numpy as np
M = load_matrix("b")                                    # (U, N) CSR, int32
P_u = np.asarray(M.sum(axis=1), dtype=np.float64).ravel()  # интенсивность юзеров
P_i = np.asarray(M.sum(axis=0), dtype=np.float64).ravel()  # стримы артистов
T, U = P_u.sum(), (P_u > 0).sum()
PR = U * P_i / T                              # pro-rata (кошелёк W=1)
inv = np.divide(1.0, P_u, out=np.zeros_like(P_u), where=P_u > 0)
UC = np.asarray(M.multiply(inv[:, None]).sum(axis=0)).ravel()  # user-centric
top = np.argsort(P_i)[::-1][:5]
print("топ-5 артистов, UC/PR:", np.round(UC[top] / PR[top], 3))
```
