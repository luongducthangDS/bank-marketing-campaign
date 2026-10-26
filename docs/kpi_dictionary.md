# KPI Dictionary: UCI Bank Marketing Campaign Performance & ROI

Tài liệu định nghĩa chuẩn hóa toàn bộ các chỉ số đo lường hiệu suất vận hành Call Center, quy luật hiệu suất giảm dần (Diminishing Returns) và hiệu quả tài chính mô phỏng (Financial ROI) của chiến dịch Telemarketing.

---

## 1. Bảng tra cứu KPI cốt lõi

| Mã KPI | Tên chỉ số | Công thức tính toán | Đơn vị | Grain / Phạm vi tính | Ý nghĩa kinh doanh & Ngưỡng chuẩn |
|:---|:---|:---|:---:|:---|:---|
| **KPI-01** | **Total Campaign Contacts** | `COUNT(*)` các lượt gọi điện | Cuộc gọi | Toàn chiến dịch ngân hàng | Tổng số lượt liên lạc qua điện thoại được thực hiện. Hiện trạng: **41,188 cuộc gọi**. |
| **KPI-02** | **Total Conversions** | `COUNT(y = 'yes')` | Hợp đồng | Toàn chiến dịch / Phân khúc | Tổng số khách hàng đồng ý mở sổ tiền gửi tiết kiệm có kỳ hạn. Đạt: **4,640 hợp đồng**. |
| **KPI-03** | **Overall Conversion Rate %** | `[Total Conversions] / [Total Contacts] * 100` | % | Toàn chiến dịch | Tỷ lệ thành công trung bình trên toàn bộ các lượt gọi. Đạt: **11.27%**. |
| **KPI-04** | **3-Strike Contact Share** | `COUNT(campaign <= 3) / COUNT(Total Contacts) * 100` | % | Chiến dịch / Telesales policy | Tỷ trọng các cuộc gọi thuộc nhóm 1 đến 3 lần đầu. Đạt: **81.5%** (33,552 cuộc gọi). |
| **KPI-05** | **3-Strike Conversion Capture** | `COUNT(y='yes' in campaign <= 3) / Total Conversions * 100` | % | Chiến dịch / Telesales policy | Tỷ trọng các hợp đồng mở sổ thu được trong 3 cuộc gọi đầu. Đạt: **88.0%** (4,085 hợp đồng). |
| **KPI-06** | **Sequence Diminishing Returns** | `Conversion Rate` theo từng bậc số lần liên lạc (`campaign` = 1, 2, 3, 4, 5, 6, 7+) | % | Từng thứ tự cuộc gọi | Đo lường điểm rơi hiệu suất. Cuộc 1: **13.0%** $\to$ Cuộc 2: **11.5%** $\to$ Cuộc 3: **10.8%** $\to$ Cuộc 4: **5.8%** $\to$ Cuộc 7+: **2.2%**. |
| **KPI-07** | **Wasted Labor Cost (Calls 4+)** | `COUNT(campaign >= 4) * (average_duration_hours * hourly_wage)` | EUR (€) | Toàn chiến dịch | Chi phí nhân sự telesales bị lãng phí vào các cuộc gọi vượt quá ngưỡng tối ưu. Đạt: **€24,800 EUR** (18.5% công suất). |
| **KPI-08** | **Cellular vs Landline Conversion Ratio**| `Conversion(Cellular) / Conversion(Telephone)` | Lần | Kênh liên lạc | Tỷ số chênh lệch hiệu quả giữa gọi di động (14.7%) và gọi máy bàn (5.2%). Đạt: **2.83 lần**. |
| **KPI-09** | **Macro Euribor Elasticity** | `Conversion(Euribor < 2.0%) / Conversion(Euribor > 4.0%)` | Lần | Môi trường kinh tế vĩ mô | Mức độ sụt giảm nhu cầu gửi tiết kiệm khi lãi suất thị trường thắt chặt (23.4% rơi xuống 4.4% $\to$ Sụt giảm **-81%**). |
| **KPI-10** | **Simulated Campaign Net ROI** | `([Gross Financial Value] - [Total Labor Cost]) / [Total Labor Cost] * 100` | % | Mô phỏng tài chính P&L | Tỷ suất hoàn vốn trên chi phí nhân sự telesales (€130k chi phí $\to$ €426k net profit). Đạt: **328%**. |

---

## 2. Bảng phân rã Hiệu suất Giảm dần theo Thứ tự Cuộc gọi

| Thứ tự cuộc gọi (`campaign`) | Số lượt liên lạc | Tỷ lệ chuyển đổi (%) | Số hợp đồng đạt được | Tích lũy hợp đồng (%) | Tích lũy công suất (%) | Nhận định năng suất Call Center |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Cuộc gọi 1** | 17,642 | **13.0%** | 2,300 | 49.6% | 42.8% | Rất hiệu quả (Lead còn tươi mới) |
| **Cuộc gọi 2** | 10,570 | **11.5%** | 1,211 | 75.7% | 68.5% | Hiệu quả cao (Follow-up thành công) |
| **Cuộc gọi 3** | 5,340 | **10.8%** | 574 | **88.0%** | **81.5%** | **Điểm dừng tối ưu (Sweet Spot)** |
| **Cuộc gọi 4** | 2,651 | **5.8%** | 154 | 91.3% | 87.9% | Bắt đầu lỗ công nhân viên |
| **Cuộc gọi 5** | 1,598 | **4.2%** | 67 | 92.8% | 91.8% | Năng suất thấp |
| **Cuộc gọi 6** | 979 | **3.8%** | 37 | 93.6% | 94.2% | Lãng phí thời gian telesales |
| **Cuộc gọi 7 – 56** | 2,408 | **2.2%** | 53 | 100.0% | 100.0% | **Vô nghĩa: Gây Call Fatigue và khiếu nại** |

---

## 3. Cạm bẫy Data Leakage của biến `duration`

- **Định nghĩa:** `duration` là thời lượng thực tế của cuộc gọi điện tính bằng giây.
- **Thực tế nghiệp vụ:** Trước khi bấm máy quay số, nhân viên telesales **không thể biết** cuộc gọi sẽ kéo dài 10 giây hay 15 phút.
- **Nguy cơ sai lệch:** Mô hình Machine Learning đưa `duration` vào sẽ đạt độ chính xác ảo (Accuracy > 92%, AUC > 0.93) vì khách đồng ý mua luôn nói chuyện lâu hơn khách từ chối. Trong môi trường triển khai thực tế, mô hình này hoàn toàn sụp đổ vì giá trị `duration = 0` tại thời điểm quyết định gọi hay không gọi.
- **Chuẩn mực phương pháp luận:** Cô lập 100% biến `duration` khỏi các mô hình dự báo và phân bổ lead trước cuộc gọi.
