# Hanoi WaterWatch — Trạm cảm biến ảo và kiểm thử

Hanoi WaterWatch là dự án của Group 5 trong môn Communication for IT Professionals (CITP). Trạm mô phỏng `ST-TOLICH-01` đại diện cho điểm Cống xả Cầu Mới trên sông Tô Lịch (21.0031, 105.8142). Trạm dùng năm chỉ số chất lượng nước để minh họa quy trình từ nhập số đo, phát hiện vượt ngưỡng đến hiển thị cảnh báo.

## Những thay đổi đã thực hiện

- Mở rộng dải nhập độ đục từ 0–200 lên **0–250 NTU**. Hai giá trị 202,0 và 215,7 NTU trong CSV được giữ nguyên khi nhập. Giá trị vượt dải được chặn tại đầu mút, ví dụ 251 NTU được xử lý thành 250 NTU.
- Áp dụng quy tắc **Cách 2** của nhóm. Simulator chọn ngưỡng độ đục 50 hoặc 75 NTU theo DO và TDS, hạ ngưỡng TDS từ 800 xuống 500 ppm, đồng thời hiển thị giới hạn đang dùng và các lý do vượt ngưỡng.
- Giới hạn bộ đếm ở 3/3. Chip chuyển xanh → vàng → đỏ theo số mẫu vi phạm liên tiếp và tự về xanh khi có một mẫu nằm trong toàn bộ giới hạn.
- Chạy lại 107 dòng CSV và 14 ca biên. Bản report cục bộ có thêm tài liệu tham khảo APA, phụ lục kiểm thử, sổ bằng chứng, prompt log và bản khai AI, đóng góp nhóm đang ở trạng thái nháp. Phần report trên nhánh `docs/tuan-references-and-evidence` đã build và qua kiểm tra liên kết 12 trang, đang chờ đưa lên GitHub.

## Cách chạy simulator trên trình duyệt

Từ thư mục gốc repo, chạy:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

Mở [Simulation.html](http://127.0.0.1:5500/Simulation.html). Có thể dùng Live Server trong VS Code để mở cùng file.

1. Chọn **Manual** để giữ đầu vào cố định. Nhập số hoặc kéo thanh trượt, rồi bấm **Run** nếu mô phỏng đang tạm dừng.
2. Xem mục **Current inputs** để biết giới hạn độ đục và lý do vi phạm. Xem chip trạng thái, đèn, bộ đếm và **Serial Monitor** sau mỗi lần đo.
3. Ở tốc độ x1, simulator lấy mẫu mỗi 3 giây và ghi một bản gửi ThingSpeak mô phỏng mỗi 15 giây. Các dòng log gửi và mã phản hồi là dữ liệu demo hiển thị trên trình duyệt. Kết nối cloud thực thuộc luồng Wokwi/firmware.
4. Dùng **Reset** để về bộ giá trị nền. Các chế độ **Normal**, **Spill** và **Random** phù hợp để minh họa. Dùng **Manual** khi muốn tái lập một mẫu CSV.

## Cách tính cảnh báo

| Chỉ số | Ý nghĩa | Dải nhập | Điều kiện trong giới hạn |
| --- | --- | --- | --- |
| pH | Độ axit hoặc kiềm | 0–14 | 6,00–8,50 |
| Độ đục | Mức cản trở truyền ánh sáng trong nước | 0–250 NTU | ≤ 75 NTU nếu DO ≥ 4,20 mg/L **và** TDS ≤ 400 ppm. Các trường hợp còn lại dùng ≤ 50 NTU |
| DO | Oxy hòa tan | 0–12 mg/L | ≥ 4,00 mg/L |
| TDS | Tổng chất rắn hòa tan | 0–2.000 ppm | ≤ 500 ppm |
| Nhiệt độ | Giá trị mô phỏng từ DS18B20 | 0–60 °C | ≤ 35,0 °C |

Mỗi mẫu được kiểm bằng các điều kiện bắt buộc. Thuật toán dùng phép **OR** giữa các vi phạm. Một mẫu có nhiều chỉ số vượt ngưỡng vẫn chỉ tăng bộ đếm một lần. Mẫu tiếp theo có mọi chỉ số trong giới hạn sẽ đưa bộ đếm về 0. Phiên bản này dùng quy tắc logic, không gán trọng số phần trăm.

| Bộ đếm | Trạng thái trên giao diện | Đèn trên board | `alert` |
| --- | --- | --- | ---: |
| 0/3 | Xanh, trong giới hạn | Xanh sáng | 0 |
| 1/3 hoặc 2/3 | Vàng, chờ xác nhận | Xanh vẫn sáng | 0 |
| 3/3 | Đỏ, đã xác nhận vượt ngưỡng mô phỏng | Đỏ sáng | 1 |

`alert = 0` nghĩa là chưa xác nhận cảnh báo và bao gồm trạng thái vàng. Các ngưỡng pH và DO có tham chiếu Mức C, Bảng 2 của QCVN 08:2023/BTNMT. Các ngưỡng độ đục, TDS và nhiệt độ bên trên là quy tắc sàng lọc của dự án. [Văn bản QCVN đã ký](https://vea.mae.gov.vn/Data/files/2023/03/QCVN%2008%20nuoc%20mat_Signed.pdf)

## Kết quả kiểm thử

Đã chạy JavaScript của `Simulation.html` tại commit `d7efdb4` trong Node.js với DOM giả lập. Mỗi dòng được reset, nhập bốn chỉ số từ CSV, đặt nhiệt độ 28,5 °C vì file thiếu cột này, rồi đo ba lần với cùng đầu vào. Kết quả so sánh dùng `alert` của lần đo thứ ba và giữ nguyên nhãn CSV. [Mã simulator đã kiểm thử](https://github.com/tuanchau832-ai/Final-Assignment/blob/d7efdb42f876c284f1d798be52b00691a0b80c9d/Simulation.html)

| Nhãn trong CSV | `alert = 0` | `alert = 1` | Tổng |
| --- | ---: | ---: | ---: |
| An toàn | 26 | 0 | 26 |
| Ô nhiễm | 0 | 81 | 81 |
| Tổng | 26 | 81 | 107 |

- Bản trước khớp **100/107 dòng (93,5%)**. Bản hiện tại khớp **107/107 dòng (100%)**. Sáu dòng độ đục trên 50 NTU chuyển sang trong giới hạn khi thỏa điều kiện dùng 75 NTU. Dòng Tô Lịch tại Đập Thanh Liệt có TDS 600 ppm chuyển sang cảnh báo theo ngưỡng 500 ppm.
- Các ca biên đi qua pH, DO, TDS, nhiệt độ, hai ngưỡng độ đục và trần nhập. Phép thử cũng kiểm tra đổi ngưỡng khi sửa đầu vào và trở về xanh sau một mẫu trong giới hạn.
- Ví dụ, 75 NTU với DO 4,20 mg/L và TDS 400 ppm vẫn xanh nếu các chỉ số còn lại đạt. 60 NTU với DO 4,19 mg/L và TDS 300 ppm cho chuỗi vàng → vàng → đỏ do ngưỡng độ đục lúc đó là 50 NTU.

Tỷ lệ 100% đo độ khớp với nhãn của **tập dữ liệu đã dùng để phát triển quy tắc**. Nhóm cần xác minh nguồn gốc và cách gán nhãn, thử trên tập quan trắc độc lập, đồng thời hiệu chuẩn thiết bị trước khi đánh giá hiệu quả ngoài thực địa. DO và TDS chỉ là tín hiệu hỗ trợ chọn ngưỡng. Việc xác định phù sa, chất gây đục hay nguồn xả thải cần thêm bằng chứng.

## Thiết kế Wokwi và kết nối website trong Google Doc

Ghi chú kỹ thuật của nhóm mô tả ba phần việc. Đạt và Tuấn phụ trách trạm Wokwi ESP32. Akai và Ngân phụ trách bản đồ Leaflet. Thư, Đạt và cả nhóm tham gia mô hình vỏ trạm 3D trên Tinkercad.

### Linh kiện và chân theo sơ đồ đề xuất

| Thành phần | GPIO trên ESP32 | Vai trò |
| --- | --- | --- |
| Bốn biến trở | 34, 35, 32, 33 | Lần lượt giả lập pH, độ đục, DO và TDS. Sơ đồ đề xuất dùng các chân ADC1 khi bật Wi-Fi |
| DS18B20 | 4 | Đọc nhiệt độ qua OneWire và DallasTemperature |
| LED xanh và LED đỏ | 26 và 27 | Hiển thị trạng thái, mỗi LED dùng điện trở 220 Ω |

### Luồng dữ liệu đề xuất

1. **Wokwi ESP32** kết nối `Wokwi-GUEST`. Thiết kế tách chu kỳ đo 3 giây và gửi 15 giây bằng `millis()`. Mã ví dụ trong Google Doc còn dùng khoảng chờ cho vòng đo, nên cần kiểm tra firmware thực tế trước khi demo.
2. **ThingSpeak** nhận sáu trường theo thứ tự `field1` pH, `field2` độ đục, `field3` DO, `field4` nhiệt độ, `field5` TDS và `field6` cờ cảnh báo 0/1. Cấu hình Channel ID và khóa ghi theo hướng dẫn firmware. Giữ khóa ở cấu hình cục bộ.
3. **Dashboard Leaflet** mẫu đọc dữ liệu mỗi 5 giây để cập nhật chấm trạm, chỉ số, banner và lịch sử. Đề xuất ban đầu là host dashboard tĩnh qua GitHub Pages rồi nhúng vào Google Sites. Google Doc cũng mô tả phương án Node.js/Express với `POST /api/alerts` và `GET /api/alerts`, triển khai riêng nếu chọn kiến trúc backend.

Sketch và dashboard mẫu trong Google Doc còn dùng **TDS 800 ppm**, độ đục **50 NTU cố định** và dải độ đục **0–200 NTU**. Các số này mô tả bản thiết kế ban đầu. Phép thử 107 dòng áp dụng cho simulator JavaScript đã cập nhật. Nếu dùng sketch mẫu để quay demo tích hợp, nhóm cần đồng bộ quy tắc, kiểm tra lại trạng thái trên bản đồ và đo thời gian truyền từ Wokwi qua cloud.

Các hạng mục mở rộng trong Google Doc gồm kiểm tra lỗi cảm biến, lọc trung bình trượt, phát hiện biến động nhanh, bù nhiệt độ cho DO, đồng bộ NTP, bộ đệm khi mất mạng, LCD I2C 20×4, còi, nút bảo trì và xác nhận, mô phỏng pin mặt trời, Telegram và thông báo phục hồi. Đây là các đề xuất để làm tiếp theo mức ưu tiên.

## Demo và bàn giao

1. **0–10 giây:** Hiển thị đầu vào trong giới hạn, bộ đếm 0/3, LED xanh.
2. **10–25 giây:** Tăng TDS lên trên 1.200 ppm và độ đục lên trên 100 NTU. Chỉ rõ chuỗi 1/3 → 2/3 → 3/3, chip đỏ và `alert = 1`.
3. **25–45 giây:** Với demo đã kết nối cloud, hiển thị chấm bản đồ, banner và lịch sử sau khi dữ liệu cập nhật. Với simulator trình duyệt, hiển thị Serial Monitor và bản ghi gửi mô phỏng.
4. **45–55 giây:** Đưa đầu vào về trong giới hạn để minh họa phục hồi. Sau khi nhóm duyệt video và quyền chia sẻ, có thể nhúng video đã duyệt vào Google Sites.

Để chạy riêng **website báo cáo**, từ gốc repo dùng Node.js 22.12+:

```bash
cd website
npm ci
npm run dev
```

`npm run check:links` kiểm tra đường dẫn, `npm run build` tạo bản production. Trước khi nộp, nhóm còn cần chốt reverse brief, nguồn gốc dữ liệu, hình và báo giá, khai AI và đóng góp, sau đó kiểm tra giới hạn 4.000 từ theo mẫu. Mẫu yêu cầu Google Sites. Nếu dùng Vercel cho bản nộp, xác nhận với giảng viên trước. [README website báo cáo](https://github.com/tuanchau832-ai/Final-Assignment/blob/main/website/README.md)

Khi đưa tài liệu vào repo nhóm, có thể đặt file tại `docs/tram-cam-bien/README.md`, commit trên nhánh phụ trách và mở pull request về `main`. [Quy trình Git của nhóm](https://github.com/tuanchau832-ai/Final-Assignment/blob/main/GITHUB_TEAM_WORKFLOW.md)

## Tài liệu đối chiếu

- **note trạm cảm biến**, Google Doc nội bộ của Group 5, phần 1–6.
- **Phân loại các nhóm sông có phù sa**, tài liệu nội bộ của nhóm, mục Cách 2.
- **du_lieu_nuoc_song_ha_noi.csv**, dữ liệu nội bộ dùng trong phép thử 107 dòng.
- [Hướng dẫn ứng dụng HanoiWaterWatch](https://github.com/tuanchau832-ai/Final-Assignment/blob/main/HanoiWaterWatch/README.md) và [hướng dẫn firmware](https://github.com/tuanchau832-ai/Final-Assignment/blob/main/HanoiWaterWatch/firmware/README.md).
