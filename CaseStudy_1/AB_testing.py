#####################################################
# AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximum bidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi ve average bidding'in maximum bidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor. A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchase metriğine odaklanılmalıdır.


#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleri ab_testing.xlsx excel’inin ayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBidding uygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç

#####################################################
# Proje Görevleri
#####################################################

#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################
# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# !pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

control_df = pd.read_excel("Github_Measurement_Problems/CaseStudy_1/dataset/ab_testing.xlsx", sheet_name="Control Group")
test_df = pd.read_excel("Github_Measurement_Problems/CaseStudy_1/dataset/ab_testing.xlsx", sheet_name="Test Group")

control_df.head()
test_df.head()
control_df.info()

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Info #####################")
    print(dataframe.info())
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    # print("##################### Quantiles #####################")
    # print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    print("##################### Describe #####################")
    print(dataframe.describe().T)

check_df(control_df)
check_df(test_df)

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

control_df["group"] = "control"
test_df["group"] = "test"

df = pd.concat([control_df, test_df], axis=0, ignore_index=False)
df.head()
df.shape

#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################
# Adım 1: Hipotezi tanımlayınız.

# H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
# H1 : M1!= M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark vardır.)


# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

df.groupby('group')['Purchase'].mean()

#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################
# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.
# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz

# Normallik Varsayımı :
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ


test_stat, pvalue = shapiro(df.loc[df['group'] == 'control', "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

test_stat, pvalue = shapiro(df.loc[df['group'] == 'test', "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ?
# Elde edilen p-value değerlerini yorumlayınız.

# Control --> p-value = 0.5891
# Test -->  p-value = 0.1541    old. için her iki grup içinde H0 red edilemez. Yani normallik varsayımı sağlanır

# Varyans Homojenliği :
# H0: Varyanslar homojendir.
# H1: Varyanslar homojen Değildir.
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ
# Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
# Test sonucuna göre normallik varsayımı sağlanıyor mu? Elde edilen p-valuedeğerlerini yorumlayınız.

test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# p-value = 0.1083  old. için H0 red edilemez. Yani varyans homejenliği sağlanır


# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz

# Normallik homejenliği ve varyans homejenliği sağlanmaktadır.
# Yani;
# Varsayımlar sağlanmaktadır. O yüzden Bağımsız İki Örneklem T Testi uygulanmalıdır

# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark yoktur.)
# H1: M1 != M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark vardır)
# p<0.05 HO RED,
# p>0.05 HO REDDEDİLEMEZ

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True)

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# p-value = 0.3493 ol için H0 Red edilemez yani
# Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol. anlamlı fark yoktur

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

# Her iki grup için de normallik varsayımı ve varyans homejenliği sağlandığı için Bağımsız .örneklem T Testi kullanıldı.
# Burada çıkan p_value değeri 0.05' den büyük olduğu için H0 red edilemez
# yani kontol ve test grubu satın alma ortalamaları arasında anlamasal bir fark yoktur sonucunu istatistiksel olarak çıkarabiliriz
# Sonuç olarak; H0 hipotezi red edilememiştir

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

# Elde ettiğimiz sonuçlara göre average bidding'in maximum bidding'den daha fazla dönüşüm getirmediği görülmektedir.
# iki seçenek sunulabiliriz.
# Ya mevcut yöntem kullanılmaya devam edilebilir ya da reklamalar ve tıklanma sayıları ile ilgili iyileştirmelere gidilebilir
# Ayrıca, tıklanma sayıları, sitede geçirilen süreler gibi diğer kriterler göz önünde bulundurularak aradadki farklar tespit edilip mevcut testler bir süre sonra tekrar denenebilir