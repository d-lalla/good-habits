# Good Habits — Decisioni approvate e brief di implementazione

13.11.2026 · stato: **approvato**, pronto per l'implementazione

Questo documento sostituisce l'architettura descritta in [analisi-good-habits.md](analisi-good-habits.md).
In caso di conflitto vale questo.

## 1. Cambio di direzione

Good Habits **non è un'applicazione**. È una **skill per assistenti AI** (formato `SKILL.md`), utilizzabile con
Claude e, dove il formato è supportato, con gli assistenti OpenAI.

| Dell'analisi originale | Esito |
|---|---|
| Catalogo dichiarativo, 4 tipi di obiettivo, 4 regole di completamento | **resta**, come file della skill |
| Distinzione obiettivo / attività pianificata / reminder / registrazione | **resta**, come concetti |
| Continuità non punitiva, progressione graduale, linguaggio descrittivo | **resta**, come istruzioni |
| Reminder contestuale al progresso (3.5), percorsi (3.6) | **resta** |
| Limiti su salute: nessuna diagnosi, default come esempi modificabili | **resta** |
| AI opzionale | **ribaltato**: l'assistente è il motore |
| Blazor, API, MariaDB, login, Web Push, scheduler in-process, hosting | **eliminato** |

## 2. Decisioni

| # | Decisione | Scelta |
|---|---|---|
| D1 | Forma del prodotto | skill per assistenti AI, non app |
| D2 | Stack | `SKILL.md` + file di riferimento + uno script Python (solo libreria standard) |
| D3 | Autenticazione | nessuna: è quella dell'host |
| D4 | Database | nessuno |
| D5 | Catalogo | un file per abitudine, caricato solo quando serve |
| D6 | Reminder | attività pianificate dell'host, al massimo **un check-in giornaliero + un riepilogo settimanale**; per orari precisi la skill genera un file calendario `.ics` |
| D7 | Attività pianificate | calcolate dalla configurazione; nel log solo fatti (registrazioni, salti, pause) |
| D8 | Continuità | finestra mobile 7 e 28 giorni; salti pianificati e pause fuori dal conteggio; serie più lunga solo come dato |
| D9 | AI | è il motore; i **numeri** però li calcola lo script, non il modello |
| D10 | Hosting | nessuno |
| D11 | Lingua | skill e catalogo in **inglese**; l'assistente risponde nella lingua dell'utente |
| D12 | Pubblico | uso personale all'inizio, repository già strutturato per essere reso pubblico (licenza MIT) |
| D13 | Portabilità | **a livelli** (sezione 3): nucleo portabile, potenziamenti solo se l'host li offre |
| D14 | Stato | **file** come fonte di verità; **memoria dell'host come ripiego** dichiarato dove i file non ci sono |
| D15 | Posizione dei dati | cartella scelta dall'utente (default `~/good-habits`), mai nella cartella della skill né nel repository |
| D16 | Ampiezza della prima versione | catalogo ampio subito: circa 20 abitudini, 3 percorsi, più abitudine personalizzata |

## 3. Architettura a livelli

Una sola skill. All'avvio verifica cosa l'host sa fare e lo dice all'utente in una riga.

| Livello | L'host offre | La skill fa | Numeri |
|---|---|---|---|
| 0 | solo conversazione | aiuta a scegliere, configura, propone percorsi, raccoglie i check-in a voce; stato affidato alla memoria dell'host | approssimati, dichiarati tali |
| 1 | file + esecuzione di codice | stato su file, script per registrare e calcolare | esatti |
| 2 | attività pianificate | crea check-in giornaliero e riepilogo settimanale | esatti |

Regole:

- nessuna funzione specifica di un host nel nucleo: i livelli 1 e 2 sono descritti come capacità ("se puoi
  scrivere file…", "se puoi pianificare attività…"), non come nomi di strumenti;
- al livello 0 la skill non inventa conteggi: riporta ciò che ricorda e segnala che non è verificabile;
- il passaggio di livello non perde dati: al livello 1 la skill offre di trascrivere nel file ciò che sa.

## 4. Struttura del repository

```
good-habits/                 cartella della skill: è ciò che si installa copiandola
  SKILL.md                   quando attivarsi, livelli, flussi, tono, limiti
  references/
    catalog/<key>.md         una abitudine per file
    paths/<key>.md           un percorso per file
    state-format.md          formato di habits.json e log.jsonl
  scripts/
    habits.py                unico script, solo libreria standard
tests/
  test_habits.py             un file di test per lo script
docs/                        questo documento e l'analisi originale
README.md  LICENSE
```

`SKILL.md` resta breve (indicativamente sotto le 300 righe): dettagli e catalogo stanno in `references/`.

## 5. Catalogo

### 5.1 File di abitudine

Intestazione strutturata + testo. Esempio illustrativo:

```markdown
---
key: hydration
category: nutrition
goal_type: quantity        # quantity | time | count | check
period: day                # day | week
unit: ml
default_target: 2000       # example value, user-adjustable
target_min: 500
target_max: 4000
quick_log: [250, 500]
progression_step: null
---
# Hydration
Why it helps · how to start small · how to log · message variants (start / midway / almost there)
```

Le regole di completamento restano quattro e fisse: `sum_at_least` (quantity), `time_before` (time),
`count_at_least` (count), `checked` (check). Un test verifica che ogni file del catalogo abbia i campi
obbligatori e valori ammessi.

### 5.2 Abitudini della prima versione (21)

| Categoria | Abitudini |
|---|---|
| Sonno e recupero | `bedtime`, `regular-sleep-schedule`, `evening-routine`, `no-screens-before-bed` |
| Alimentazione e idratazione | `hydration`, `fruit-and-vegetables`, `less-sugary-drinks` |
| Attività fisica | `workout`, `daily-steps`, `stretching`, `active-breaks` |
| Benessere mentale | `meditation`, `breathing`, `gratitude-journal` |
| Apprendimento e crescita | `daily-reading`, `language-study`, `learning-15-min` |
| Produttività e organizzazione | `plan-day`, `weekly-review`, `focus-time` |
| Relazioni e vita personale | `reach-out` |

Più `custom`: stessi campi, scelti dall'utente.

Vincoli di contenuto: nessuna richiesta di peso, calorie, diagnosi, farmaci; diario e gratitudine registrano
solo il fatto, mai il testo; ogni default è presentato come esempio modificabile.

### 5.3 Percorsi (3)

File con elenco di `key`, parametri che sostituiscono i default e scostamento in minuti da un orario-àncora.

| Percorso | Àncora | Passi |
|---|---|---|
| `sleep-better` | ora di andare a letto | −60 `no-screens-before-bed` · −45 `daily-reading` · −20 `meditation` · 0 `bedtime` |
| `morning-start` | sveglia | `hydration` · `stretching` · `plan-day` |
| `focused-workday` | inizio lavoro | `plan-day` · `focus-time` · `active-breaks` · `weekly-review` (settimanale) |

Attivare un percorso crea normali abitudini marcate con `path`; poi ognuna è indipendente.

## 6. Stato (livelli 1 e 2)

Nella cartella dell'utente, due file:

- `habits.json` — abitudini attive e loro configurazione (target, giorni, orario, stato attiva/in pausa,
  `path` di provenienza), più preferenze (ora del check-in, giorno del riepilogo).
- `log.jsonl` — una riga per evento, solo in aggiunta: `log` (valore), `skip`, `pause`, `resume`.
  Ogni riga porta la **data locale** dell'utente e l'istante di inserimento.

Nessun altro file. Niente dati derivati salvati: progressi e continuità si ricalcolano dal log.

## 7. Script `habits.py`

Unica fonte dei numeri. Comandi previsti:

| Comando | Fa |
|---|---|
| `log` | aggiunge una riga a `log.jsonl` (registrazione, salto, pausa, ripresa) |
| `today` | cosa è previsto oggi, cosa è fatto, cosa manca |
| `progress` | completamento del periodo, continuità 7 e 28 giorni, serie più lunga, traguardi |
| `ics` | genera un file calendario con gli orari delle abitudini attive |

Uscita in JSON: l'assistente la traduce in linguaggio naturale. Lo script non contiene testi per l'utente.
Proposte di progressione (aumentare o ridurre il target) derivano da soglie fisse calcolate da `progress`:
continuità ≥ 80 % per due settimane → propone un passo in più; < 40 % → un passo in meno. Sempre proposta,
mai modifica automatica.

## 8. Comportamento della skill

- **Primo avvio**: aree di interesse → 2–3 proposte per area o un percorso → configurazione con default →
  consiglio di partire con una o due abitudini → cartella dei dati (livello 1) → check-in e riepilogo (livello 2).
- **Check-in**: `today`, poi registrazione di ciò che l'utente riferisce; messaggio contestuale al progresso
  ("questa settimana 4 su 7"), mai solo "ricordati di…".
- **Riepilogo settimanale**: `progress`, cosa è andato, cosa è cambiato, al massimo un suggerimento.
- **Gestione**: aggiungere, modificare, mettere in pausa, archiviare, eliminare in qualsiasi momento.
- **Reminder ignorati**: se i check-in restano senza risposta, la skill propone di cambiare orario o ridurre,
  non insiste.
- **Tono**: descrittivo, mai valutativo; nessun punteggio, livello, classifica o "serie a rischio".
- **Limiti**: nessuna diagnosi o prescrizione; obiettivi di benessere mai presentati come validi per tutti;
  rimando a un professionista per temi medici.

## 9. Piano di implementazione

| Passo | Contenuto | Fatto quando |
|---|---|---|
| 1 | `habits.py` + `tests/test_habits.py` (completamento, continuità, salti e pause, settimane, `.ics`) | i test passano |
| 2 | `references/state-format.md` e 3 abitudini campione, una per tipo di obiettivo non banale | il test di validazione del catalogo passa |
| 3 | `SKILL.md`: attivazione, livelli, flussi, tono, limiti | prova manuale di primo avvio e check-in al livello 1 |
| 4 | Resto del catalogo (21 abitudini) e 3 percorsi | validazione del catalogo verde |
| 5 | Prova ai tre livelli; istruzioni di installazione nel README | check-in pianificato eseguito almeno una volta |

## 10. Da verificare durante l'implementazione

- Supporto effettivo del formato `SKILL.md` negli assistenti OpenAI e differenze di installazione: va
  controllato sulla documentazione corrente, non dato per scontato.
- Quali host offrono attività pianificate e con che limiti (frequenza minima, costo per esecuzione).
- Comportamento al livello 0: quanto è affidabile la memoria dell'host tra conversazioni.
- Fuso orario: lo script usa la data locale della macchina; da verificare negli ambienti di esecuzione remoti,
  dove l'orologio può essere in UTC (in quel caso la data la passa l'assistente).
