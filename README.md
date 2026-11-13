# Good Habits

Skill per assistenti AI (formato [Agent Skills](https://agentskills.io/specification), file `SKILL.md`) che
aiuta a costruire abitudini positive: catalogo di 21 abitudini configurabili, 3 percorsi pronti, check-in
contestuali al progresso ("questa settimana 4 su 7"), continuità non punitiva. Salti e pause non contano come
mancanze, i cambi di target sono sempre proposte.

L'assistente è il motore della conversazione; i **numeri** li calcola uno script Python (solo libreria
standard), così non sono mai stimati dal modello.

- [Decisioni approvate e brief di implementazione](docs/decisioni.md) — documento di riferimento
- [Analisi originale](docs/analisi-good-habits.md) — pensata per un'applicazione, superata in parte

## Struttura

```
good-habits/                 la skill: è la cartella da installare
  SKILL.md                   attivazione, livelli, flussi, tono, limiti
  references/
    catalog/<key>.md         una abitudine per file (21)
    paths/<key>.md           un percorso per file (3)
    state-format.md          formato di habits.json e log.jsonl
  scripts/habits.py          log, today, progress, ics
tests/test_habits.py         test dello script, del catalogo, dei percorsi e di SKILL.md
```

## Livelli

La skill verifica all'avvio cosa sa fare l'assistente e lo dice in una riga.

| Livello | L'assistente può | Cosa offre la skill |
|---|---|---|
| 0 | solo conversare | scelta e configurazione, check-in a voce; stato nella memoria dell'assistente, numeri dichiarati approssimati |
| 1 | scrivere file persistenti ed eseguire Python 3 | registro su file, numeri esatti, file calendario `.ics` per gli orari |
| 2 | in più, pianificare attività | un check-in giornaliero e un riepilogo settimanale automatici |

## Installazione

La cartella da installare è `good-habits/` (quella che contiene `SKILL.md`), non l'intero repository.
Il nome della cartella deve restare `good-habits`: deve coincidere con il campo `name`.

**Claude Code** — skill personale, disponibile in tutti i progetti
([documentazione](https://code.claude.com/docs/en/skills)):

```bash
cp -r good-habits ~/.claude/skills/good-habits
```

Livello 1. Il livello 2 c'è con le attività pianificate dell'app desktop (vedi limiti noti).

**claude.ai e app Claude** — attivare *Settings > Capabilities > Code execution and file creation*, poi
*Customize > Skills > + > Upload a skill* con uno ZIP che ha la cartella `good-habits` alla radice
([help center](https://support.claude.com/en/articles/12512180-use-skills-in-claude)):

```powershell
Compress-Archive -Path good-habits -DestinationPath good-habits.zip
```

**Codex (OpenAI)** — skill utente ([documentazione](https://learn.chatgpt.com/docs/build-skills)):

```bash
cp -r good-habits ~/.agents/skills/good-habits
```

**ChatGPT** — secondo la documentazione OpenAI le skill standalone sono disponibili nell'app desktop
(barra *Skills*) e, distribuite come plugin, anche sul web e su mobile. Vedi limiti noti.

**Altri assistenti compatibili con Agent Skills** — copiare la cartella dove l'assistente carica le skill.

I dati dell'utente (`habits.json`, `log.jsonl`) stanno in una cartella scelta dall'utente (default
`~/good-habits`), mai nella cartella della skill né in questo repository. Il `.gitignore` li esclude comunque.

## Test

```bash
python -m unittest discover -s tests
```

Coprono le quattro regole di completamento, la continuità a 7 e 28 giorni, salti e pause, gli obiettivi
settimanali a cavallo di due settimane, le proposte di progressione, il file `.ics`, la riga di comando, la
validazione di tutti i file del catalogo e dei percorsi, l'intestazione di `SKILL.md` e la coerenza tra
`state-format.md` e lo script.

## Limiti noti

Verificati sulla documentazione a novembre 2026; dove non è stato possibile, è scritto.

- **Persistenza dei file.** Il livello 1 richiede file che restano tra una conversazione e l'altra.
  Con Claude Code, Codex CLI e le app desktop che lavorano su una cartella locale ci sono. Per claude.ai
  e ChatGPT non risulta documentato che l'ambiente di esecuzione conservi i file tra conversazioni: in quel
  caso la skill funziona al livello 0. **Non verificato.**
- **ChatGPT ed esecuzione di script.** La documentazione OpenAI prevede una cartella `scripts/` nelle skill
  ma non dice se ChatGPT esegue script Python inclusi. **Non verificato.**
- **Attività pianificate in Claude Desktop** ([documentazione](https://claude.com/docs/third-party/claude-desktop/scheduled-tasks)):
  girano sul computer dell'utente, che deve essere acceso con l'app aperta. Se un'esecuzione salta, ne parte
  una sola alla riapertura; oltre i sette giorni le esecuzioni perse non partono più.
- **Attività pianificate in ChatGPT** ([help center](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)):
  da 3 a 15 attività attive secondo il piano, al massimo una volta al giorno sul piano gratuito, ogni
  esecuzione consuma la quota. Se un'attività pianificata possa usare una skill ed eseguirne lo script:
  **non verificato**.
- **Routine cloud di Claude Code**: i limiti di esecuzione giornalieri si trovano solo su fonti di terzi.
  **Non verificato.**
- **Memoria al livello 0**: quanto la memoria di un assistente sia affidabile tra conversazioni non è
  verificabile; per questo al livello 0 la skill non dà conteggi esatti.
- **Fuso orario**: negli ambienti remoti l'orologio può essere in UTC. Lo script accetta la data locale con
  `--date` e la skill chiede all'assistente di passarla sempre; per le esecuzioni pianificate il fuso
  dell'utente è scritto nel testo dell'attività.
- **Prova del livello 2**: eseguita con un'attività pianificata di sessione di Claude Code (un check-in alle
  21:41, eseguito all'orario previsto). Le attività pianificate durevoli di Claude Desktop e di ChatGPT non
  sono state provate.
- **Correzioni**: una quantità si corregge con un valore negativo, un orario registrandolo di nuovo (vale
  l'ultimo). Una registrazione sbagliata di tipo `count` o `check` non si può ancora annullare.
- **Cambio di target**: il target precedente resta valido per i giorni passati (campo `history`). Cambiare i
  giorni previsti (`days`) invece rivaluta anche il passato.
- **Orari oltre la mezzanotte**: un orario conta "entro il target" se cade nelle 12 ore precedenti.

## Licenza

[MIT](LICENSE)
