<div align="center">

<img src="images/whisky_icon.png" alt="Whisky icon" width="80"/>

# Whisky

### Robot esapode autonomo — 18 GdL · ESP32-C3 Zero · Stampa 3D

![Banner Whisky](images/banner.jpg)

[![Licenza: MIT](https://img.shields.io/badge/Licenza-MIT-yellow.svg)](LICENSE)
[![Piattaforma: ESP32-C3](https://img.shields.io/badge/Piattaforma-ESP32--C3%20Zero-blue)](https://www.espressif.com/)
[![GdL](https://img.shields.io/badge/GdL-18-green)]()
[![Stampa 3D PLA](https://img.shields.io/badge/Stampa%203D-PLA-orange)]()

</div>

---

## 📸 Galleria

<div align="center">

| Vista frontale | Vista laterale |
|:--------------:|:--------------:|
| ![Frontale](images/front.jpg) | ![Laterale](images/side.jpg) |

| Vista dall'alto | In movimento |
|:---------------:|:------------:|
| ![Alto](images/top.jpg) | ![Camminata](images/walking.gif) |

</div>

---

## 🧾 Panoramica

**Whisky** è un robot esapode a 6 zampe con 18 gradi di libertà, progettato e costruito interamente da zero.
Il telaio è stampato in 3D con filamento **PLA** a partire da modelli personalizzati realizzati in [OnShape](https://www.onshape.com/), e il cervello del robot è un microcontrollore **ESP32-C3 Zero**.

Il progetto nasce con l'obiettivo di esplorare algoritmi di locomozione, cinematica inversa e movimento autonomo su hardware embedded con un budget estremamente basso (40€).

---

## 🖥️ Modello 3D

> Modelli progettati in **OnShape** — completamente parametrici e open source.

<div align="center">

![Modello OnShape](images/onshape_model.png)

*Modello CAD completo di Whisky su OnShape*

</div>

I file STL pronti per la stampa sono disponibili nella cartella [`/stl`](stl/).
Tutti i componenti sono stati stampati in **PLA** con le seguenti impostazioni:

| Parametro | Valore |
|-----------|--------|
| Altezza layer | 0.2 mm |
| Riempimento | 30% |
| Supporti | Sì (zampe e staffe) |
| Materiale | PLA |

---

## ⚙️ Hardware

### Elettronica

| Componente | Modello | Quantità |
|------------|---------|:--------:|
| Microcontrollore | ESP32-C3 Zero | 1 |
| Servomotori | MG90S (ingranaggi metallici) | 18 |
| Batterie | Li-Ion 2S 5000 mAh | 2 |
| Driver servo | PCA9685 (16 canali) | 2 |
| Regolatore di tensione | BEC 5V / 6V | 1 |

### Meccanica

| Proprietà | Valore |
|-----------|--------|
| Numero di zampe | 6 |
| Gradi di libertà totali | 18 (3 per zampa) |
| Giunti per zampa | Coxa · Femore · Tibia |
| Materiale telaio | PLA |
| Peso totale | ~XXX g |

---

## 🔋 Sistema di alimentazione

Whisky è alimentato da due **pacco batterie Li-Ion 2S** in parallelo, ciascuno da **5000 mAh**, per una capacità totale di **10 000 mAh** a ~7.4 V nominali.

```
[Batteria 2S — 5000mAh] ──┐
                           ├──► BEC 5V/6V ──► Servomotori (×18)
[Batteria 2S — 5000mAh] ──┘         └──► ESP32-C3 Zero
```

---

## 🧠 Software

### Struttura del progetto

```
whisky/
├── src/
│   ├── main.cpp            # Punto di ingresso
│   ├── gait/               # Algoritmi di andatura (tripode, wave, ripple)
│   ├── ik/                 # Risolutore di cinematica inversa
│   ├── servo/              # Livello di astrazione servo
│   └── comm/               # Comunicazione WiFi / BLE
├── stl/                    # Parti stampabili in 3D
├── cad/                    # Esportazioni OnShape (.step)
├── images/                 # Foto e render
└── README.md
```

### Dipendenze

- [Arduino ESP32 core](https://github.com/espressif/arduino-esp32)
- [Adafruit PWM Servo Driver](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library)

---

## 🚀 Come iniziare

```bash
# Clona il repository
git clone https://github.com/TUO_USERNAME/whisky.git
cd whisky

# Apri con PlatformIO o Arduino IDE
# Seleziona la scheda: ESP32-C3 Zero
# Carica src/main.cpp
```

---

## 📐 Cinematica

Whisky utilizza un **modello a 3 GdL per zampa** con cinematica inversa analitica.

Ogni zampa ha tre giunti:
- **Coxa** — rotazione orizzontale (attacco al telaio)
- **Femore** — sollevamento verticale
- **Tibia** — estensione / ritrazione

Andature supportate:
- [x] Tripode (più veloce)
- [ ] Ripple (fluida)
- [ ] Wave (più stabile)

---

## 📷 Altre foto

<div align="center">

![Dettaglio zampe](images/detail_legs.jpg)
*Dettaglio zampe — servomotori MG90S e staffe in PLA*

![Elettronica](images/electronics.jpg)
*Vano elettronica — ESP32-C3 Zero e driver servo*

![Stampa](images/printing.jpg)
*Componenti in uscita dalla stampante*

</div>

---

## 🗺️ Roadmap

- [x] Progettazione meccanica (OnShape)
- [x] Stampa 3D e assemblaggio
- [x] Controllo base dei servo
- [ ] Cinematica inversa
- [ ] Andatura tripode
- [ ] Adattamento al terreno
- [ ] Controllo remoto via BLE / WiFi
- [ ] Camera a bordo

---

## 🤝 Contribuire

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti!
Apri pure una [issue](../../issues) o invia una pull request.

---

## 📄 Licenza

Distribuito con licenza MIT. Vedi [`LICENSE`](LICENSE) per i dettagli.

---

<div align="center">

<img src="images/whisky_icon.png" alt="Whisky" width="32"/>

Fatto con ☕ e tanto 🥃 &nbsp;·&nbsp; **Whisky the hexapod**

</div>
