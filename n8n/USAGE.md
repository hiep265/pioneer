# Hướng dẫn sử dụng Pioneer Bot

## Giới thiệu

Pioneer Bot là một bot Telegram cho phép bạn tìm kiếm tin tức và bài viết chuyên gia từ hệ thống Pioneer. Bot này kết nối với API tin tức và chuyên gia để cung cấp thông tin mới nhất và phù hợp nhất dựa trên yêu cầu của bạn.

## Các lệnh có sẵn

### Lệnh cơ bản

- `/start` - Khởi động bot và nhận hướng dẫn sử dụng

### Lệnh tin tức

- `/news` - Hiển thị tin tức hàng đầu
  - Bot sẽ trả về 3 tin tức hàng đầu từ hệ thống
  - Mỗi tin bao gồm tiêu đề, tóm tắt, liên kết và điểm đánh giá

- `/news_keyword [từ khóa]` - Tìm tin tức theo từ khóa
  - Ví dụ: `/news_keyword kinh tế`
  - Bot sẽ trả về các tin tức liên quan đến từ khóa "kinh tế"
  - Kết quả được sắp xếp theo mức độ liên quan

### Lệnh chuyên gia

- `/expert [từ khóa]` - Tìm bài viết chuyên gia theo từ khóa
  - Ví dụ: `/expert chứng khoán`
  - Bot sẽ trả về các bài viết của chuyên gia liên quan đến từ khóa "chứng khoán"
  - Kết quả bao gồm nội dung bài viết, liên kết đến Facebook, số lượt thích, bình luận và điểm đánh giá

- `/expert_content [nội dung]` - Tìm bài viết chuyên gia tương tự với nội dung
  - Ví dụ: `/expert_content The stock market is experiencing significant volatility due to recent economic policies`
  - Bot sẽ dịch nội dung từ tiếng Anh sang tiếng Việt (nếu cần)
  - Sau đó tìm các bài viết chuyên gia có nội dung tương tự
  - Kết quả được sắp xếp theo độ tương đồng với nội dung đã cung cấp

## Ví dụ sử dụng

### Tìm tin tức hàng đầu

```
/news
```

Kết quả:

```
📰 TIN TỨC HÀNG ĐẦU

1. Thị trường chứng khoán Việt Nam tăng điểm mạnh
📝 Thị trường chứng khoán Việt Nam đã tăng điểm mạnh trong phiên giao dịch hôm nay, với VN-Index tăng hơn 15 điểm...
🔗 Đọc thêm
📊 Điểm: 0.85

2. Ngân hàng Nhà nước điều chỉnh lãi suất
📝 Ngân hàng Nhà nước vừa công bố quyết định điều chỉnh lãi suất điều hành, giảm 0.5% đối với lãi suất tái cấp vốn...
🔗 Đọc thêm
📊 Điểm: 0.82

3. Xuất khẩu nông sản đạt kỷ lục mới
📝 Kim ngạch xuất khẩu nông sản Việt Nam đã đạt mức kỷ lục mới trong 6 tháng đầu năm, với tổng giá trị đạt hơn 24 tỷ USD...
🔗 Đọc thêm
📊 Điểm: 0.78
```

### Tìm bài viết chuyên gia theo từ khóa

```
/expert lạm phát
```

Kết quả:

```
👨‍🏫 BÀI ĐĂNG CHUYÊN GIA VỀ "lạm phát"

1. Bài đăng
📝 Lạm phát tại Việt Nam đang có xu hướng giảm trong quý II/2023. Theo số liệu mới nhất từ Tổng cục Thống kê, CPI tháng 6 chỉ tăng 0.2% so với tháng trước và tăng 2.8% so với cùng kỳ năm ngoái...
🔗 Xem trên Facebook
👍 Lượt thích: 245
💬 Bình luận: 37
📊 Điểm: 0.92

2. Bài đăng
📝 Áp lực lạm phát từ giá thực phẩm và năng lượng đang giảm dần, tuy nhiên chúng ta vẫn cần thận trọng với lạm phát cơ bản (core inflation) khi nó vẫn duy trì ở mức cao hơn mục tiêu của Chính phủ...
🔗 Xem trên Facebook
👍 Lượt thích: 189
💬 Bình luận: 28
📊 Điểm: 0.87
```

### Tìm bài viết chuyên gia tương tự với nội dung

```
/expert_content The impact of rising interest rates on Vietnam's real estate market is becoming more pronounced as investors shift their portfolios
```

Kết quả:

```
👨‍🏫 BÀI ĐĂNG CHUYÊN GIA TƯƠNG TỰ VỚI NỘI DUNG

Nội dung gốc: The impact of rising interest rates on Vietnam's real estate market is becoming more pronounced as investors shift their portfolios...

Bản dịch: Tác động của lãi suất tăng đối với thị trường bất động sản Việt Nam đang trở nên rõ rệt hơn khi các nhà đầu tư chuyển đổi danh mục đầu tư của họ...

1. Bài đăng
📝 Thị trường bất động sản đang chịu áp lực lớn từ việc tăng lãi suất. Nhiều nhà đầu tư đã bắt đầu chuyển hướng sang các kênh đầu tư khác như trái phiếu doanh nghiệp và chứng khoán. Điều này dẫn đến thanh khoản của thị trường BĐS giảm mạnh trong quý vừa qua...
🔗 Xem trên Facebook
👍 Lượt thích: 312
💬 Bình luận: 54
📊 Độ tương đồng: 87.65%

2. Bài đăng
📝 Lãi suất tăng cao đang khiến chi phí vay mua nhà tăng theo, người mua nhà để ở cũng dè dặt hơn. Các chủ đầu tư buộc phải điều chỉnh chiến lược, nhiều dự án phải giãn tiến độ hoặc tung ra các chương trình ưu đãi lớn để kích cầu...
🔗 Xem trên Facebook
👍 Lượt thích: 278
💬 Bình luận: 42
📊 Độ tương đồng: 82.31%
```

## Lưu ý

- Bot sẽ trả về kết quả tốt nhất dựa trên dữ liệu hiện có trong hệ thống
- Nếu không tìm thấy kết quả phù hợp, bot sẽ thông báo cho bạn
- Đối với lệnh `/expert_content`, nội dung có thể được cung cấp bằng tiếng Anh hoặc tiếng Việt
- Kết quả được định dạng bằng Markdown, vì vậy các liên kết có thể được nhấp trực tiếp trong Telegram