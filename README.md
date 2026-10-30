# docx-to-chinese-vocab

Agent skill biến **các từ được gạch chân trong file Word (.docx)** thành **bảng từ vựng tiếng Trung dạng `.tsv`**, sẵn sàng nhập vào Anki hoặc Google Sheets / Excel.

Skill này là một pipeline 2 bước, gộp từ hai skill:

| Bước | Skill gốc | Việc làm |
|---|---|---|
| 1 | `docx-underlined-words` | Lọc các từ/cụm từ gạch chân trong .docx ra 1 cột, bỏ trùng |
| 2 | [`chinese-vocab-tsv`](https://github.com/vibeailabs-tech/chinese-vocab-tsv) | Lấy danh sách đó làm bảng từ vựng 7 cột |

```
bai_doc.docx ──(bước 1)──> bai_doc_gach_chan.txt ──(bước 2)──> output/2026_10_30_01.tsv
```

## Cài đặt

### Hermes Agent

```bash
hermes skills install vibeailabs-tech/docx-to-chinese-vocab/skills/docx-to-chinese-vocab
```

Kiểm tra:

```bash
hermes skills list | grep docx-to-chinese-vocab
```

Skill được nạp từ phiên (session) mới, hoặc dùng `/skills install --now ...` trong phiên đang chạy.
Cập nhật bản mới: `hermes skills update docx-to-chinese-vocab`. Gỡ: `hermes skills uninstall docx-to-chinese-vocab`.

### Devin / Claude Code / agent khác dùng chuẩn SKILL.md

Copy thư mục `skills/docx-to-chinese-vocab` vào thư mục skills của agent:

```bash
git clone https://github.com/vibeailabs-tech/docx-to-chinese-vocab /tmp/docx-to-chinese-vocab

# Devin (global)
cp -R /tmp/docx-to-chinese-vocab/skills/docx-to-chinese-vocab ~/.config/devin/skills/
# Claude Code (global)
cp -R /tmp/docx-to-chinese-vocab/skills/docx-to-chinese-vocab ~/.claude/skills/
```

## Yêu cầu

- `python3` (chỉ dùng thư viện chuẩn, không cần `pip install`).
- File đầu vào phải là `.docx`. File `.doc` cũ cần chuyển trước:
  - macOS: `textutil -convert docx bai_doc.doc`
  - LibreOffice: `soffice --headless --convert-to docx bai_doc.doc`

## Cách dùng

Đưa đường dẫn file cho agent và nói một trong các câu như:

- "Chạy docx-to-chinese-vocab với file `~/Desktop/bai_doc.docx`"
- "Lọc từ gạch chân trong file này rồi làm bảng từ vựng"
- "docx sang tsv: `/path/to/bai_doc.docx`"

Agent sẽ:

1. Chạy `scripts/docx_underlined_words.py` để lọc từ gạch chân, lưu `bai_doc_gach_chan.txt` cạnh file .docx.
2. Dùng đúng danh sách đó (giữ thứ tự, không thêm/bớt) để tạo bảng từ vựng theo `references/chinese-vocab-tsv.md`.
3. Ghi file `.tsv` vào thư mục `output/` cạnh file .docx và kiểm tra mỗi dòng đủ 7 cột.
4. Trả lời số từ, đường dẫn file `.txt`, đường dẫn file `.tsv` và kết quả kiểm tra.

Chỉ chạy riêng bước 1 (không cần agent):

```bash
python3 skills/docx-to-chinese-vocab/scripts/docx_underlined_words.py bai_doc.docx
python3 skills/docx-to-chinese-vocab/scripts/docx_underlined_words.py bai_doc.docx -o tu_vung.txt
```

## Kết quả

### Bước 1: `<tên>_gach_chan.txt`

Mỗi dòng một từ/cụm từ. Quy tắc:

- Bỏ trùng, giữ lần xuất hiện đầu tiên (không phân biệt hoa/thường).
- Các đoạn gạch chân **liền nhau** (không có chữ nào chen giữa) được gộp thành một cụm.
- Bỏ dấu câu và khoảng trắng thừa ở hai đầu.
- Nhận cả gạch chân trực tiếp lẫn gạch chân qua character style của Word.

### Bước 2: `output/YYYY_MM_DD_STT.tsv`

- Tên file theo ngày đọc + số thứ tự trong ngày (`2026_10_30_01.tsv`, `2026_10_30_02.tsv`, ...), không bao giờ ghi đè file cũ.
- Phân tách bằng tab, có dòng tiêu đề, đúng 7 cột:

| Vocabulary | Pronunciation | English | Vietnamese | Example | Sentence Pinyin | Sentence Translation |
|---|---|---|---|---|---|---|
| 喜欢 | xǐhuan | to like | thích | 我很喜欢喝茶。 | Wǒ hěn xǐhuan hē chá. | I really like drinking tea. |

Muốn đổi thư mục/tên file đầu ra hoặc dùng chữ phồn thể, chỉ cần nói với agent khi yêu cầu.

### Nhập vào Anki

File → Import → chọn file `.tsv` → Field separator: **Tab** → map 7 cột vào các field của note type. Dòng đầu là tiêu đề: bỏ qua hoặc xoá nó nếu Anki nhập thành một thẻ.

## Cấu trúc repo

```
skills/docx-to-chinese-vocab/
├── SKILL.md                          # hướng dẫn pipeline cho agent
├── scripts/docx_underlined_words.py  # bước 1: lọc từ gạch chân
└── references/chinese-vocab-tsv.md   # bước 2: quy tắc bảng từ vựng 7 cột
```

## Lưu ý

- Bước 1 là script nên kết quả cố định. Bước 2 do mô hình AI viết (pinyin, nghĩa, câu ví dụ), nên hãy xem lại trước khi học.
- Nếu file không có từ nào gạch chân, agent dừng lại và báo, không tự bịa từ.
- Từ gạch chân trong header/footer, footnote/endnote, comment không được lọc (script chỉ đọc phần thân `word/document.xml`).
