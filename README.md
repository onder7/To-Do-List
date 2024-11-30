# 📝 Todo List Uygulaması

Flet framework'ü kullanılarak geliştirilmiş modern ve kullanıcı dostu bir yapılacaklar listesi uygulaması.

![image](https://github.com/user-attachments/assets/c96c2b0e-c7b4-4fed-b215-9ff3e5f63b64)

İndirme Linki : https://drive.google.com/file/d/16Ft3BO3V1-Cu2KCWn5zS2yGmYb6VMBVV/view?usp=sharing
## 🌟 Özellikler

- ✨ Modern ve kullanıcı dostu arayüz
- 📅 Görevlere tarih ve saat ekleme
- ⏰ Alarm ve hatırlatma sistemi
- 🏷️ Kategori ve öncelik belirleme
- 📝 Görevlere not ekleme
- 🌓 Karanlık/Aydınlık tema desteği
- 🔔 Bildirim sistemi
- 💾 SQLite veritabanı ile veri saklama

## 🚀 Kurulum

1. Repositoryi klonlayın:
```bash
git clone https://github.com/onder7/todo-list.git
cd todo-list
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python To-Do-List.py
```

## 📦 Gereksinimler

- Python 3.8+
- flet
- plyer
- sqlite3

## 💻 Kullanım

- **Görev Ekleme:** Ana ekrandaki form aracılığıyla yeni görevler ekleyin
- **Görev Düzenleme:** Görevlere tıklayarak detayları görüntüleyin
- **Alarm Kurma:** Görevlere tarih/saat ekleyip alarm kurabilirsiniz
- **Tema Değiştirme:** Sağ üst köşedeki tema butonu ile temayı değiştirin
- **Görev Filtreleme:** Kategorilere göre görevleri filtreleyebilirsiniz

## 🎯 Özellikler Detayı

### Görev Yönetimi
- Görev ekleme, silme ve düzenleme
- Görevleri tamamlandı olarak işaretleme
- Öncelik seviyesi belirleme (Normal, Önemli, Acil)
- Kategori atama (İş, Kişisel, Alışveriş, Sağlık vb.)

### Zaman Yönetimi
- Görevlere son tarih ekleme
- Saat belirleme
- Alarm kurma
- Zamanı geçen görevleri vurgulama

### Bildirimler
- Masaüstü bildirimleri
- Sesli alarmlar
- Özelleştirilebilir alarm sesleri

### Arayüz
- Sezgisel kullanıcı arayüzü
- Karanlık/Aydınlık tema desteği
- Duyarlı tasarım
- Modern görsel öğeler

## 🛠️ Teknik Detaylar

- **Frontend:** Flet (Flutter tabanlı)
- **Veritabanı:** SQLite
- **Bildirim Sistemi:** Plyer
- **Dosya Yapısı:**
  ```
  todo-list/
  ├── To-Do-List.py
  ├── requirements.txt
  ├── README.md
  ├── alarms/
  │   └── alarm-clock.wav
  └── todo.db
  ```

## 🤝 Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📞 İletişim & Sosyal Medya

* **GitHub:** [github.com/onder7](https://github.com/onder7)
* **LinkedIn:** Mustafa Önder Aköz
* **Medium:** @onder7
* **Web:** ondernet.net

## 📜 Lisans

© 2024 Mustafa Önder Aköz - Tüm hakları saklıdır.
