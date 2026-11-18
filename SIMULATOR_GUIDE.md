# Hanoi WaterWatch — Hướng dẫn mô phỏng và đánh giá kết quả

Phiên bản thử nghiệm ngày 18/11/2026. Mở `Simulation.html` cùng thư mục với `Simulation.css` để chạy mô phỏng.

## Mục tiêu và phạm vi

Mô phỏng nhập năm thông số chất lượng nước, so sánh với các giới hạn của nhóm và xác nhận cảnh báo sau ba lần đo liên tiếp có vi phạm. Giao diện cho biết ngưỡng độ đục đang áp dụng và nguyên nhân vượt giới hạn.

“Cách 2” được triển khai theo hàm `isSafeBySensorsOnly` trong tài liệu nhóm **PHÂN LOẠI CÁC NHÓM SÔNG CÓ PHÙ SA.docx**. DO và TDS quyết định có dùng ngưỡng độ đục mở rộng hay không. Đây là giả thuyết sàng lọc cần kiểm chứng bằng quan trắc và lấy mẫu. Tổ hợp cảm biến này chưa xác định được nguồn gốc phù sa hoặc chất gây đục.

## Cách sử dụng

1. Chọn **Manual**, nhập số hoặc kéo thanh trượt. Thay đổi một ô cũng tự chuyển sang Manual.
2. Bấm **Run** nếu đang tạm dừng. Đọc phần Current inputs để xem giới hạn độ đục và các chỉ số đang vượt giới hạn.
3. Quan sát chip màu trên thanh đầu và Serial Monitor sau mỗi lần đo. Màu ở ô nhập cập nhật ngay, còn chip cảnh báo chỉ cập nhật theo chu kỳ đo.
4. Chọn **Normal**, **Spill** hoặc **Random** để thử dữ liệu tự sinh. Dữ liệu tự sinh thay đổi dần và có nhiễu, vì vậy không dùng chế độ này để tái hiện chính xác một dòng CSV.
5. **Reset** đặt lại các giá trị nền và bộ đếm, rồi lấy một mẫu khởi tạo. Chọn Manual để giữ số đo cố định khi kiểm thử.

Ở tốc độ x1, app đo mỗi 3 giây và mô phỏng gửi dữ liệu mỗi 15 giây. x3 và x10 tăng tốc đồng hồ mô phỏng. Sau khi nhập dữ liệu ở thời điểm bất kỳ, mẫu vi phạm thứ ba thường xuất hiện sau khoảng 6–9 giây mô phỏng, tùy thời điểm nhập trong chu kỳ.

## Ý nghĩa từng chỉ tiêu và dải nhập

| Chỉ tiêu | Ý nghĩa | Đơn vị | Dải nhập | Điều kiện trong giới hạn |
|---|---|---|---|---|
| pH | Độ axit hoặc kiềm | Không có | 0–14 | 6,00 ≤ pH ≤ 8,50 |
| Turbidity | Độ đục do vật chất ảnh hưởng đến sự truyền ánh sáng | NTU | 0–250 | ≤ 50 hoặc ≤ 75 theo điều kiện DO/TDS |
| Dissolved O2 / DO | Oxy hòa tan trong nước | mg/L | 0–12 | DO ≥ 4,00 |
| TDS | Tổng chất rắn hòa tan, không đồng nghĩa với chất rắn lơ lửng | ppm | 0–2.000 | TDS ≤ 500 |
| Temperature | Nhiệt độ mô phỏng từ DS18B20 | °C | 0–60 | Nhiệt độ ≤ 35,0 |

Các dấu bằng đều được chấp nhận. Nhiệt độ được giữ từ logic cũ của app, bổ sung cho bốn chỉ số trong “cách 2”. Dữ liệu CSV hiện thiếu nhiệt độ nên phần kiểm thử sử dụng mặc định 28,5°C.

Ô nhập và thanh kéo dùng chung giá trị. Giá trị vượt dải được giới hạn về đầu mút. Ví dụ nhập 251 NTU sẽ áp dụng 250 NTU. Giới hạn dải nhập 250 NTU cho phép app nhận hai mẫu 202,0 và 215,7 NTU trong CSV.

Thanh kéo có bước pH 0,05, độ đục 1 NTU, DO 0,1 mg/L, TDS 10 ppm và nhiệt độ 0,1°C. Nhập trực tiếp có thể giữ nhiều chữ số hơn số đang hiển thị. App so sánh giá trị lưu trong bộ nhớ trước khi định dạng hiển thị, nên các số rất sát ngưỡng có thể nhìn giống nhau sau làm tròn.

## Cách tính output và trọng số

App dùng các điều kiện logic. Mỗi giới hạn là một điều kiện bắt buộc, và chưa có điểm tổng hợp hoặc trọng số phần trăm cho từng chỉ tiêu.

```text
maxTurbidity = 75 nếu DO >= 4.20 và TDS <= 400
maxTurbidity = 50 trong các trường hợp còn lại

breached = pH < 6.00 hoặc pH > 8.50
           hoặc turbidity > maxTurbidity
           hoặc DO < 4.00
           hoặc TDS > 500
           hoặc temperature > 35.0

breachCount = min(breachCount + 1, 3) nếu breached
breachCount = 0 nếu toàn bộ chỉ số trong giới hạn

alert = 1 nếu breachCount >= 3
alert = 0 trong các trường hợp còn lại
```

Một lần đo có ba chỉ tiêu vi phạm vẫn tăng bộ đếm một đơn vị. Bộ đếm đếm **số lần đo liên tiếp có bất kỳ vi phạm**, không đếm số chỉ tiêu. Chỉ tiêu gây vi phạm có thể thay đổi giữa các lần đo mà chuỗi vẫn tiếp tục.

Khi sửa DO hoặc TDS, giới hạn độ đục và màu các ô được tính lại ngay. Ví dụ độ đục 60 NTU với DO 5 và TDS 300 được chấp nhận. Nếu DO giảm xuống 4,1, giới hạn độ đục trở về 50 NTU và mẫu kế tiếp vi phạm dù DO vẫn trên mức tối thiểu 4.

## Màu, đèn và alert

| Trạng thái mẫu gần nhất | breachCount | Chip | LED xanh | LED đỏ | alert |
|---|---:|---|---|---|---:|
| Toàn bộ chỉ số trong giới hạn | 0/3 | Xanh, WITHIN LIMITS | Sáng | Mờ | 0 |
| Vi phạm lần liên tiếp thứ nhất | 1/3 | Vàng | Sáng | Mờ | 0 |
| Vi phạm lần liên tiếp thứ hai | 2/3 | Vàng | Sáng | Mờ | 0 |
| Vi phạm liên tiếp từ lần thứ ba | 3/3 | Đỏ | Mờ | Sáng | 1 |

`alert = 0` nghĩa là chưa có cảnh báo được xác nhận. Trạng thái này bao gồm cả hai lần cảnh báo vàng, nên cần xem cùng chip và bộ đếm. `alert = 1` nghĩa là ba mẫu liên tiếp đã vi phạm ít nhất một giới hạn. Một mẫu về trong toàn bộ giới hạn đưa bộ đếm và alert về 0 ngay.

Hai LED mô phỏng dùng opacity 1 khi sáng và 0,35 khi mờ. Giao diện có chip vàng nhưng mạch hiển thị hai LED xanh/đỏ. LED xanh vẫn sáng khi đang chờ xác nhận. LED xanh dương trên board nháy sau mỗi lần đo.

Ảnh minh họa cũ trong trao đổi có pH 7,38, độ đục khoảng 200 NTU, DO 3,40 mg/L, nhiệt độ 17,8°C và TDS 1.380 ppm. Theo phiên bản này, mẫu đó vi phạm độ đục, DO và TDS. Ba mẫu liên tiếp như vậy đưa alert lên 1. Giá trị kiểu `50/3` ở phiên bản cũ biểu thị 50 mẫu vi phạm liên tiếp, với 3 là số mẫu cần xác nhận. Phiên bản này chặn bộ đếm ở 3/3 để dễ đọc.

## Các thành phần và materials

| Thành phần hiển thị | Vai trò trong thiết kế mô phỏng |
|---|---|
| ESP32 DevKit / WROOM-32 | Board trung tâm minh họa việc đọc cảm biến và xử lý cảnh báo |
| Bốn biến trở / thanh nhập | Đại diện tín hiệu pH, độ đục, DO và TDS |
| DS18B20 | Cảm biến nhiệt độ được mô phỏng bằng giá trị nhập |
| LED xanh, LED đỏ và điện trở 220 Ω | Minh họa trạng thái trước và sau xác nhận cảnh báo |
| Dây nối, đường nguồn, cổng USB | Minh họa mạch và các kết nối |
| Serial Monitor | Hiển thị số đo, chuỗi vi phạm, giới hạn độ đục và nguyên nhân |
| ThingSpeak panel | Hiển thị bản ghi giả lập theo chu kỳ 15 giây |

Web được viết bằng HTML, CSS và JavaScript với hình mạch SVG. Thay đổi thanh trượt sinh số liệu phần mềm. Mô phỏng hiện chưa kiểm chứng ADC, hiệu chuẩn cảm biến, đặc tính điện, độ chính xác DS18B20 hay mạch ESP32 thật. Không dùng sơ đồ minh họa làm hướng dẫn đi dây phần cứng đã xác nhận.

## Dữ liệu ThingSpeak mô phỏng

| Field | Nội dung |
|---|---|
| field1 | pH |
| field2 | Độ đục, NTU |
| field3 | DO, mg/L |
| field4 | Nhiệt độ, °C |
| field5 | TDS, ppm |
| field6 | alert, 0 hoặc 1 |

Chuỗi `GET api.thingspeak.com/update` và `Code 200` là nội dung log mô phỏng. Hàm gửi hiện không thực hiện HTTP request, chưa kết nối Wi-Fi thật và chưa ghi lên tài khoản ThingSpeak. Khi alert bằng 0 nhưng bộ đếm là 1 hoặc 2, panel ghi rõ PENDING WARNING.

## Test cases

Trong bảng, thứ tự số đo là pH / độ đục NTU / DO mg/L / TDS ppm / nhiệt độ °C. Chạy mỗi case độc lập, bắt đầu với bộ đếm 0 và Manual.

| Case | Giá trị | Giới hạn độ đục | Kết quả theo ba mẫu |
|---|---|---:|---|
| Trong giới hạn | 7,2 / 20 / 5 / 300 / 28,5 | 75 | Xanh → xanh → xanh, alert 0 |
| Đúng biên mở rộng | 7,2 / 75 / 4,2 / 400 / 28,5 | 75 | Xanh → xanh → xanh |
| Trên biên mở rộng | 7,2 / 75,01 / 5 / 300 / 28,5 | 75 | Vàng 1/3 → vàng 2/3 → đỏ 3/3 |
| DO chưa đủ để mở rộng | 7,2 / 60 / 4,19 / 300 / 28,5 | 50 | Vàng → vàng → đỏ do độ đục |
| TDS chưa đủ để mở rộng | 7,2 / 60 / 5 / 400,01 / 28,5 | 50 | Vàng → vàng → đỏ do độ đục |
| Đúng các biên nghiêm ngặt | 6 / 50 / 4 / 500 / 35 | 50 | Xanh → xanh → xanh |
| pH cao | 8,51 / 20 / 5 / 300 / 28,5 | 75 | Vàng → vàng → đỏ |
| DO thấp | 7,2 / 20 / 3,99 / 300 / 28,5 | 50 | Vàng → vàng → đỏ |
| TDS cao | 7,2 / 20 / 5 / 500,01 / 28,5 | 50 | Vàng → vàng → đỏ |
| Nhiệt độ cao | 7,2 / 20 / 5 / 300 / 35,01 | 75 | Vàng → vàng → đỏ |
| Phục hồi | Sau trạng thái đỏ, đưa mọi giá trị về case đầu | 75 | Mẫu kế tiếp về xanh, 0/3, alert 0 |
| Vi phạm ngắt quãng | Hai mẫu DO 2, một mẫu DO 5, rồi DO 2 | 75/50 | Mẫu trong giới hạn cắt chuỗi, lần vi phạm sau bắt đầu 1/3 |

Kiểm tra tự động cũng bao gồm pH thấp, pH đúng 8,5, trần nhập 250, nhập 251 bị chặn ở 250, chuỗi vi phạm kéo dài vẫn giữ 3/3 và cập nhật lý do ngay khi DO thay đổi.

## Evaluation trên 107 dòng CSV

Dữ liệu gốc được lấy từ `du_lieu_nuoc_song_ha_noi.csv` của nhóm. Cột Tình trạng thực tế được dùng làm nhãn đối chiếu. Mỗi dòng được nhập riêng qua trình xử lý ô nhập của mã JavaScript, giữ Manual, reset bộ đếm rồi gọi ba lần đo. Các hàm chạy trong môi trường DOM giả lập để kiểm tra logic. Phép thử này chưa kiểm tra độ chính xác của thiết bị thật hoặc toàn bộ thao tác kéo chuột trong trình duyệt.

| Nhãn CSV | App báo trong giới hạn | App báo vi phạm xác nhận | Tổng |
|---|---:|---:|---:|
| An toàn | 26 | 0 | 26 |
| Ô nhiễm | 0 | 81 | 81 |
| Tổng | 26 | 81 | 107 |

Phiên bản cũ khớp 100/107 dòng (93,5%). Cách 2 khớp 107/107 dòng (100%) trong chính tập này, không sửa số đo hoặc nhãn nguồn. Sáu mẫu độ đục 54,2–72,8 NTU nay được nhận theo ngưỡng 75 khi DO/TDS thỏa điều kiện. Mẫu Tô Lịch tại Đập Thanh Liệt với TDS 600 ppm nay vi phạm giới hạn 500 ppm, khớp nhãn Ô nhiễm đang có.

Hai mẫu độ đục lớn nhất 202,0 và 215,7 NTU được nhập đầy đủ nhờ dải 0–250 NTU. Tất cả dòng thiếu nhiệt độ sử dụng 28,5°C, nên kết quả chưa đánh giá được tác động của nhiệt độ thực tế.

### Độ tin cậy và limitations

- 100% thể hiện mức khớp với nhãn của 107 dòng, với điều kiện kiểm thử nêu trên. Logic được đề xuất sau khi xem chính tập dữ liệu này nên cần thêm tập kiểm chứng độc lập để đánh giá khả năng áp dụng rộng hơn.
- Cần kiểm tra nguồn gốc, phương pháp đo, ngày đo và cơ sở gán nhãn từng dòng. Một số tên và ghi chú trong CSV ghép nối nhiều năm hoặc dùng TDS nền, nên chưa thể coi mọi bộ thông số là một mẫu đồng thời.
- Tài liệu nhóm đề nghị đổi TDS 600 thành 350 và nhãn của mẫu Thanh Liệt. Chưa có nguồn quan trắc xác nhận thay đổi đó. Phép thử ở đây giữ 600 ppm và nhãn Ô nhiễm.
- DO cao và TDS thấp chưa loại trừ hóa chất độc, kim loại, vi khuẩn hoặc nước thải pha loãng. Độ đục cần thêm kiểm chứng để phân biệt bùn, phù sa và tác động xả thải.
- Ngưỡng TDS 500 và bộ điều kiện mở rộng 75/4,2/400 là quy tắc thử nghiệm từ tài liệu nhóm. Nhiệt độ 35 là ngưỡng giữ từ app trước đó. Cần bổ sung căn cứ chuyên môn cho các lựa chọn này.
- Các khoảng pH và DO có tham chiếu đến thông số Mức C trong QCVN 08:2023/BTNMT. Đánh giá đầy đủ theo quy chuẩn còn cần các thông số, cách lấy mẫu và tổng hợp dữ liệu quy định trong văn bản. Mức C được mô tả là chất lượng nước xấu, nên tên nhãn An toàn trong CSV cần được hiểu trong phạm vi bài kiểm thử của nhóm.
- Bộ đếm ba mẫu giảm cảnh báo do vi phạm ngắn, đồng thời trì hoãn cảnh báo xác nhận và không thay thế bộ lọc nhiễu/hiệu chuẩn. Sau một mẫu trong giới hạn, app xóa cảnh báo ngay, chưa có hysteresis hoặc thời gian giữ trạng thái.

### Conclusion

Mô phỏng thực hiện được quy tắc cảm biến-only của nhóm, giải thích nguyên nhân và ngưỡng đang áp dụng, đồng thời tái hiện chuỗi vàng/đỏ và phục hồi. Kết quả 107/107 là bằng chứng cho việc mã thực hiện đúng quy tắc trên dữ liệu đã cho. Bước đánh giá tiếp theo cần tập quan trắc độc lập và so sánh với thiết bị/kiểm nghiệm phù hợp trước khi dùng cảnh báo cho vận hành thực tế.

## Tài liệu và dữ liệu nguồn

- Tài liệu do nhóm cung cấp, **PHÂN LOẠI CÁC NHÓM SÔNG CÓ PHÙ SA.docx**, phần Cách 2.
- [CSV nhóm trên Google Drive](https://drive.google.com/file/d/1vLh75SwMf8Syzmra4Uoh2GtW-W2JhFv6/view). Phép thử dùng dữ liệu gốc đã lưu ngày 16/11/2026, với 107 dòng dữ liệu.
- [QCVN 08:2023/BTNMT — văn bản ký](https://vea.mae.gov.vn/Data/files/2023/03/QCVN%2008%20nuoc%20mat_Signed.pdf), Bảng 2 và các nguyên tắc đánh giá chất lượng nước.
- `Simulation.html`, các hàm `turbidityLimit`, `assessment`, `measure` và `send` là nguồn xác định hành vi của phiên bản này.
