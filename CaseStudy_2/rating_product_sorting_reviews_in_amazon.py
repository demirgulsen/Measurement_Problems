###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı


###################################################
# GÖREV 1: Average Rating'i Güncel Yorumlara Göre Hesaplayınız ve Var Olan Average Rating ile Kıyaslayınız.
###################################################

# Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır.
# Bu görevde amacımız verilen puanları tarihe göre ağırlıklandırarak değerlendirmek.
# İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.

import matplotlib.pyplot as plt
import pandas as pd
import math
import scipy.stats as st

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', 10)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

###################################################
# Adım 1: Veri Setini Okutunuz ve Ürünün Ortalama Puanını Hesaplayınız.
###################################################
df = pd.read_csv("Github_Measurement_Problems/CaseStudy_2/dataset/amazon_review.csv")
df.head()
df.shape
df.info()

df['overall'].mean()
###################################################
# Adım 2: Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
###################################################
# Kullanıcı trendine göre bir skor hesaplandı.
df.loc[df['day_diff'] <= df['day_diff'].quantile(0.25), 'overall'].mean()   # 4.69579
df.loc[(df['day_diff'] > df['day_diff'].quantile(0.25)) & (df['day_diff'] <= df['day_diff'].quantile(0.50)), 'overall'].mean()  # 4.63614
df.loc[(df['day_diff'] > df['day_diff'].quantile(0.50)) & (df['day_diff'] <= df['day_diff'].quantile(0.75)), 'overall'].mean()  # 4.57166
df.loc[(df['day_diff'] > df['day_diff'].quantile(0.75)), 'overall'].mean()  # 4.44625


def time_based_weighted_average(df, w1=28, w2=26, w3=24, w4=22):
    return df.loc[df['day_diff'] <= df['day_diff'].quantile(0.25), 'overall'].mean() * w1 / 100 + \
           df.loc[(df['day_diff'] > df['day_diff'].quantile(0.25)) & (df['day_diff'] <= df['day_diff'].quantile(0.50)), 'overall'].mean() * w2 / 100 + \
           df.loc[(df['day_diff'] > df['day_diff'].quantile(0.50)) & (df['day_diff'] <= df['day_diff'].quantile(0.75)), 'overall'].mean() * w3 / 100 + \
           df.loc[(df['day_diff'] > df['day_diff'].quantile(0.75)), 'overall'].mean() * w4 / 100


time_based_weighted_average(df)
# Elde edilen sonuç : 4.595593165128118
df['overall'].mean()
# Elde edilen sonuç : 4.587589013224822

###################################################
# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirleyiniz.
###################################################
###################################################
# Adım 1. helpful_no Değişkenini Üretiniz
###################################################
# Not:
# total_vote bir yoruma verilen toplam up-down(oy) sayısıdır.
# up, helpful demektir.
# veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.
# Toplam oy sayısından (total_vote) yararlı oy sayısı (helpful_yes) çıkarılarak yararlı bulunmayan oy sayılarını (helpful_no) bulunuz.

df['helpful_no'] = df['total_vote'] - df['helpful_yes']
###################################################
# Adım 2. score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Ekleyiniz
###################################################
# score_pos_neg_diff, score_average_rating ve wilson_lower_bound skorlarını hesaplayabilmek için score_pos_neg_diff,
# score_average_rating ve wilson_lower_bound fonksiyonlarını tanımlayınız.
# score_pos_neg_diff'a göre skorlar oluşturunuz. Ardından; df içerisinde score_pos_neg_diff ismiyle kaydediniz.
# score_average_rating'a göre skorlar oluşturunuz. Ardından; df içerisinde score_average_rating ismiyle kaydediniz.
# wilson_lower_bound'a göre skorlar oluşturunuz. Ardından; df içerisinde wilson_lower_bound ismiyle kaydediniz.

def score_up_down_diff(up, down):
    return up-down

def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up + down)

def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df['score_pos_neg_diff'] = df.apply(lambda x: score_up_down_diff(x['helpful_yes'], x['helpful_no']), axis=1)
df['score_average_rating'] = df.apply(lambda x: score_average_rating(x['helpful_yes'], x['helpful_no']), axis=1)
df['wilson_lower_bound'] = df.apply(lambda x: wilson_lower_bound(x['helpful_yes'], x['helpful_no']), axis=1)

##################################################
# Adım 3. 20 Yorumu Belirleyiniz ve Sonuçları Yorumlayınız.
###################################################
# wilson_lower_bound'a göre ilk 20 yorumu belirleyip sıralayanız.
# Sonuçları yorumlayınız.

df.sort_values('wilson_lower_bound', ascending=False)[:20]

# Wilson Lower Bound skoruna göre sıralamanın, social proof' u en iyi yansıtan yöntem olduğunu görüyoruz.
# Yani;
# toplam oy sayısı beğenme ve beğenmeme sayıları da aldıkları overall değeriyle güzel bir uyum içinde sıralanmış görünüyor.
# Ayrıca zamana göre de değrelendirdiğimizde daha yakin tarihteki yorumlar daha yüksek puan almış görünüyor.
# Wilson Lower Bound yöntemiyle sıralayarak elde ettiğimiz sonuçlar daha güvenilir ve tutarlı görünmektedir.
