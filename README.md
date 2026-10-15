# LocalPDF Suite — %100 Yerel, Güvenli & Hızlı PDF Platformu

iLovePDF'in tüm temel özelliklerini tersine mühendislikle kendi bilgisayarınızda **%100 yerel (localhost / offline)** çalıştıran, sıfır bulut bağımlılığı ve tam veri gizliliği sunan modern PDF uygulaması.

---

## 🔒 Neden Yerel (Local)?
1. **Sıfır Veri Sızıntısı:** Belgeleriniz (sözleşmeler, kimlik fotokopileri, finansal raporlar) asla harici bir sunucuya yüklenmez.
2. **Virüs & Zararlı Yazılım Koruması:** İnternetteki şüpheli PDF dönüştürme araçlarına veya güvensiz `.exe` dosyalarına ihtiyaç duymazsınız.
3. **Sınırsız & Ücretsiz:** Dosya boyutu sınırı, günlük işlem limiti veya abonelik ücreti yoktur.
4. **Yüksek Hız:** Dosyaları internete yükleyip indirmekle vakit kaybetmezsiniz; yerel C++ tabanlı motorlarla saniyeler içinde işlenir.

---

## 🚀 Özellikler Kataloğu

| Modül | Açıklama | Çekirdek Teknoloji |
| :--- | :--- | :--- |
| **PDF Birleştir (Merge)** | Birden fazla PDF'i dilediğiniz sırayla kayıpsız birleştirir. | `pypdf` |
| **PDF Böl (Split)** | Sayfa aralıklarına veya her sayfayı ayrı dosyalara böler. | `pypdf` |
| **Sayfaları Düzenle & Döndür** | Sayfaları görsel olarak sürükleyip sıralar, 90° döndürür, istenmeyen sayfaları siler. | `PyMuPDF` + `pypdf` |
| **PDF Sıkıştır (Compress)** | Görsel DPI ve akış optimizasyonu ile dosya boyutunu küçültür. | `PyMuPDF` + `Pillow` |
| **PDF'ten Word'e (.docx)** | PDF belgelerini düzenlenebilir Microsoft Word formatına dönüştürür. | `pdf2docx` |
| **Görselden PDF'e** | JPG, PNG, WebP ve BMP görsellerini tek bir PDF belgesine dönüştürür. | `Pillow` |
| **PDF'ten Görsellere** | Sayfaları yüksek çözünürlüklü PNG/JPG resimlere dönüştürüp ZIP olarak sunar. | `PyMuPDF` |
| **PDF'ten Metne / Markdown** | Belgedeki metinleri yapılandırılmış Markdown formatında çıkarır. | `PyMuPDF` |
| **PDF Şifrele (Protect)** | Belgeyi güçlü AES-256 şifreleme algoritmasıyla kilitler. | `pypdf` + `cryptography` |
| **Şifre Kaldır (Unlock)** | Şifresi bilinen belgelerin korumasını kalıcı olarak kaldırır. | `pypdf` |
| **Filigran Ekle (Watermark)** | İstenen açı, renk ve şeffaflıkta vektörel filigran basar. | `ReportLab` + `pypdf` |
| **Sayfa Numarası Ekle** | İstenen konumda (alt/üst, sağ/sol/orta) dinamik sayfa numaraları ekler. | `ReportLab` + `pypdf` |
| **Hassas Bilgi Sansürleme** | TC kimlik, ad-soyad, tel vb. verileri kalıcı olarak PDF'ten kazır (Blackout). | `PyMuPDF Redactions` |
| **PDF Onar (Repair)** | Bozuk veya hasarlı PDF belgelerinin XREF indekslerini yeniden inşa eder. | `PyMuPDF` |

---

## ⚡ Hızlı Başlatma (1-Tık)

### Yöntem 1: Doğrudan Başlatıcı (Önerilen)
Proje dizinindeki **`run.bat`** dosyasına çift tıklayın veya PowerShell üzerinden çalıştırın:
```powershell
.\run.ps1
```
*Gerekli Python ortamını otomatik hazırlar, yerel sunucuyu ayağa kaldırır ve tarayıcınızı `http://127.0.0.1:8000` adresinde açar.*

---

### Yöntem 2: Manuel Çalıştırma
```powershell
# 1. Sanal ortamı aktifleştirin
.\.venv\Scripts\Activate.ps1

# 2. Sunucuyu başlatın
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Tarayıcınızdan **`http://127.0.0.1:8000`** adresine gidin.

---

## 🧪 Otomatik Test Paketi
Tüm çekirdek modüllerin yerel makinenizde hatasız çalıştığını doğrulamak için:
```powershell
.\.venv\Scripts\python.exe backend\test_suite.py
```

---

## 🏗️ Ölçeklenebilirlik Mimarisi (Scalability)
Bu mimari kurumsal veya çok kullanıcılı ihtiyaçlara göre rahatça genişletilebilir:
1. **İşçi Havuzu (Task Queue):** Büyük boyutlu dosyalar için `FastAPI BackgroundTasks` veya `Celery / Redis` kuyruğu kolayca entegre edilebilir.
2. **Docker Desteği:** `Dockerfile` ve `docker-compose.yml` eklenerek yerel ağda (LAN / Intranet) şirket içi servis olarak barındırılabilir.
3. **Headless LibreOffice:** Word/Excel -> PDF dönüşümleri için sisteme kurulu LibreOffice CLI çağrısı yapılarak %100 ofis sadakati sağlanabilir.
