<div align="center">

# <img src="images/whisky_icon.png" alt="Whisky icon" width="50" valign="bottom"/> Whisky
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
| Supporti | No |
| Materiale | PLA |

---

## ⚙️ Hardware

### Elettronica

| Componente | Modello | Quantità |
|------------|---------|:--------:|
| Microcontrollore | ESP32-C3 Zero | 1 |
| Servomotori | MG90S (ingranaggi metallici) | 18 |
| Batterie | Li-Ion 1S 5000 mAh | 2 |
| Driver servo | PCA9685 (16 canali) | 2 |
| Regolatore di tensione | DD4012SA 5V | 1 |
| Regolatore di tensione | UBEC 6V | 1 |

### Meccanica

| Proprietà | Valore |
|-----------|--------|
| Numero di zampe | 6 |
| Gradi di libertà totali | 18 (3 per zampa) |
| Giunti per zampa | Coxa · Femore · Tibia |
| Materiale telaio | PLA |
| Peso totale | 670 g |

---

## 🔋 Sistema di alimentazione

Whisky è alimentato da un **pacco batteria Li-Ion 2S** composto da due celle da **5000 mAh ciascuna** collegate in serie, per una tensione nominale di ~7.4 V e una capacità di **5000 mAh**.

```
[Cella 1 — 3.7V 5000mAh] ──┐
                           ├──► BEC 5V       2x BEC 6V ──► Servomotori (9 + 9)
[Cella 2 — 3.7V 5000mAh] ──┘      └──► ESP32-C3 Zero
```

---

## 🧠 Software

### Algoritmi di movimento
 
Il controllo del movimento segue una pipeline a più stadi, dall'input dell'utente fino ai segnali inviati ai singoli servomotori.
 
**1. Input utente — due vettori**
 
Il movimento è descritto da due vettori `[angolo, velocità]`:
 
- **Traslazione** — direzione assoluta sul piano e intensità, ad esempio `[180, 1.0]` per andare indietro a velocità massima o `[90, 0.5]` per spostarsi a destra al 50%.
- **Rotazione** — senso di rotazione e intensità. Per scelta progettuale l'angolo accetta solo due valori: `0` per girare a sinistra e `180` per girare a destra, ad esempio `[0, 0.5]` ruota a sinistra al 50% e `[180, 0.8]` ruota a destra all'80%.
**2. Decomposizione per zampa — da 2 a 6 vettori**
 
Per ogni zampa viene calcolato un vettore di movimento individuale in tre passi:
 
1. I due vettori di input vengono **sommati vettorialmente**, ottenendo un comando unico che combina traslazione e rotazione in modo continuo e simultaneo.
2. Al vettore risultante viene **aggiunto l'offset angolare** della zampa. Le sei zampe sono disposte con uno scarto fisso di **45° o 90°** l'una rispetto alla precedente, in modo che ciascuna spinga nella direzione corretta rispetto alla propria posizione sul telaio.
3. Il risultato è un **vettore per zampa** che specifica direzione e ampiezza del passo di quella specifica zampa.

**3. Generazione dell'andatura — traiettoria a "D" rovesciata**
 
L'estremità di ogni zampa non si muove in linea retta: un algoritmo di *gait generation* prende in input il vettore della zampa e la sua **fase** nel ciclo di andatura, e genera una traiettoria a forma di **"D" rovesciata**.
 
- La parte curva (arco in aria) rappresenta la fase di **swing** — la zampa si solleva, avanza e torna a terra.
- La parte piatta (appoggio a terra) rappresenta la fase di **stance** — la zampa spinge il corpo in avanti.
La lunghezza e la direzione dell'arco sono quelle calcolate al passo precedente. Le fasi delle sei zampe sono due sfasate di 180°, la prima per le zampe [1,3,5] e una per [2,4,6] in modo da mantenere sempre almeno 3 zampe a terra.
 
**4. Cinematica inversa**
 
Una volta noto il punto che l'estremità della zampa deve raggiungere in un dato istante, si risolve la **cinematica inversa** per ricavare gli angoli dei tre giunti (Coxa, Femore, Tibia). L'algoritmo è identico per tutte le zampe, ma opera in un **sistema di riferimento cartesiano locale** ruotato nella direzione di ciascuna zampa, semplificando il calcolo.
 
**5. Output — segnali ai driver**
 
Gli angoli dei 18 giunti vengono infine convertiti in **segnali PWM** e inviati ai driver servo (PCA9685), che pilotano fisicamente i motori MG90S.


### Dipendenze

- [Interprete Micropython](https://github.com/micropython/micropython)

---

## 🚀 Come costruirlo
### Stampa 3D
Scarica e stampa preferibilmente con stampante FDM tutti i file presenti nella cartella [`/stl`](stl/)

### Assemblaggio
Prima di iniziare devi smontare tutti i 18 motori per cambiare il carter inferiore con quello stampato con i supporti per i bracci.
Successivamente parti dal telaio centrale su cui devi avvitare i motori alla base degli snodi, le viti sono autoperforanti e devono impanare nella plastica quindi evita di applicare forza eccessiva. Poi monta i motori degli altri due snodi come mostrato in foto.
Fisssa gli UBEC ai driver con una fascetta altrimenti non c'è spazio per i cavi dei motori. 
Avvita i driver nelle sedi apposite del telaio e lega con delle fascette i fili dei motori ai braccetti delle zampe lasciando un pò di filo per permettere il movimento delle articolazioni.
Collega i motori ai driver seguendo i collegamenti presenti nel file main.py e allo stesso modo collega il microcontrollore ai driver e infine l'alimentazione di microcontrollore e driver.
Attenzione, i ground dei due alimentatori devono essere messi in comune ma le linee 5v e 6v devono rimanere separate per evitare danni al microcontrollore.

### Carica il software

Per prima cosa devi assicurarti di aver installato ampy e di aver collegato il robot via USB-C

```bash
# Clona il repository
git clone https://github.com/L0r3nz0000/Whisky.git
cd Whisky

ampy -p PORTA put src/main.py # esempio porta: /dev/ttyACM0
ampy -p PORTA reset
```
Ora si aprirà una rete wifi "Configura Whisky" senza password, collegati e inserisci le credenziali del tuo access point per permettere a whisky di collegarsi al controller.  

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
- [x] Cinematica inversa
- [x] Andatura tripode
- [x] Combinazione di più movimenti simultanei
- [x] Controllo remoto via WiFi
- [ ] Adattamento al terreno

---

## 📄 Licenza

Distribuito con licenza MIT. Vedi [`LICENSE`](LICENSE) per i dettagli.

---

<div align="center">

Fatto con ☕ e tanto 🥃 &nbsp;·&nbsp; 

</div>
