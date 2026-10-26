# Bank Marketing: Eliminating Call Fatigue with a 3-Strike Policy

Analysis of **41,188 telemarketing contacts** from the Portuguese Bank Marketing dataset (UCI Machine Learning Repository). It assesses call center operational efficiency, exposes the fatal trap of Data Leakage in telemarketing models, quantifies diminishing returns per contact, and designs an optimized lead allocation policy backed by an interactive dashboard.

![Dashboard](reports/figures/00_dashboard_preview.png)

## Executive Answer

**Telemarketers are over-calling cold leads past the point of negative return.** The baseline conversion rate is **11.27%** (4,640 term deposit subscribers). However, **88.0% of all conversions are secured within the first 3 calls**. Calls 4 through 56 consume **18.5% of sales capacity** (7,636 dials) and €24.8k in labor, but yield diminishing returns (<2.5% conversion).

| Finding | Metric |
|---|---|
| Total Contacts Analyzed | **41,188 phone calls** |
| Total Conversions & Rate | **4,640 conversions (11.27%)** |
| Simulated Campaign Profit & ROI | **€426,931 net profit** (ROI: 328% based on labor cost) |
| Sequence Diminishing Returns | Call 1: **13.0%** $\to$ Call 2: **11.5%** $\to$ Call 3: **10.8%** $\to$ Call 4: **5.8%** $\to$ Call 7+: **2.2%** |
| 3-Strike Policy Efficiency | 81.5% of contacts capture **88.0% of total subscriptions** |
| Cellular vs Landline Conversion | **14.7% (Cellular)** vs. **5.2% (Landline)** (2.8x higher response) |
| Macroeconomic Elasticity | Euribor <2.0%: **23.4% conversion** vs. Euribor >4.0%: **4.4% conversion** (-81% drop) |
| Prior Campaign Success Lift | Odds Ratio = **1.85x** ($p < 0.001$) for clients with successful past interactions |

**So what:** Enforce an automated **3-Strike Policy** in dialer software to drop leads after 3 unsuccessful attempts; reallocate freed capacity to fresh mobile contacts; avoid heavy deposit pushes during high-interest-rate tightening environments.

## 📖 Business Storytelling & Problem Statement

### 1. Tình huống kích hoạt (The Trigger Scenario)
Tại phiên họp giao ban ngân sách quý của Ngân hàng Bồ Đào Nha, **Giám đốc Tiếp thị (CMO)** và **Giám đốc Khối Vận hành Tổng đài (Head of Contact Center)** tranh cãi nảy lửa:
> *"Tổng đài đã thực hiện hơn 41,000 cuộc gọi chào mời tiền gửi tiết kiệm có kỳ hạn (Term Deposit), nhưng tỷ lệ chuyển đổi chung chỉ đạt 11.27%. Đội ngũ nhân viên Telesales đang kiệt quệ tinh thần vì hội chứng 'Call Fatigue', tỷ lệ nhân sự xin nghỉ việc tăng cao, và khách hàng liên tục khiếu nại vì bị gọi điện làm phiền quá nhiều lần. Tuy nhiên, CMO vẫn yêu cầu nhân viên phải 'cày nát' danh bạ khách hàng cũ, kiên trì gọi từ 10 đến 20 lần một người cho đến khi họ đồng ý!"*

Tổng Giám đốc ngân hàng yêu cầu Data Analyst độc lập phân tích dữ liệu 41,188 cuộc gọi để phân xử bằng dữ liệu thực nghiệm: Đâu là điểm rơi tối ưu của nỗ lực telesales?

### 2. Xung đột nghiệp vụ & Bẫy ngộ nhận (The Core Problem & Conflict)
* **Xung đột phòng ban:**
  * **Marketing Team (CMO):** Muốn tối đa hóa số lượng cuộc gọi và số hợp đồng danh nghĩa. Họ tự tin vào một mô hình Machine Learning cũ có chỉ số độ chính xác (Accuracy) lên tới 90%+ để bảo vệ quan điểm tiếp tục gọi điện dồn dập.
  * **Khối Vận hành Call Center:** Báo động về tình trạng lãng phí ngân sách khi mỗi giờ lao động của nhân viên tốn €10/giờ nhưng phải gọi những cuộc gọi vô vọng (gọi tới lần thứ 15, thứ 30 cho một người không hề có nhu cầu).
* **Bẫy ngộ nhận & Sai lầm phương pháp luận (Methodological Fallacy):**
  1. *Bẫy kinh doanh:* Cho rằng *"Càng kiên trì gọi nhiều lần thì khách hàng càng dễ mủi lòng mở sổ tiết kiệm"*.
  2. *Bẫy kỹ thuật Data Leakage:* Mô hình 90% Accuracy cũ đưa biến `duration` (thời lượng cuộc gọi) vào làm biến dự báo. **Thực tế, trước khi nhấc máy gọi, telesales không thể biết cuộc gọi sẽ kéo dài bao nhiêu giây!** Đưa `duration` vào dự đoán là hành vi rò rỉ dữ liệu nghiêm trọng, hoàn toàn vô dụng trong triển khai thực tế.

### 3. Cung bậc câu chuyện dữ liệu (The Data Story Arc)
* **Hồi 1 - Ảo tưởng ban đầu (The False Comfort):** Tổng cộng 4,640 khách hàng đã mở sổ tiết kiệm, tỷ lệ chuyển đổi 11.27%, tạo ra khoản lợi nhuận ròng mô phỏng €426k — nhìn trên báo cáo tổng thể, chiến dịch có vẻ đang có lãi.
* **Hồi 2 - Vết nứt xuất hiện (The Investigation):**
  * Data Analyst lập tức loại bỏ biến `duration` khỏi mô hình dự báo để loại trừ gian lận dữ liệu.
  * Khi phân tích thứ tự liên hệ (Call Sequence Diminishing Returns), quy luật hiệu suất giảm dần bộc lộ một cách tàn nhẫn:
    * Cuộc gọi 1: Tỷ lệ chuyển đổi đạt **13.0%**.
    * Cuộc gọi 2: Tỷ lệ chuyển đổi đạt **11.5%**.
    * Cuộc gọi 3: Tỷ lệ chuyển đổi đạt **10.8%**.
    * **Cuộc gọi 4: Tỷ lệ rơi tự do xuống 5.8%**!
    * **Từ cuộc gọi thứ 7 trở đi: Tỷ lệ chỉ còn vỏn vẹn 2.2%** — thấp hơn rất nhiều so với chi phí nhân công tối thiểu của tổng đài.
* **Hồi 3 - Điểm bùng nổ "Aha!" (The Naked Truth):**
  * **88.0% TẤT CẢ các khoản tiền gửi tiết kiệm được chốt thành công trong vòng 3 cuộc gọi đầu tiên!**
  * Toàn bộ các cuộc gọi từ lần thứ 4 đến lần thứ 56 đã tiêu tốn tới **18.5% tổng thời lượng làm việc của toàn bộ tổng đài** (7,636 cuộc gọi) và ngốn **€24,800 chi phí nhân công trực tiếp**, nhưng chỉ thu về lượng hợp đồng còm cõi với chi phí đắt gấp 5 lần giá trị thu về.
  * Kênh liên hệ: Gọi vào số **Di động (Cellular) đạt tỷ lệ chuyển đổi 14.7%**, cao gấp **2.8 lần** so với gọi vào số **Máy bàn cố định (Landline - 5.2%)**.
  * Bối cảnh kinh tế vĩ mô: Khi lãi suất liên ngân hàng Euribor 3M tăng trên 4.0%, tỷ lệ mở sổ tiết kiệm sụt giảm thảm hại tới **81%** (từ 23.4% rớt xuống 4.4%) vì người dân chuyển hướng sang trái phiếu và bất động sản.
* **Hồi 4 - Tháo gỡ nút thắt (The Strategic Resolution):**
  1. **Ban hành Quy tắc 3 Lần (3-Strike Policy) tự động:** Lập trình phần mềm quay số tự động (Dialer CRM) tự động khóa và ngừng gọi đối với bất kỳ khách hàng nào sau 3 lần không chuyển đổi.
  2. **Tái phân bổ năng lực:** Chuyển 100% thời lượng dôi dư (hơn 7,600 cuộc gọi) sang gọi cho tệp thuê bao di động hoàn toàn mới.
  3. **Chiến lược theo chu kỳ vĩ mô:** Tạm hoãn các chiến dịch huy động tiền gửi dài hạn khi chỉ số Euribor 3M vượt ngưỡng 4.0% để tránh đốt tiền quảng cáo ngược dòng thị trường.
* **Hồi 5 - Tác động kinh doanh (The Business Impact):**
  * Tiết kiệm ngay lập tức **18.5% ngân sách lao động Call Center** (€24,800).
  * Nâng tỷ lệ chuyển đổi bình quân trên mỗi cuộc gọi từ 11.3% lên **14.2%**.
  * Chấm dứt triệt để tình trạng kiệt sức (Call Fatigue) của nhân viên telesales và tối ưu hóa ROI chiến dịch đạt **328%**.

## Architecture & Method

1. **Model** (`sql/00_model.sql`, DuckDB): Cleans 41k records, parses semicolons with explicit casting, engineers call sequence tiers, constructs macroeconomic indices, and simulates financial labor costs and customer lifetime value.
2. **Methodological Rigor (Data Leakage Removal)**: The duration column is strictly isolated from predictive modeling. In real-world deployment, call duration is unobserved before dialing; including it produces artificial 90%+ AUC that fails in production.
3. **Checks** (`tests/test_model.py`, pytest): 5 tests verifying exact row volumes (41,188), benchmark conversion rates (11.27%), tier logic consistency, client profile surrogate key uniqueness, and star schema referential integrity.
4. **Outputs**:
   - `reports/results.json` (reproducible metrics).
   - `reports/dashboard.html` (interactive Plotly dashboard).
   - `powerbi/`: Star schema CSVs (`fact_campaign_calls.csv`, `dim_client_profile.csv`), `measures.dax`, and `power_query.m`.

## How to Run It

```bash
pip install -r requirements.txt
python scripts/get_data.py              # Fetches and extracts clean dataset from UCI zip
pytest -q                               # Runs 5 data integrity and referential checks
python analysis/run_analysis.py         # Produces reports/results.json
python analysis/build_dashboard.py      # Exports powerbi/*.csv & reports/dashboard.html
```

## Decisions Worth Defending in an Interview

- **Why is `duration` considered data leakage?** The UCI dataset documentation notes that call duration is strongly correlated with conversion because an interested customer talks longer. However, duration is only known *after* the call ends. Using duration to predict who to call in advance is classic post-hoc data leakage. Our model excludes duration to reflect realistic outbound prioritization.
- **Why simulate ROI when deposit amounts are unobserved?** Real business decisions require currency trade-offs, not just F1-scores. By anchoring labor cost (€1.00 base + €0.50/min) and average retail banking deposit margin (€120 LTV), we translate statistical findings into executive P&L terms and demonstrate commercial acumen.
- **How does macroeconomics confound conversion?** Euribor 3-month rates reflect general interest rate conditions. When Euribor was >4% (2008 pre-crisis), consumers sought competing money market yields, cutting bank term deposit conversion from 23.4% down to 4.4%. Controlling for macro trends prevents attributing market-wide shifts to telemarketer performance.

## Interview Questions this Project Prepares For

1. Why is call duration dangerous to use as an input feature for outbound lead scoring?
2. How did you formulate your simulated ROI, and how would you validate your financial assumptions with the finance team?
3. What is the business trade-off of capping calls at 3: won't you lose the 12% of conversions that occur on calls 4+?
