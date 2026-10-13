# Dock Waybar

Loghi SVG monocromatici da 16 px in celle 28 × 28 px, grigio lavanda #c5bdd9 a riposo e verde Dracula #50fa7b quando attive. Tray accanto ai launcher, LocalSend scompare dal dock mentre il processo è attivo. VM resta come icona con stato nel tooltip. Tailscale e Proton sono verdi quando connessi; Syncthing, T3 e Pi quando in esecuzione; Octo durante la sessione SSH; Slack mentre il browser della web app è in esecuzione.

## Configurazione personale

Copia `.env.example` in `~/.config/waybar/.env` e proteggilo con `chmod 600 ~/.config/waybar/.env`, poi modifica i valori. `.env` è escluso da Git; se manca, i launcher usano i valori di `.env.example`.

Configurazione personale:

```dotenv
OCTO_HOST=octo.example.net
OCTO_USER=nomeutente
SLACK_URL='https://app.slack.com/client/...'
SLACK_USER='nome@example.net'
SLACK_PROFILE='Profile 1'
PI_START_DIR='~'
SLACK_FLATPAK=io.github.ungoogled_software.ungoogled_chromium
```

- `PI_START_DIR`: cartella iniziale di Pi, predefinita `~` (home). Sono supportati percorsi con spazi. Pi si apre in tiling, senza massimizzazione o fullscreen; le dimensioni seguono il layout del workspace.
- `OCTO_HOST`: hostname o alias definito in `~/.ssh/config`.
- `OCTO_USER`: utente SSH passato con `ssh -l`; se vuoto usa quello predefinito di SSH. È ancora possibile scrivere `utente@hostname` in OCTO_HOST lasciando OCTO_USER vuoto.
- `SLACK_URL`: link del workspace Slack.
- `SLACK_USER`: account/email da usare sul sito, conservato come promemoria. Il login avviene nel browser e resta salvato nel profilo; il launcher non compila automaticamente il modulo di accesso.
- `SLACK_PROFILE`: `Profile 1`, cartella verificata del profilo Chromium “gugu”.

Valori letterali, con virgolette per spazi o caratteri speciali. Il file non viene eseguito come shell e non espande `$VAR`. Puoi aggiungere altre variabili per i tuoi siti. I comandi di T3 e Pi restano in `dock-settings.json` come liste di argomenti.

Le impostazioni vengono rilette a ogni click: nessun riavvio necessario. I launcher portano in primo piano una finestra esistente quando identificabile tramite Hyprland. Log degli avvii in `~/.local/state/waybar/` (o `$XDG_STATE_HOME/waybar/`).

I click dei servizi esistenti rimangono quelli della configurazione precedente. Timer: click sinistro attiva/avvia/pausa, destro seleziona preset o disattiva, centrale reset, rotella regola tempo/modalità. Pomodoro mostra tempo e sessione corrente, con pausa arancione.

## Backup e ripristino

I backup locali sono in `~/.config/waybar/back/` e sono esclusi da Git. Ogni cartella contiene `waybar.tar.gz` e `restore.sh`. Esegui `bash ~/.config/waybar/back/<backup>/restore.sh` per ripristinare quel backup. Il ripristino salva prima la configurazione corrente in `back/pre-restore-*`, poi ricarica Waybar.

Timer a riposo: solo clessidra da 16 px, senza bordo né sfondo.

Tutti i tooltip gestiti dalla configurazione Waybar sono in inglese. I tooltip delle applet nel tray vengono forniti dalle rispettive applicazioni.
