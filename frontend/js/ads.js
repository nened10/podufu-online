/**
 * Pödüfü.online — Smart Device-Adaptive Ad & Sponsor Manager
 * Detects visitor brand/device (iPhone, Samsung, Xiaomi, Windows, Mac, etc.)
 * and renders high-converting native sponsor units or Google AdSense.
 */

const AD_CONFIG = {
  useAdSense: false, // Set to true when AdSense is approved
  adSenseClient: "ca-pub-XXXXXXXXXXXXXXXX",
  slots: {
    topBanner: "1234567890",
    waitingCard: "2345678901",
    resultCard: "3456789012"
  }
};

// 1. Device & Brand Detection Engine
function detectUserDevice() {
  const ua = navigator.userAgent || "";
  const platform = navigator.platform || "";
  
  let brand = "Genel";
  let model = "Cihaz";
  let os = "Bilinmeyen OS";
  let category = "desktop";

  // Category detection
  if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/i.test(ua)) {
    category = "mobile";
  } else if (/Tablet|iPad/i.test(ua) || (platform === 'MacIntel' && navigator.maxTouchPoints > 1)) {
    category = "tablet";
  }

  // OS & Brand Detection
  if (/iPhone/i.test(ua)) {
    brand = "Apple";
    model = "iPhone";
    os = "iOS";
    category = "mobile";
  } else if (/iPad/i.test(ua) || (platform === 'MacIntel' && navigator.maxTouchPoints > 1)) {
    brand = "Apple";
    model = "iPad";
    os = "iPadOS";
    category = "tablet";
  } else if (/Macintosh|Mac OS X/i.test(ua)) {
    brand = "Apple";
    model = "Mac";
    os = "macOS";
    category = "desktop";
  } else if (/Samsung|SM-[A-Z0-9]+/i.test(ua)) {
    brand = "Samsung";
    const smMatch = ua.match(/SM-([A-Z0-9]+)/i);
    model = smMatch ? `Galaxy (${smMatch[1]})` : "Galaxy";
    os = "Android";
    category = "mobile";
  } else if (/Redmi|POCO|Mi [0-9]|Xiaomi/i.test(ua)) {
    brand = "Xiaomi";
    model = /Redmi/i.test(ua) ? "Redmi" : (/POCO/i.test(ua) ? "POCO" : "Xiaomi");
    os = "Android / HyperOS";
    category = "mobile";
  } else if (/Huawei|HONOR/i.test(ua)) {
    brand = "Huawei";
    model = "Huawei / Honor";
    os = "EMUI / HarmonyOS";
    category = "mobile";
  } else if (/Pixel/i.test(ua)) {
    brand = "Google";
    model = "Google Pixel";
    os = "Android";
    category = "mobile";
  } else if (/Android/i.test(ua)) {
    brand = "Android";
    model = "Android Cihaz";
    os = "Android";
    category = "mobile";
  } else if (/Windows NT/i.test(ua)) {
    brand = "Windows";
    model = "PC";
    os = "Windows";
    category = "desktop";
  } else if (/Linux/i.test(ua)) {
    brand = "Linux";
    model = "Workstation";
    os = "Linux";
    category = "desktop";
  }

  return { category, brand, model, os };
}

// 2. Targeted Ad Copy Generator
function getTargetedAdContent(device, slotType) {
  const brand = device.brand;
  
  if (brand === "Apple" && device.category === "mobile") {
    return {
      badge: "iPhone & iPad İçin Önerilen",
      title: "📱 iPhone Belgeleriniz İçin Hızlı Bulut & Arşivleme",
      description: "iCloud ve yerel dosyalarınızı tek tıkla dönüştürün, sıkıştırın ve güvenle saklayın.",
      cta: "Uygulamayı Keşfet",
      link: "https://meadsocial.com",
      accent: "#5B5CE5"
    };
  } else if (brand === "Samsung") {
    return {
      badge: "Samsung Galaxy Özel",
      title: `⚡ Samsung ${device.model} Kullanıcıları İçin Özel Araçlar`,
      description: "Galaxy cihazınızda büyük PDF'leri anında hafifletin ve güvenli bağlantıyla paylaşın.",
      cta: "Detayları İncele",
      link: "https://meadsocial.com",
      accent: "#2563EB"
    };
  } else if (brand === "Xiaomi") {
    return {
      badge: "Xiaomi / Redmi Uyumlu",
      title: `🚀 ${device.model} İçin Yüksek Performanslı Belge Yöneticisi`,
      description: "Dosya Yöneticisi ile tam uyumlu, minimum hafıza harcayan hızlı mikro araçlar.",
      cta: "Hemen Başla",
      link: "https://meadsocial.com",
      accent: "#EA580C"
    };
  } else if (brand === "Windows") {
    return {
      badge: "Windows Masaüstü",
      title: "💻 Windows İçin Gelişmiş PDF & Office Çözümleri",
      description: "Büyük tabloları, sözleşmeleri ve sunumları masaüstünüzde 10 kat daha hızlı işleyin.",
      cta: "Ücretsiz İncele",
      link: "https://meadsocial.com",
      accent: "#5B5CE5"
    };
  } else if (brand === "Apple" && device.category === "desktop") {
    return {
      badge: "macOS Uyumlu",
      title: "🍏 Mac İçin Akıcı & Gizlilik Odaklı Verimlilik",
      description: "Sıfır izleme, anında dönüştürme. MeadSocial ekosistemiyle iş akışınızı hızlandırın.",
      cta: "Keşfedin",
      link: "https://meadsocial.com",
      accent: "#4F46E5"
    };
  }

  // Default Fallback
  return {
    badge: "MeadSocial Sponsorlu",
    title: "⚡ Hızlı, Güvenli ve Tamamen Ücretsiz Dijital Araçlar",
    description: "Belge boyutlarını küçültün, formatları dönüştürün ve işlerinizi kolaylaştırın.",
    cta: "Topluluğa Katıl",
    link: "https://meadsocial.com",
    accent: "#5B5CE5"
  };
}

// 3. Render Ad Card HTML
function renderNativeAdCard(content, slotId, extraClass = "") {
  return `
    <div class="native-ad-card ${extraClass}">
      <div class="native-ad-header">
        <span class="native-ad-badge" style="background: ${content.accent}15; color: ${content.accent};">
          ${content.badge}
        </span>
        <span class="native-ad-sponsor-label">Sponsorlu</span>
      </div>
      <div class="native-ad-body">
        <h4 class="native-ad-title">${content.title}</h4>
        <p class="native-ad-desc">${content.description}</p>
      </div>
      <div class="native-ad-footer">
        <a href="${content.link}" target="_blank" rel="noopener noreferrer" class="native-ad-cta-btn" style="background: ${content.accent};">
          ${content.cta}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </a>
      </div>
    </div>
  `;
}

// 4. Initialize Ads Across Page
function initAds() {
  const device = detectUserDevice();

  // Top Banner Slot
  const topSlot = document.getElementById("ad-top-slot");
  if (topSlot) {
    if (AD_CONFIG.useAdSense) {
      topSlot.innerHTML = `
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="${AD_CONFIG.adSenseClient}"
             data-ad-slot="${AD_CONFIG.slots.topBanner}"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
      `;
      try { (adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
    } else {
      const content = getTargetedAdContent(device, "top");
      topSlot.innerHTML = renderNativeAdCard(content, "top", "native-ad-banner");
    }
  }

  // Result Screen Slot
  const resultSlot = document.getElementById("ad-result-slot");
  if (resultSlot) {
    const content = getTargetedAdContent(device, "result");
    resultSlot.innerHTML = renderNativeAdCard(content, "result", "native-ad-compact");
  }
}

// In-Modal Waiting Screen Ad (Rendered dynamically when file starts uploading)
function renderWaitingAd() {
  const waitingSlot = document.getElementById("ad-waiting-slot");
  if (!waitingSlot) return;
  
  const device = detectUserDevice();
  const content = getTargetedAdContent(device, "waiting");
  waitingSlot.innerHTML = renderNativeAdCard(content, "waiting", "native-ad-waiting");
}

window.PödufuAds = {
  initAds,
  renderWaitingAd,
  detectUserDevice
};

document.addEventListener("DOMContentLoaded", initAds);
