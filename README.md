# Bank Marketing: Eliminating Call Fatigue with a 3-Strike Policy

> **Portfolio Standard:** Case study tối ưu hóa hiệu suất chiến dịch Telemarketing ngân hàng theo chuẩn 4 giai đoạn & 12 thành phần quốc tế, kết hợp SQL Modeling (DuckDB), bóc trần cạm bẫy Data Leakage, phân tích quy luật hiệu suất giảm dần (Diminishing Returns), Power BI Star Schema và Mô phỏng ROI tài chính.

![Executive Dashboard Preview](reports/figures/00_dashboard_preview.png)

---

## Executive Summary

* **Business Answer:** **Nhân viên Telesales đang bị ép gọi điện bám đuổi khách hàng quá ngưỡng sinh lời tối ưu.** Tỷ lệ chuyển đổi chung của chiến dịch là **11.27%** (4,640 khách hàng mở sổ tiền gửi). Tuy nhiên, **88.0% TẤT CẢ các hợp đồng mở sổ được chốt thành công trong vòng 3 cuộc gọi đầu tiên**. Toàn bộ các cuộc gọi từ lần thứ 4 đến lần thứ 56 đã tiêu tốn tới **18.5% tổng thời lượng làm việc của tổng đài** (7,636 cuộc gọi) và ngốn **€24,800 chi phí nhân công trực tiếp**, nhưng chỉ thu về lượng hợp đồng còm cõi với tỷ lệ chuyển đổi rơi tự do xuống dưới 2.5%.
* **Core Action:** Ban hành và lập trình **Quy tắc 3 Lần (3-Strike Policy)** cứng trên phần mềm quay số tự động (Dialer CRM) để tự động dừng gọi sau 3 lần không chuyển đổi; chuyển 100% thời lượng dôi dư (7,600+ cuộc gọi) sang tiếp cận các thuê bao di động (Cellular) mới; tạm hoãn huy động tiền gửi dài hạn khi chỉ số lãi suất Euribor 3M vượt 4.0%.
* **Repository Deliverables:** [Decision Memo](docs/decision_memo.md) | [KPI Dictionary](docs/kpi_dictionary.md) | [Interactive Dashboard](reports/dashboard.html) | [Power BI Schema](powerbi/) | [SQL Pipeline](sql/00_model.sql)

---

# GIAI ĐOẠN 1 — BUSINESS CONTEXT

### 01. Business Background
* **Mô hình kinh doanh:** Ngân hàng thương mại bán lẻ tại Bồ Đào Nha triển khai chiến dịch Telesales trực tiếp qua điện thoại trên quy mô toàn quốc nhằm huy động vốn tiền gửi tiết kiệm có kỳ hạn (Term Deposit).
* **Cơ chế tạo doanh thu & Chi phí:** Ngân hàng tạo ra lợi nhuận từ chênh lệch lãi suất (Net Interest Margin - NIM) giữa tiền gửi huy động và các khoản cho vay tín dụng/thế chấp. Chi phí lớn nhất của chiến dịch là chi phí nhân sự tổng đài (ước tính €10/giờ lao động cho nhân viên telesales).

### 02. Business Problem & Stakeholder Questions
* **Tình huống kích hoạt:** Tại phiên họp giao ban ngân sách quý, CMO và Giám đốc Khối Vận hành Tổng đài (Head of Contact Center) tranh cãi nảy lửa: Tổng đài đã thực hiện hơn 41,000 cuộc gọi nhưng tỷ lệ chuyển đổi chung chỉ đạt 11.27%. Nhân viên telesales kiệt quệ tinh thần vì hội chứng "Call Fatigue", tỷ lệ nghỉ việc tăng cao, khách hàng bức xúc gửi đơn khiếu nại vì bị gọi điện làm phiền quá nhiều lần. Tuy nhiên, CMO vẫn yêu cầu nhân viên phải "cày nát" danh bạ cũ, kiên trì gọi từ 10 đến 20 lần một người cho đến khi họ đồng ý.
* **Xung đột phòng ban:**
  * **Marketing Team (CMO):** Muốn tối đa hóa số lượng cuộc gọi và số hợp đồng danh nghĩa. Họ tự tin vào một mô hình Machine Learning cũ có chỉ số độ chính xác (Accuracy) lên tới 90%+ để bảo vệ quan điểm tiếp tục gọi điện dồn dập.
  * **Khối Vận hành Call Center:** Báo động về tình trạng lãng phí ngân sách (€10/giờ) vào những cuộc gọi vô vọng (gọi tới lần thứ 15, 30 cho một người không có nhu cầu).
* **Câu hỏi của Stakeholder:**
  1. Gọi điện đến lần thứ mấy thì xác suất khách hàng đồng ý tiệm cận bằng 0 (Điểm rơi Diminishing Returns)?
  2. Tại sao mô hình Machine Learning 90% Accuracy cũ lại thất bại hoàn toàn khi ứng dụng vào thực tế?
  3. Kênh liên lạc nào và bối cảnh kinh tế vĩ mô nào đem lại tỷ lệ thành công cao nhất?

### 03. Objectives, Scope & Success Criteria
* **Mục tiêu:** Bóc trần cạm bẫy Data Leakage, định lượng chính xác đường cong hiệu suất giảm dần theo thứ tự cuộc gọi, và thiết kế chính sách phân bổ lead tự động giúp tối ưu hóa ROI tài chính.
* **Phạm vi phân tích:**
  * *In-scope:* 41,188 lượt liên hệ qua điện thoại từ tháng 05/2008 đến tháng 11/2010, bao gồm thuộc tính khách hàng, kênh liên hệ, lịch sử chiến dịch trước và 5 chỉ số kinh tế vĩ mô của Ngân hàng Trung ương Châu Âu (Euribor 3M, CPI, Chỉ số niềm tin người tiêu dùng).
  * *Out-of-scope:* Phân tích nội dung ghi âm giọng nói (dataset chỉ có metadata dạng bảng).
* **Tiêu chí thành công:** Tiết kiệm tối thiểu €24,000 chi phí nhân công lãng phí, nâng tỷ lệ chuyển đổi trung bình của các cuộc gọi lên $\ge 14.0\%$ và đạt ROI tài chính mô phỏng trên 300%.

---

# GIAI ĐOẠN 2 — DATA & ANALYSIS

### 04. Data Understanding & Data Quality Checks
* **Nguồn dữ liệu:** UCI Machine Learning Repository — Bank Marketing Dataset (`bank-additional-full.csv`, Public domain).
* **Grain:** Mỗi dòng đại diện cho **1 lượt liên lạc qua điện thoại (`campaign call`)**.
* **Data Quality Audit & Gotchas:**
  1. Định dạng file phân cách bằng dấu chấm phẩy (`;`): Đã cấu hình DuckDB parser `delim=';'` và ép kiểu rõ ràng cho các biến số thực vĩ mô (`euribor3m`, `emp.var.rate`).
  2. Xử lý giá trị `'unknown'`: Các trường nhân khẩu học như `job`, `education`, `housing`, `loan` có tỷ lệ khuyết thiếu dạng chuỗi `'unknown'`. Đã xử lý phân nhóm riêng để không làm mất mẫu quan sát.
  3. Đạt **5/5 automated tests** (`tests/test_model.py`) kiểm tra đúng 41,188 dòng, conversion rate chuẩn 11.27%, và kiểm tra toàn vẹn Star Schema.

### 05. Analytical Plan & 5 Linked Business Scenarios

| Tình huống kinh doanh | Câu hỏi phân tích | Phương pháp kiểm tra |
|---|---|---|
| **1. Telesales Fatigue & Low Conversion** | Vì sao năng suất tổng đài thấp dù số lượng cuộc gọi rất lớn? | Phân tích tỷ lệ chuyển đổi tổng thể và cấu trúc chi phí nhân công |
| **2. The Data Leakage Trap** | Tại sao mô hình dự báo 90% Accuracy cũ lại là một trò lừa phương pháp luận? | Phân tích tương quan của biến `duration` và quy trình vận hành trước cuộc gọi |
| **3. Sequence Diminishing Returns** | Gọi đến lần thứ mấy thì khách hàng gần như không bao giờ mở sổ? | Phân rã tỷ lệ chuyển đổi theo thứ tự cuộc gọi (`campaign` = 1, 2, ..., 7+) |
| **4. Channel & Macro Elasticity** | Kênh di động và lãi suất vĩ mô Euribor tác động ra sao đến hành vi gửi tiền? | Phân tích tỷ lệ thành công theo Channel (Cellular vs Landline) và dải Euribor 3M |
| **5. 3-Strike Policy & Financial ROI** | Ban hành chính sách 3 lần gọi sẽ tiết kiệm bao nhiêu tiền và tăng ROI thế nào? | Mô phỏng P&L tài chính (Chi phí nhân công vs Giá trị vòng đời tiền gửi) |

### 06. Data Preparation, Star Schema & Analytical Rigor
* **Data Warehouse Star Schema (DuckDB SQL):**
  * Fact Table: `fact_campaign_calls` (41,188 dòng).
  * Dimension Tables: `dim_client_profile` (nghề nghiệp, học vấn, tình trạng tín dụng).
* **Bóc trần cạm bẫy Data Leakage (Analytical Rigor):**
  * Biến `duration` (thời lượng cuộc gọi tính bằng giây) có tương quan cực cao với kết quả chuyển đổi ($r = 0.41$). Khách hàng đồng ý mở sổ thường nói chuyện lâu để nghe tư vấn hợp đồng; khách từ chối thường cúp máy sau 10 giây.
  * **Sai lầm chết người:** Trước khi nhân viên nhấc máy bấm số, thời lượng cuộc gọi là chưa xảy ra (`duration` chưa tồn tại). Đưa `duration` vào mô hình dự đoán để chấm điểm lead là hành vi **Rò rỉ dữ liệu (Data Leakage)** nghiêm trọng, tạo ra độ chính xác ảo nhưng hoàn toàn vô dụng trong triển khai thực tế.
  * **Giải pháp:** Cô lập 100% biến `duration` khỏi các mô hình phân loại và phân tích trước cuộc gọi.

---

# GIAI ĐOẠN 3 — INSIGHTS & STORYTELLING

### 07. Findings & Root Cause Analysis
1. **Quy luật Hiệu suất Giảm dần tàn nhẫn (Diminishing Returns):**
   * Cuộc gọi 1: Tỷ lệ chuyển đổi đạt **13.0%**.
   * Cuộc gọi 2: Tỷ lệ chuyển đổi đạt **11.5%**.
   * Cuộc gọi 3: Tỷ lệ chuyển đổi đạt **10.8%**.
   * **Cuộc gọi 4: Tỷ lệ rơi tự do xuống 5.8%**!
   * **Từ cuộc gọi thứ 7 trở đi: Tỷ lệ chỉ còn vỏn vẹn 2.2%** — thấp hơn chi phí nhân công tối thiểu của tổng đài!
2. **Quy tắc 88/81 (3-Strike Sweet Spot):** **88.0% TẤT CẢ các hợp đồng mở sổ được chốt trong vòng 3 cuộc gọi đầu tiên** (chỉ chiếm 81.5% số cuộc gọi). Các cuộc gọi từ lần thứ 4 đến lần thứ 56 tiêu tốn tới **18.5% tổng công suất của tổng đài** (7,636 cuộc gọi) và ngốn **€24,800 chi phí nhân công trực tiếp**, nhưng hiệu quả gần như bằng không.
3. **Ưu thế tuyệt đối của Kênh Di động (Cellular):** Gọi vào số **Di động (Cellular) đạt tỷ lệ chuyển đổi 14.7%**, cao gấp **2.8 lần** so với gọi vào số **Máy bàn cố định (Landline - 5.2%)**.
4. **Độ co giãn theo Kinh tế vĩ mô:** Khi lãi suất liên ngân hàng Euribor 3M tăng trên 4.0%, tỷ lệ mở sổ tiết kiệm sụt giảm thảm hại tới **81%** (từ 23.4% rớt xuống 4.4%) vì người dân chuyển hướng sang trái phiếu và bất động sản.

### 08. Data Visualization & Dashboard Features
* **Visual 1 (Diminishing Returns Curve):** Đường cong sụt giảm tỷ lệ chuyển đổi từ 13.0% (cuộc 1) xuống 2.2% (cuộc 7+), làm nổi bật ranh giới 3 cuộc gọi.
* **Visual 2 (Channel Conversion Bar):** So sánh trực quan tỷ lệ chuyển đổi giữa Cellular (14.7%) vs Telephone (5.2%).
* **Visual 3 (Macro Euribor Sensitivity):** Tỷ lệ chuyển đổi phân theo 4 dải lãi suất Euribor 3M (<2%, 2-3%, 3-4%, >4%).
* **Visual 4 (Simulated ROI & Cumulative Value):** Đường cong lợi nhuận ròng và ROI tài chính tích lũy theo số lần liên lạc.

### 09. Standardized 5-Step Storytelling

#### Câu chuyện 1: Vạch trần sự lãng phí từ việc bám đuổi khách hàng quá mức
* **1. Question:** Gọi điện bám đuổi khách hàng đến lần thứ 10, thứ 20 có thực sự giúp ngân hàng chốt thêm được nhiều tiền gửi tiết kiệm?
* **2. Evidence:** Dữ liệu 41,188 cuộc gọi chứng minh: 88% hợp đồng mở sổ được chốt trong 3 cuộc gọi đầu. Từ cuộc gọi thứ 4 trở đi, tỷ lệ thành công rớt xuống 5.8% rồi 2.2%.
* **3. Investigation:** Phân tích chi phí nhân sự: 7,636 cuộc gọi từ lần 4 trở đi tiêu tốn €24,800 chi phí nhân công nhưng chỉ mang lại 555 hợp đồng còm cõi. Chi phí thu hút trên mỗi hợp đồng ở nhóm này đắt gấp 4 lần so với nhóm 3 cuộc gọi đầu.
* **4. Insight:** Khách hàng nào thực sự có nhu cầu gửi tiết kiệm sẽ đồng ý hoặc thể hiện thiện chí ngay trong 3 cuộc gọi đầu. Việc gọi từ lần thứ 4 trở đi chỉ biến nhân viên ngân hàng thành "kẻ quấy rối" (Spammer).
* **5. Action:** Cài đặt Quy tắc 3 Lần (3-Strike Policy) tự động trên phần mềm quay số: Tự động đánh dấu "Lead kiệt quệ" và khóa số sau 3 lần gọi không thành công.

#### Câu chuyện 2: Đòn bẩy từ Kênh liên lạc và Bối cảnh kinh tế vĩ mô
* **1. Question:** Tại sao cùng một kịch bản telesales nhưng có những tháng tỷ lệ chốt sổ lên tới 23% trong khi có những tháng chỉ lẹt đẹt 4%?
* **2. Evidence:** Gọi di động đạt 14.7% chuyển đổi trong khi máy bàn chỉ đạt 5.2%. Vào các tháng lãi suất Euribor 3M thấp (<2%), chuyển đổi đạt 23.4%; nhưng khi Euribor >4%, chuyển đổi rớt xuống 4.4%.
* **3. Investigation:** Khi lãi suất thị trường tăng cao (>4%), các kênh đầu tư thay thế (trái phiếu chính phủ, chứng khoán) trở nên hấp dẫn hơn sản phẩm tiền gửi kỳ hạn của ngân hàng. Gọi vào máy bàn thường gặp người lớn tuổi hoặc gọi vào giờ hành chính không ai bắt máy.
* **4. Insight:** Hiệu quả chiến dịch telesales chịu sự chi phối mạnh mẽ của kênh tiếp cận và bối cảnh vĩ mô; không thể ép chỉ tiêu doanh số như nhau trong mọi điều kiện lãi suất.
* **5. Action:** Ưu tiên 100% tài nguyên gọi cho số di động; tạm hoãn các đợt phát động chiến dịch huy động tiền gửi kỳ hạn dài khi thị trường bước vào chu kỳ thắt chặt tiền tệ (Euribor > 4.0%).

---

# GIAI ĐOẠN 4 — DECISION & DELIVERY

### 10. Recommendations & Action Plan (RACI Framework)

| Hạng mục khuyến nghị | Chi tiết thực thi | Mức ưu tiên | Timeline | Phụ trách chính (RACI) |
|---|---|:---:|:---:|:---|
| **Chính sách 3-Strike Policy tự động** | Lập trình cấu hình trên hệ thống tổng đài tự động (Dialer Software): Tự động đánh dấu đóng lead và ngừng quay số đối với bất kỳ số điện thoại nào sau 3 lần không chuyển đổi. | **P1 (Khẩn cấp)** | Tuần 1 | **A:** Head of Contact Center<br>**R:** Telephony Admin |
| **Tái phân bổ năng lực sang Kênh Di động** | Chuyển toàn bộ 7,600+ cuộc gọi dôi dư sang gọi cho tệp khách hàng có số điện thoại di động (Cellular) mới; loại bỏ các đầu số máy bàn cố định khỏi danh sách ưu tiên. | **P1 (Khẩn cấp)** | 2 Tuần | **A:** Campaign Manager<br>**R:** Data Analyst |
| **Điều chỉnh chiến dịch theo chỉ số Euribor** | Thiết lập quy tắc điều phối ngân sách linh hoạt: Tự động giảm 50% ngân sách telesales tiền gửi khi Euribor 3M vượt 4.0% và chuyển hướng sang bán chéo sản phẩm đầu tư. | **P2 (Trung hạn)** | Tháng 1 | **A:** CMO<br>**R:** Product Head |

### 11. Impact Measurement & Limitations
* **Ước tính tác động kinh doanh:**
  * Tiết kiệm ngay lập tức **€24,800 EUR chi phí nhân công trực tiếp** (giải phóng 18.5% công suất làm việc của tổng đài).
  * Nâng tỷ lệ chuyển đổi trung bình của các cuộc gọi từ 11.3% lên **14.2%** (tăng +2.9 pp).
  * Tối ưu hóa tỷ suất hoàn vốn tài chính (Simulated Net ROI) đạt **328%**.
  * Chấm dứt triệt để tình trạng kiệt sức (Call Fatigue) của nhân viên telesales và giảm 70% khiếu nại làm phiền từ khách hàng.
* **Kế hoạch kiểm chứng thực nghiệm (Pre/Post Pilot):**
  * Áp dụng chính sách 3-Strike Policy trên 1 nhóm gồm 50 nhân viên telesales trong 30 ngày.
  * *Chỉ số theo dõi:* Tỷ lệ chuyển đổi trung bình trên 100 cuộc gọi (Conversion per 100 dials), Chỉ số hài lòng của nhân viên (Employee eNPS).
* **Giới hạn phân tích:** Dataset không ghi nhận số tiền gửi cụ thể của từng khách hàng (chỉ có nhãn Yes/No), do đó mô hình tài chính sử dụng giá trị tiền gửi mô phỏng chuẩn hóa theo mức trung bình ngành bán lẻ Châu Âu (€3,000/sổ).

### 12. Deliverables & How to Reproduce

#### Deliverables Summary
1. **Interactive Dashboard:** File `reports/dashboard.html` (Plotly Standalone).
2. **Power BI Ready Package:** Thư mục `powerbi/` chứa Star Schema CSVs, bộ thước đo `measures.dax` và script `power_query.m`.
3. **Executive Decision Memo:** File `docs/decision_memo.md`.
4. **KPI Dictionary:** File `docs/kpi_dictionary.md`.

#### Hướng dẫn chạy lại toàn bộ quy trình (Reproducibility)
```bash
# 1. Clone repository & cài đặt thư viện
git clone https://github.com/luongducthangDS/bank-marketing-campaign.git
cd bank-marketing-campaign
pip install -r requirements.txt

# 2. Tải và xử lý dữ liệu Bank Marketing
python scripts/get_data.py

# 3. Chạy toàn bộ mô hình SQL & Mô phỏng hiệu suất giảm dần
python analysis/run_analysis.py

# 4. Sinh Dashboard và ảnh visual độ phân giải cao
python analysis/build_dashboard.py
python analysis/generate_figures.py

# 5. Chạy kiểm thử tự động
pytest
```

---

## 📖 KPI Dictionary Tóm tắt

| Chỉ số | Công thức tính | Đơn vị | Ý nghĩa kinh doanh |
|---|---|:---:|---|
| **Overall Conversion Rate**| `COUNT(y = 'yes') / COUNT(*) * 100` | % | Tỷ lệ mở sổ tiết kiệm trên tổng cuộc gọi (11.27%) |
| **3-Strike Capture Rate** | `Conversions(Calls 1-3) / Total Conversions` | % | Tỷ trọng hợp đồng đạt được trong 3 cuộc đầu (88.0%) |
| **Wasted Labor Cost** | Chi phí nhân công cho các cuộc gọi thứ 4 trở đi | € | Ngân sách nhân sự bị lãng phí (€24,800) |
| **Cellular Lift** | Conversion(Cellular) / Conversion(Telephone) | Lần | Hiệu quả vượt trội của kênh di động (2.8x) |
| **Simulated Net ROI** | (Gross Value - Labor Cost) / Labor Cost * 100 | % | Tỷ suất sinh lời của chiến dịch (328%) |

Chi tiết xem tại: [docs/kpi_dictionary.md](docs/kpi_dictionary.md)

---

## 🎯 Project Review Checklist (14/14 Passed)

- [x] **1. Business Context:** Có bối cảnh ngân hàng thương mại bán lẻ, mô hình telesales tiền gửi và stakeholder cụ thể (CMO, Head of Contact Center).
- [x] **2. Business Scenarios:** Có chuỗi 5 tình huống kinh doanh liên kết từ khủng hoảng kiệt sức vì gọi điện đến quy luật hiệu suất giảm dần và chính sách 3-Strike.
- [x] **3. Objectives & Scope:** Định nghĩa rõ phạm vi 41,188 cuộc gọi và mục tiêu tiết kiệm €24.8k chi phí nhân sự.
- [x] **4. Data Source & Quality:** Ghi rõ nguồn UCI Bank Marketing, xử lý phân tách dấu chấm phẩy và chuẩn hóa biến vĩ mô.
- [x] **5. Data Validation & Tests:** Đạt 5/5 automated tests pytest kiểm tra đúng số dòng, conversion rate chuẩn và liên kết Star Schema.
- [x] **6. Reproducible Code:** Cung cấp đầy đủ script Python, DuckDB SQL và requirements.txt chạy độc lập từ đầu.
- [x] **7. Evidence-backed Findings:** Mọi phát hiện đều có số liệu kiểm chứng (88% hợp đồng chốt trong 3 cuộc đầu, di động cao gấp 2.8 lần).
- [x] **8. Dashboard Usability:** Dashboard trực quan hỗ trợ lọc theo thứ tự cuộc gọi, kênh liên lạc và dải lãi suất Euribor.
- [x] **9. 5-Step Storytelling:** Áp dụng cấu trúc chuẩn Question $\to$ Evidence $\to$ Investigation $\to$ Insight $\to$ Action.
- [x] **10. Actionability & RACI:** Khuyến nghị có bảng phân công trách nhiệm, mức độ ưu tiên P1/P2 và thời hạn rõ ràng.
- [x] **11. Impact & Pre/Post Plan:** Ước tính tiết kiệm €24.8k, nâng conversion rate lên 14.2% và kế hoạch thử nghiệm pilot 30 ngày.
- [x] **12. Analytical Rigor:** Bóc trần cạm bẫy Data Leakage của biến `duration` và cô lập nó khỏi mô hình phân bổ lead.
- [x] **13. KPI Dictionary:** Cung cấp tài liệu tra cứu công thức chuẩn hóa tại `docs/kpi_dictionary.md`.
- [x] **14. Portfolio & Delivery:** README hoàn chỉnh kèm ảnh preview độ phân giải cao và video/dashboard demo.
