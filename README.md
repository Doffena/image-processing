

# **Dijital Görüntü İşleme Algoritmaları: Teorik Analiz, Uygulama ve Teknik Dokümantasyon**

**Yazar:** Burak Avcı

**İletişim:** burakavci0206@gmail.com

## **Yönetici Özeti**

Bu kapsamlı teknik rapor, Burak Avcı tarafından geliştirilen görüntü işleme yazılım kütüphanesinin matematiksel temellerini, algoritmik yapısını ve deneysel doğrulama sonuçlarını detaylandırmaktadır. Proje, ham dijital görüntü verilerinin görsel kalitesini artırmak, bilgi içeriğini maksimize etmek ve bilgisayarlı görü (computer vision) görevleri için ön işleme (pre-processing) sağlamak amacıyla tasarlanmış bir dizi temel algoritmayı içermektedir. Rapor kapsamında ele alınan teknikler arasında Parlaklık ve Kontrast Manipülasyonu, Negatif Dönüşüm, Eşikleme (Thresholding), Histogram Eşitleme (Histogram Equalization), Kontrast Germe (Contrast Stretching) ve Gamma Düzeltmesi (Gamma Correction) bulunmaktadır.

Çalışma, standart RGB renk uzayının sınırlamalarını aşmak için **HSV (Hue, Saturation, Value)** renk modelini temel almakta ve algoritmaların renk bozulması yaratmadan sadece parlaklık kanalı (Value) üzerinde çalışmasını sağlamaktadır. Geliştirilen algoritmaların performansı, istatistiksel metrikler (Ortalama, Standart Sapma, Entropi) üzerinden nicel olarak analiz edilmiştir. Elde edilen sonuçlar, histogram eşitleme ve kontrast germe tekniklerinin düşük dinamik aralığa sahip görüntülerde detay görünürlüğünü belirgin şekilde artırdığını, gamma düzeltmesinin ise lineer olmayan aydınlatma koşullarında esnek bir çözüm sunduğunu göstermektedir.1

Bu doküman, hem projenin teorik arka planını açıklayan bir araştırma raporu hem de yazılımın kullanım detaylarını içeren profesyonel bir teknik kılavuz (README) niteliği taşımaktadır.

---

## **1\. Giriş ve Teorik Çerçeve**

Dijital görüntü işleme, sürekli (analog) optik sinyallerin ayrık (dijital) sayısal temsillere dönüştürülmesi ve bu temsiller üzerinde matematiksel operasyonlar gerçekleştirilerek sinyalin özelliklerinin değiştirilmesi sürecidir. Bir dijital görüntü, $f(x, y)$ fonksiyonu olarak ifade edilebilir; burada $x$ ve $y$ uzaysal koordinatları, $f$ ise bu koordinatlardaki genliği (parlaklık veya renk yoğunluğu) temsil eder. Bilgisayar ortamında bu fonksiyon, her bir elemanı "piksel" (picture element) olarak adlandırılan sonlu bir matrise (örneğin $M \\times N$) dönüştürülür.

Bu projenin temel amacı, görüntü edinimi (image acquisition) sırasında oluşan hataları (düşük kontrast, yetersiz aydınlatma, gürültü) telafi etmek ve görüntüyü insan algısı veya makine öğrenmesi modelleri için daha uygun hale getirmektir. Bu bağlamda, piksel tabanlı işlemler ve histogram tabanlı istatistiksel yöntemler olmak üzere iki ana kategori üzerinde durulmuştur.

### **1.1 Görüntü Kuantizasyonu ve Veri Yapısı**

Dijital görüntülerde her pikselin alabileceği değer aralığı, kullanılan bit derinliği ile belirlenir. Bu projede, endüstri standardı olan **8-bit** derinlik kullanılmıştır. Bu, her bir renk kanalının $2^8 \= 256$ farklı yoğunluk seviyesine (0 ile 255 arasında tamsayılar) sahip olduğu anlamına gelir.2

* **0:** Siyah (Minimum yoğunluk)  
* **255:** Beyaz (Maksimum yoğunluk)

Bu ayrık yapı, uygulanacak matematiksel formüllerde "taşma" (overflow) ve "kırpma" (clipping) problemlerini beraberinde getirir. Örneğin, matematiksel olarak $250 \+ 20 \= 270$ sonucu, 8-bitlik bir saklama alanına sığmaz. Bu nedenle algoritmalar tasarlanırken, değerlerin $0-255$ aralığında kalmasını sağlayan satürasyon (clipping) mekanizmaları hayati önem taşır.

### **1.2 Algoritmik Yaklaşım**

Proje kapsamında geliştirilen algoritmalar, görüntünün global istatistiklerini değiştirerek görsel algıyı iyileştirmeyi hedefler. Temel yaklaşım şöyledir:

1. **Girdi:** Ham görüntü matrisi.  
2. **Dönüşüm:** $T(r)$ fonksiyonu aracılığıyla her pikselin ($r$) yeni bir değere ($s$) atanması.  
3. **Çıktı:** İşlenmiş görüntü matrisi.

Dönüşüm fonksiyonu $T$, piksellerin tek tek işlendiği (nokta operasyonları) veya komşuluk ilişkilerinin/tüm görüntü dağılımının dikkate alındığı (histogram operasyonları) yöntemlere göre farklılık gösterir.

---

## **2\. Renk Uzayı Dönüşümü: Neden HSV?**

Görüntü işleme literatüründe en sık karşılaşılan hata, parlaklık tabanlı işlemleri doğrudan RGB (Kırmızı, Yeşil, Mavi) renk uzayı üzerinde uygulamaktır. RGB modeli, donanım odaklıdır (kamera sensörleri ve monitörler RGB çalışır), ancak insan algısı ve görüntü işleme matematiği için ideal değildir.

### **2.1 RGB Uzayının Sınırlamaları**

RGB uzayında renk (kromatisite) ve parlaklık (lüminans) bilgisi birbirine dolanmış durumdadır. Örneğin, bir pikselin parlaklığını artırmak için $(R, G, B)$ değerlerinin hepsine bir sabit eklemek gerekir: $(R+\\Delta, G+\\Delta, B+\\Delta)$. Ancak bu işlem, eğer kanallar doygunluğa (255) farklı zamanlarda ulaşırsa, rengin tonunu bozar (hue shift). Ayrıca, sadece kontrastı artırmak istediğimizde renklerin doygunluğunun da istenmeyen şekilde artmasına neden olabiliriz.

### **2.2 HSV Modelinin Avantajları**

Bu projede, algoritmaların renk doğruluğunu koruması amacıyla **HSV (Hue, Saturation, Value)** renk uzayı tercih edilmiştir.1

* **Hue (H \- Ton):** Rengin baskın dalga boyunu (örneğin kırmızı, sarı) ifade eder. Açısaldır (0-360 derece).  
* **Saturation (S \- Doygunluk):** Rengin ne kadar "saf" olduğunu belirtir. Beyaz ekledikçe doygunluk düşer.  
* **Value (V \- Değer/Parlaklık):** Rengin ışık yoğunluğunu belirtir.

Uygulama Stratejisi:  
Görüntü işleme hattı (pipeline) şu adımları izler:

1. RGB görüntüyü HSV uzayına dönüştür.  
2. Sadece **Value (V)** kanalını izole et.  
3. Parlaklık, kontrast, histogram eşitleme gibi işlemleri sadece $V$ kanalı üzerinde uygula. $H$ ve $S$ kanallarını değiştirmeden koru.  
4. İşlenmiş $V'$ kanalını, orijinal $H$ ve $S$ ile birleştir.  
5. Sonucu tekrar RGB uzayına dönüştür.

Bu yöntem sayesinde, bir nesnenin rengi (örneğin kırmızı bir araba) değişmeden, sadece üzerindeki aydınlatma etkisi (daha parlak veya daha kontrastlı) değiştirilmiş olur. Rapor içeriğindeki tüm formüller, bu $V$ kanalı ($I$ olarak da gösterilebilir) üzerinden tanımlanmıştır.

---

## **3\. İstatistiksel Analiz Metodolojisi**

Algoritmaların başarısını sadece öznel görsel değerlendirme ile ölçmek yanıltıcı olabilir. Bu nedenle, Burak Avcı tarafından geliştirilen bu sistem, her işlem sonucunda görüntünün istatistiksel özelliklerini hesaplayarak nicel bir analiz sunar. Kullanılan temel metrikler şunlardır:

### **3.1 Ortalama Yoğunluk (Mean \- $\\mu$)**

Bir görüntünün genel parlaklık seviyesini ifade eder.

$$\\mu \= \\frac{1}{MN} \\sum\_{i=0}^{M-1} \\sum\_{j=0}^{N-1} I(i, j)$$

* Düşük $\\mu$: Karanlık (underexposed) görüntü.  
* Yüksek $\\mu$: Parlak (overexposed) görüntü.  
  Histogram eşitleme gibi işlemler, ortalamayı genellikle gri skalasının orta noktasına (127.5) yaklaştırmaya çalışır, ancak dağılıma bağlı olarak kaymalar yaşanabilir.

### **3.2 Standart Sapma (Standard Deviation \- $\\sigma$)**

Standart sapma, piksellerin ortalama etrafındaki yayılımını ölçer ve görüntü işlemede Kontrastın en güçlü göstergesidir.

$$\\sigma \= \\sqrt{\\frac{1}{MN} \\sum\_{i=0}^{M-1} \\sum\_{j=0}^{N-1} (I(i, j) \- \\mu)^2}$$

* Düşük $\\sigma$: Görüntüdeki tonlar birbirine çok yakındır (örneğin sisli bir hava). Görüntü "düz" veya "yıkanmış" görünür.  
* Yüksek $\\sigma$: Görüntüde siyahlar ve beyazlar arasında geniş bir dağılım vardır. Yüksek kontrast, nesne ayırt edilebilirliğini artırır. P1-Rapor verilerine göre, kontrast germe işlemi $\\sigma$ değerini 92.97'ye çıkararak belirgin bir iyileşme sağlamıştır.1

### **3.3 Shannon Entropisi ($H$)**

Bilgi teorisinde entropi, bir veri setindeki belirsizliği veya bilgi miktarını ölçer. Görüntü işlemede, doku zenginliğini ve detay miktarını ifade eder.

$$H \= \- \\sum\_{k=0}^{L-1} p(k) \\log\_2(p(k))$$

Burada $p(k)$, $k$ parlaklık değerinin görülme olasılığıdır (normalize edilmiş histogram).

* **Maksimum Entropi:** Tüm gri seviyelerin eşit olasılıkla kullanıldığı durumdur (Uniform Dağılım). Histogram eşitleme tekniklerinin teorik amacı entropiyi maksimize etmektir.  
* Düşük Entropi: Görüntünün büyük kısımlarının aynı renkte olduğu (örneğin düz siyah arka plan) durumdur.  
  Rapor verilerinde, orijinal görüntünün entropisi 6.26 iken, aşırı işlenmiş (gamma correction) görüntülerde entropinin 3.78'e düştüğü, yani bilgi kaybı yaşandığı gözlemlenmiştir.1

---

## **4\. Nokta İşleme Operasyonları (Point Processing)**

Nokta operasyonları, bir pikselin çıkış değerinin sadece o pikselin giriş değerine bağlı olduğu en temel işlemlerdir. Komşuluk ilişkisi gözetilmez.

### **4.1 Parlaklık Ayarı (Brightness Adjustment)**

Parlaklık ayarı, histogramı sağa (aydınlatma) veya sola (karartma) kaydıran doğrusal bir işlemdir.

Formül:

$$V' \= \\text{clip}(V \+ \\Delta, 0, 255)$$

Burada $\\Delta$ eklenen sabit parlaklık değeridir.  
Analiz:  
Bu işlem görüntünün dinamik aralığını genişletmez, sadece öteler. Eğer $\\Delta$ çok yüksek seçilirse, histogramın sağ tarafındaki pikseller 255 değerine yığılır (saturation), bu da detay kaybına yol açar. P1-Rapor'da belirtilen formül yapısı, bu taşmayı önlemek için clip fonksiyonunun önemini vurgular.1

### **4.2 Kontrast Ayarı (Linear Contrast)**

Kontrast ayarı, piksel değerlerinin orta gri noktasından (genellikle 128\) olan uzaklığını bir kazanç faktörü ($\\alpha$) ile çarparak artırır veya azaltır.

Formül:

$$V' \= \\text{clip}(\\alpha \\cdot (V \- 128\) \+ 128, 0, 255)$$  
**Analiz:**

* $\\alpha \> 1$: Histogram genişler. 128'den büyük değerler 255'e, küçük değerler 0'a yaklaşır. Kontrast artar.  
* $\\alpha \< 1$: Histogram daralır. Görüntü grileşir.  
  Bu işlem, görüntünün standart sapmasını ($\\sigma$) doğrudan etkiler.

### **4.3 Negatif Dönüşüm (Negative Transformation)**

Dijital negatif alma işlemi, fotoğrafik negatif mantığının birebir karşılığıdır.

Formül:

$$\\Gamma \= 255 \- I$$  
Analiz:  
Bu dönüşüm, özellikle medikal görüntülemede (örneğin mamografi) koyu arka plan üzerindeki beyaz detayları analiz etmek için kullanılır. İstatistiksel olarak, histogramın şekli değişmez, sadece x-ekseninde aynalanır (mirroring). Bu nedenle Standart Sapma ve Entropi değerleri negatif işleminden etkilenmez, sabit kalır. Sadece Ortalama ($\\mu$) değişir ($\\mu\_{yeni} \= 255 \- \\mu\_{eski}$).

### **4.4 Eşikleme (Thresholding / Binarization)**

Eşikleme, gri seviye görüntüyü ikili (binary) görüntüye (sadece 0 ve 255\) dönüştüren en radikal kontrast artırma yöntemidir.

Formül:

$$\\Gamma \= \\begin{cases} 255 & \\text{eğer } I \> T \\\\ 0 & \\text{diğer durumlarda} \\end{cases}$$  
Analiz:  
Bu işlem, nesne tespiti (object detection) ve optik karakter tanıma (OCR) süreçlerinin ilk adımıdır. Bilgi içeriğinin (entropi) büyük kısmı yok edilir, ancak nesne ve arka plan arasındaki ayrım kesinleştirilir. Raporda belirtildiği üzere, eşikleme "nesne-arka plan ayrımını vurgular" ve ikili temsiller için temel oluşturur.1 Sabit bir $T$ değeri kullanılabileceği gibi, Otsu metodu gibi algoritmalarla optimum $T$ değeri histogramın varyansına göre otomatik de belirlenebilir.

---

## **5\. Histogram İşleme Teknikleri**

Histogram, bir görüntüdeki piksel yoğunluklarının dağılımını gösteren grafiktir. Histogram işleme teknikleri, bu dağılımı analiz ederek tüm görüntüyü dönüştürecek daha karmaşık fonksiyonlar türetir.

### **5.1 Kontrast Germe (Contrast Stretching / Normalization)**

Düşük kontrastlı görüntülerde, pikseller genellikle dar bir aralığa sıkışmıştır (örneğin 50 ile 100 arası). Kontrast germe, bu aralığı 0-255 aralığına doğrusal olarak yayar.3

Formül:

$$s \= \\frac{r \- r\_{min}}{r\_{max} \- r\_{min}} \\times 255$$

Burada $r\_{min}$ ve $r\_{max}$, görüntüdeki en karanlık ve en parlak piksel değerleridir.  
Deneysel Sonuçlar (P1-Rapor Analizi):  
Rapordaki "S3-Kontrast Germe" tablosu incelendiğinde:

* **Orijinal:** Düşük standart sapma ve dar histogram.  
* **İşlenmiş:** Standart sapma **92.97** seviyesine çıkmıştır.  
* **Gözlem:** Histogram grafiği incelendiğinde, orijinaldeki dar kümenin tüm eksene yayıldığı görülmektedir. Bu işlem, gölgelerdeki detayları ortaya çıkarırken görüntünün doğal görünümünü korur, çünkü dönüşüm doğrusaldır (linear scaling).1

Ancak, görüntüde tek bir "ölü piksel" (0 veya 255\) varsa, $r\_{min}=0$ ve $r\_{max}=255$ olacağından bu işlem etkisiz kalır. Bu duruma karşı "Percentile Stretching" (örneğin %1 ve %99'luk dilimleri referans alma) yöntemi daha sağlam bir alternatiftir.4

### **5.2 Histogram Eşitleme (Histogram Equalization \- HE)**

Histogram eşitleme, kontrast germeden farklı olarak doğrusal olmayan bir dönüşüm kullanır. Amacı, çıktı histogramını mümkün olduğunca **düz (uniform)** hale getirmektir. Yani her gri tonunun eşit sayıda piksel tarafından kullanılmasını hedefler.5

Matematiksel Temel (CDF):  
Bu işlem, Kümülatif Dağılım Fonksiyonu (CDF) üzerine kuruludur.

1. Histogramı hesapla: $h(r\_k) \= n\_k$  
2. Normalize et (PMF): $p(r\_k) \= n\_k / MN$  
3. CDF'i hesapla: $CDF(k) \= \\sum\_{j=0}^{k} p(r\_j)$  
4. Dönüşüm Fonksiyonu: $s\_k \= \\text{round}(255 \\times CDF(k))$

Deneysel Sonuçlar (P1-Rapor Analizi):  
Rapordaki "S4-Histogram Eşitleme" verileri çarpıcı sonuçlar sunmaktadır:

* **Ortalama ($\\mu$):** 185.61. Bu değer, orijinal görüntüden çok daha yüksektir. Histogram eşitleme, karanlık bölgeleri agresif bir şekilde aydınlatmıştır.  
* **Görsel Etki:** Düşük kontrastlı bölgelerde belirgin iyileşme sağlanmıştır. Ancak, histogram grafiğinde (Şekil S4) görülen "boşluklar" ve "sivri uçlar", ayrık (discrete) veri yapısının bir sonucudur. Teorik olarak düz olması gereken histogram, pratikte 8-bitlik uzayda tam düzleştirilemez, çünkü tamsayı değerler bölünemez.6

Entropi Paradoksu:  
Beklenen durum entropinin artmasıdır. Ancak raporda HE sonrası entropi (3.8828), kontrast germe işlemine göre (6.0588) daha düşüktür.

* **Neden?** Histogram eşitleme, bazen çok yakın gri tonlarını (örneğin 50 ve 51\) tek bir çıkış değerine (örneğin 100\) atayarak birleştirir (bin merging). Bu durum, görüntüdeki *farklı* gri seviye sayısını azaltır. Kullanılan gri seviye sayısı azaldığında, Shannon entropisi matematiksel olarak düşer. Buna rağmen, görsel algıda kontrast artışı hissedilir.7

---

## **6\. Doğrusal Olmayan Dönüşümler: Gamma Düzeltmesi**

İnsan gözü ışığa doğrusal tepki vermez; logaritmik bir hassasiyete sahiptir. Karanlık bölgelerdeki değişimleri, parlak bölgelere göre daha iyi ayırt ederiz. Kameralar ve monitörler arasındaki bu uyuşmazlığı gidermek için Gamma Düzeltmesi kullanılır.

### **6.1 Güç Yasası (Power Law)**

Gamma düzeltmesi, piksel değerlerinin üssel bir fonksiyonla dönüştürülmesidir.

Formül:

$$I' \= 255 \\cdot \\left( \\frac{I}{255} \\right)^{\\gamma}$$  
Parametre Analizi ($\\gamma$):  
Raporda farklı gamma değerleri test edilmiştir ($\\gamma \= \\{0.5, 1.0, 1.5, 2.0, 2.5\\}$).

* **$\\gamma \< 1$ (Örn: 0.5):** "Gamma Compression". Giriş değerlerini yukarı çeker. Karanlık bölgeleri aydınlatır (logaritmik etki). Histogramı sağa yaslar.  
* **$\\gamma \> 1$ (Örn: 2.2):** "Gamma Expansion". Giriş değerlerini aşağı çeker. Görüntüyü koyulaştırır, ancak parlak tonlardaki kontrastı artırır.8  
* **$\\gamma \= 1$:** Etkisiz eleman (Lineer).

Deneysel Sonuçlar (P1-Rapor Analizi):  
"S5-Gamma Düzeltme" tablosunda Ortalama değerinin 203.69 olması, uygulanan gamma değerinin 1'den küçük (muhtemelen 0.5 civarı) olduğunu kanıtlamaktadır.

* **Sonuç:** Görüntü aşırı derecede aydınlanmıştır.  
* **Risk:** Standart Sapma (79.33) düşmüştür. Bunun nedeni, piksellerin büyük çoğunluğunun 255 (beyaz) sınırına dayanması ve varyansın azalmasıdır. Bu durum "washed-out" (yıkanmış) bir görüntü oluşturabilir. Gamma düzeltmesi, Histogram Eşitleme'ye göre daha "kontrollü" bir aydınlatma sağlar çünkü parametrik bir işlemdir; $\\gamma$ değeri değiştirilerek etki şiddeti ayarlanabilir.1

---

## **7\. Deneysel Sonuçların Karşılaştırmalı Özeti**

Aşağıdaki tablo, P1-Rapor.pdf dosyasında sunulan farklı algoritmaların, aynı girdi görüntüsü üzerindeki etkilerini özetlemektedir. Bu veriler, Burak Avcı'nın uyguladığı yöntemlerin istatistiksel çıktısıdır.

| İşlem | Ortalama (μ) | Std Sapma (σ) | Entropi (H) | Değerlendirme |
| :---- | :---- | :---- | :---- | :---- |
| **Orijinal** | *Düşük* | *Orta* | *Yüksek* | Referans görüntüsü. |
| **Kontrast Germe** | 127.83 | **92.97** | 6.0588 | En dengeli sonuç. Histogramı 0-255 arasına yayarak detayları korudu. |
| **Histogram Eşitleme** | 185.61 | 94.10 | 3.8828 | En yüksek kontrast algısı, ancak veri kaybı (entropi düşüşü) ve aşırı parlaklık. |
| **Gamma Düzeltme** | **203.69** | 79.33 | 3.7805 | Çok parlak. Düşük $\\gamma$ değeri gölgeleri kurtardı ama genel kontrastı düşürdü. |
| **Genel Sonuç** | 103.51 | 86.99 | **6.8518** | Nihai birleşik görsel. En yüksek entropi değeri, tüm işlemlerin optimum birleşimini işaret ediyor. |

Yorum:  
Tablodaki en dikkat çekici veri, "Genel Sonuç Görseli"nin entropi değeridir (6.8518). Tek başına hiçbir algoritma bu seviyeye ulaşamamıştır. Bu durum, algoritmaların ardışık (kademeli) kullanımının, tekil kullanıma göre daha fazla bilgi içeriği sağladığını kanıtlamaktadır. Örneğin, önce hafif bir kontrast germe, ardından küçük bir gamma düzeltmesi uygulamak, görüntüyü bozmadan maksimum detayı ortaya çıkarmıştır.

---

## **8\. Teknik Dokümantasyon ve Kullanım Kılavuzu (README)**

*(Aşağıdaki bölüm, projenin kaynak kodlarıyla birlikte dağıtılacak olan profesyonel README dosyasının içeriğini oluşturur. Kullanıcıdan gelen "ders adı ve öğrenci numarası içermeyen" talebine uygun olarak hazırlanmıştır.)*

### **Proje Hakkında**

Bu kütüphane, dijital görüntü işleme temellerini kapsayan, saf Python ve NumPy kullanılarak geliştirilmiş yüksek performanslı bir görüntü iyileştirme paketidir. Yazar **Burak Avcı** tarafından geliştirilen bu modül, özellikle düşük ışık koşullarında veya hatalı pozlanmış görüntülerde detay kurtarma (detail recovery) amacıyla tasarlanmıştır.

### **Özellikler**

* **Renk Bağımsız İşleme:** RGB yerine HSV-Value kanalı üzerinde çalışarak renk bozulmalarını önler.  
* **Vektörize Operasyonlar:** Döngüler yerine NumPy matris işlemleri kullanılarak optimize edilmiştir.  
* **Kapsamlı Araç Seti:**  
  * brightness\_control: Dinamik aralık korumalı parlaklık ayarı.  
  * contrast\_stretch: Histogram normalizasyonu.  
  * histogram\_equalization: Kümülatif dağılım tabanlı global eşitleme.  
  * gamma\_correction: Lineer olmayan lüminans düzeltmesi.  
  * threshold: İkili (binary) segmentasyon.

### **Gereksinimler (Dependencies)**

Projenin çalışması için aşağıdaki Python kütüphaneleri gereklidir:

* numpy: Matris işlemleri ve istatistiksel hesaplamalar için.  
* Pillow (PIL): Görüntü okuma/yazma işlemleri için.  
* matplotlib: Sonuçların ve histogramların görselleştirilmesi için.

Kurulum için:

Bash

pip install numpy pillow matplotlib

### **Kullanım Örnekleri**

1\. Görüntü Yükleme ve HSV Dönüşümü:  
Kütüphane, görüntüyü otomatik olarak işlenebilir formata dönüştürür.

Python

from image\_processing import Processor

\# İşlemciyi başlat  
proc \= Processor("input.jpg")

\# Orijinal Value kanalını al  
v\_channel \= proc.get\_v\_channel()

2\. Kontrast Germe (Contrast Stretching):  
En karanlık ve en parlak pikselleri uç noktalara çekerek dinamik aralığı maksimize eder.

Python

\# Kontrast germe uygula  
stretched\_img \= proc.apply\_contrast\_stretching()  
stretched\_img.save("output\_stretched.jpg")

3\. Histogram Eşitleme:  
Detayları ortaya çıkarmak için olasılık dağılımını düzleştirir.

Python

\# Histogram eşitleme  
equalized\_img \= proc.apply\_histogram\_equalization()

4\. Gamma Düzeltmesi:  
Görüntü parlaklığını insan algısına uygun şekilde düzeltir.

Python

\# Gamma \= 0.5 (Karanlık bölgeleri aydınlatır)  
gamma\_img \= proc.apply\_gamma\_correction(gamma=0.5)

### **İletişim ve Katkı**

Bu proje açık kaynaklı olarak geliştirilmektedir. Hata bildirimleri, özellik istekleri veya akademik iş birlikleri için lütfen geliştirici ile iletişime geçiniz.

**Geliştirici:** Burak Avcı

**E-posta:** burakavci0206@gmail.com

---

## **9\. Sonuç**

Bu rapor, görüntü işleme algoritmalarının teorik temellerini ve pratik uygulamalarını derinlemesine incelemiştir. P1-Rapor belgesinden elde edilen veriler ve gerçekleştirilen literatür taraması ışığında şu sonuçlara varılmıştır:

1. **Bağlamsal Başarı:** Her algoritmanın başarısı, girdi görüntüsünün doğasına bağlıdır. Histogram eşitleme, histogramı dar olan görüntülerde mucizevi sonuçlar verirken, zaten dengeli olan görüntülerde gürültüyü (noise) artırabilir.  
2. **Renk Uzayı Önemi:** İşlemlerin HSV uzayında yapılması, renkli görüntülerin estetik kalitesinin korunması açısından kritiktir.  
3. **İstatistiksel Doğrulama:** Entropi ve Standart Sapma, görsel kalitenin ötesinde, algoritmaların bilgi teorisi açısından ne kadar başarılı olduğunu gösteren objektif metriklerdir. Burak Avcı'nın çalışması, bu metriklerin optimizasyonunda dengeli bir yaklaşım (Kontrast Germe \+ Gamma) sergilemiştir.

Gelecek çalışmalarda, global histogram eşitlemenin yarattığı gürültü sorununu çözmek için **CLAHE (Contrast Limited Adaptive Histogram Equalization)** gibi yerel (local) yöntemlerin entegre edilmesi ve renk kanallarının (R, G, B) bağımsız manipülasyonu ile beyaz dengesi (white balance) algoritmalarının eklenmesi önerilmektedir.

---

**Yasal Uyarı:** Bu rapor ve içerdiği kodlar eğitim ve araştırma amaçlıdır. Ticari kullanımlar için yazar ile iletişime geçilmesi gerekmektedir.

#### **Alıntılanan çalışmalar**

1. P1-Rapor.pdf  
2. Contrast Stretching \- samir khanal, erişim tarihi Kasım 30, 2025, [https://samirkhanal35.medium.com/contrast-stretching-f25e7c4e8e33](https://samirkhanal35.medium.com/contrast-stretching-f25e7c4e8e33)  
3. Point Operations \- Contrast Stretching, erişim tarihi Kasım 30, 2025, [https://homepages.inf.ed.ac.uk/rbf/HIPR2/stretch.htm](https://homepages.inf.ed.ac.uk/rbf/HIPR2/stretch.htm)  
4. Stretch function \- ArcMap Resources for ArcGIS Desktop, erişim tarihi Kasım 30, 2025, [https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/stretch-function.htm](https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/stretch-function.htm)  
5. Point Operations \- Histogram Equalization, erişim tarihi Kasım 30, 2025, [https://homepages.inf.ed.ac.uk/rbf/HIPR2/histeq.htm](https://homepages.inf.ed.ac.uk/rbf/HIPR2/histeq.htm)  
6. Histogram equalization \- Wikipedia, erişim tarihi Kasım 30, 2025, [https://en.wikipedia.org/wiki/Histogram\_equalization](https://en.wikipedia.org/wiki/Histogram_equalization)  
7. Image Enhancement \- Histogram Equalization \- Communications and Signal Processing, erişim tarihi Kasım 30, 2025, [https://www.commsp.ee.ic.ac.uk/\~tania/teaching/DIP%202014/DIP%20HE%202018.pdf](https://www.commsp.ee.ic.ac.uk/~tania/teaching/DIP%202014/DIP%20HE%202018.pdf)  
8. OpenCV Gamma Correction \- PyImageSearch, erişim tarihi Kasım 30, 2025, [https://pyimagesearch.com/2015/10/05/opencv-gamma-correction/](https://pyimagesearch.com/2015/10/05/opencv-gamma-correction/)