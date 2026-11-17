# Snagomjer: tehnički plan

> Radna verzija 0.2 (17.11.2026). Tehnički dio projekta. Organizacija (tim, faze, WBS, gantogram, zapisnici) je u [Projektna_dokumentacija_v1.1.docx](Projektna_dokumentacija_v1.1.docx). Odjeljci označeni s **Prijedlog** treba potvrditi do M2 (4.12.2026).

## 1. Opseg i ograničenja

Snagomjer je mobilna aplikacija za bilježenje treninga snage (vježbe, serije, ponavljanja, težina), pregled povijesti i grafički prikaz napretka po vježbi.

| Ograničenje | Posljedica za izvedbu |
| --- | --- |
| Podaci samo lokalno, bez računa i sinkronizacije | nema backenda ni autentikacije; SQLite na uređaju je jedini izvor podataka |
| Potpuni rad bez interneta | nema mrežnih poziva u aplikaciji |
| Android je obavezna platforma | isporučuje se APK (EAS Build) |
| iOS bez plaćenog Apple računa | iOS se testira samo u Expo Go; koriste se samo moduli iz Expo SDK-a |
| Unos tijekom treninga, jednom rukom | veliki dodirni elementi, unos bez tipkovnice gdje god je moguće |
| Sučelje samo na engleskom | jedan jezik, bez i18n; brojevi i datumi formatiraju se preko `Intl` |

## 2. Zahtjevi

### 2.1 Funkcionalni (MoSCoW)

**Must**

- Katalog vježbi: predefinirane vježbe po mišićnim skupinama, pretraga, vlastite vježbe
- Trening: početak, dodavanje vježbi, unos serija (ponavljanja + težina), završetak
- Brzi unos: kopiranje prethodne serije, tipke +/−, popunjavanje vrijednostima s prošlog treninga
- Prikaz prethodnog rezultata iste vježbe tijekom unosa
- Povijest: popis po datumu, detalji, uređivanje i brisanje treninga
- Izračun volumena po vježbi i po treningu
- Grafovi po vježbi: volumen, najveća težina, ukupno ponavljanja, procijenjeni 1RM

**Should:** osobni rekordi s oznakom novog rekorda, odbrojavanje odmora, predlošci treninga, filtar razdoblja na grafovima (4 tjedna / 3 mjeseca / godina), jedinice kg/lb, tamna tema.

**Could:** izvoz/uvoz (CSV/JSON), kalendarski prikaz treninga, praćenje tjelesne težine.

**Won't:** računi, sinkronizacija, društvene funkcije, prehrana.

### 2.2 Nefunkcionalni

| # | Zahtjev | Kako se provjerava |
| --- | --- | --- |
| N1 | Ponovljena serija (ista težina ili ponavljanja) unosi se u najviše 3 dodira | brojanje dodira u testiranju s korisnicima |
| N2 | Prekid aplikacije usred treninga ne gubi unesene serije | ručni test: zatvaranje aplikacije tijekom treninga |
| N3 | Promjena sheme baze ne briše postojeće podatke | migracije + CI provjera (odj. 8) |
| N4 | Aplikacija radi bez mreže | ručni test u načinu rada u zrakoplovu |
| N5 | Izračuni su pokriveni unit testovima | Jest, pokrivenost modula izračuna |

## 3. Tehnologije

| Namjena | Odabrano | Razlog |
| --- | --- | --- |
| Okvir | React Native + Expo (TypeScript) | jedan kod za Android i iOS; testiranje na vlastitom mobitelu preko Expo Go |
| Navigacija | Expo Router | navigacija prema strukturi datoteka u `app/` |
| Baza | expo-sqlite + Drizzle ORM | relacijski podaci, tipizirani upiti, migracije generirane iz sheme |
| Grafovi | react-native-gifted-charts (+ react-native-svg) | linijski i stupčasti grafovi, radi u Expo Go |
| Testovi | Jest (`jest-expo`) + React Native Testing Library | standard za Expo |
| Kvaliteta | ESLint + Prettier, husky + lint-staged + commitlint | jednak stil, provjera prije commita |
| CI/CD | GitHub Actions, EAS Build | provjere na svaki PR, APK na oznaku verzije |

Paketi se dodaju s `npx expo install`, da verzije budu usklađene s Expo SDK-om.

## 4. Arhitektura

```text
Ekrani (app/, Expo Router)
   │  koriste
Komponente (src/components)   Hookovi (src/hooks)
                                 │  pozivaju
                        Repozitoriji (src/db/repositories)  ──  Izračuni (src/lib/calculations)
                                 │  Drizzle
                        expo-sqlite  (lokalna baza)
```

- **Baza je jedini izvor stanja.** Ekrani čitaju podatke preko hookova. Za popise koji se mijenjaju koristi se `useLiveQuery` iz `drizzle-orm/expo-sqlite`, pa se prikaz sam osvježi nakon upisa (baza se otvara s `enableChangeListener: true`). Zasebna biblioteka za globalno stanje zasad nije potrebna. **Prijedlog**
- **Repozitoriji** sadrže sve upite. Ekrani i komponente ne pišu SQL ni Drizzle upite izravno.
- **Izračuni** su čiste funkcije bez pristupa bazi. Primaju serije i vraćaju brojeve, pa se lako testiraju.
- **Aktivni trening se sprema odmah.** Na početku treninga nastaje redak `Workout` s `finished_at = NULL`, a svaka serija upisuje se čim se potvrdi. Tako je ispunjen N2. Pri pokretanju aplikacija provjerava postoji li nedovršeni trening i nudi nastavak.

## 5. Model podataka

**Prijedlog** (konačna verzija do M2):

| Tablica | Stupci | Napomene |
| --- | --- | --- |
| `exercise` | `id`, `name`, `muscle_group`, `equipment?`, `is_custom`, `archived_at?` | vlastita vježba s poviješću se arhivira, ne briše |
| `workout` | `id`, `started_at`, `finished_at?`, `note?` | `finished_at = NULL` znači aktivni trening |
| `workout_exercise` | `id`, `workout_id` → workout, `exercise_id` → exercise, `position` | redoslijed vježbi u treningu |
| `set` | `id`, `workout_exercise_id` → workout_exercise, `position`, `reps`, `weight`, `is_warmup` | jedna serija |
| `setting` | `key`, `value` | jedinice, tema |
| `template`*, `template_exercise`* | `id`, `name` / `template_id`, `exercise_id`, `position` | samo ako se rade predlošci |

\* Should

**Pravila:**

- Vrijeme se sprema kao Unix vrijeme u milisekundama (`integer`).
- Težina se uvijek sprema u **kg** (`real`). Pretvorba u lb (1 lb = 0,45359237 kg) radi se samo pri prikazu i unosu.
- Brisanje treninga kaskadno briše njegove `workout_exercise` i `set` retke. Vježba koja se koristi u povijesti ne smije se obrisati (`ON DELETE RESTRICT`).
- Indeksi: `workout(started_at)`, `workout_exercise(exercise_id)`, `set(workout_exercise_id)`. Prva dva ubrzavaju povijest i prethodni rezultat vježbe.
- Predefinirane vježbe upisuju se jednom, u vlastitoj migraciji (`drizzle-kit generate --custom`). **Prijedlog**

## 6. Izračuni

Zagrijavajuće serije (`is_warmup`) ne ulaze ni u jedan izračun.

| Pokazatelj | Formula | Razina |
| --- | --- | --- |
| Volumen vježbe | Σ (ponavljanja × težina) | vježba na treningu |
| Volumen treninga | Σ volumena vježbi | trening |
| Najveća težina | max (težina) | vježba na treningu |
| Ukupno ponavljanja | Σ ponavljanja | vježba na treningu |
| Procijenjeni 1RM | težina × (1 + ponavljanja / 30), najbolja serija (Epley) | vježba na treningu |
| Osobni rekord* | najveća vrijednost pokazatelja u cijeloj povijesti vježbe | vježba |

Kad su sve serije jednake, volumen je *serije × ponavljanja × težina*, kako traži zadatak. Zbroj po serijama radi i kad se serije razlikuju.

**Prethodni rezultat** vježbe su serije iz zadnjeg **završenog** treninga koji sadrži tu vježbu, bez trenutačnog treninga.

**Grafovi:** jedna točka po treningu, os x je datum. Podataka je malo (stotine treninga), pa se agregacija radi u TypeScriptu nad rezultatom jednog upita.

## 7. Ekrani i navigacija

**Prijedlog** strukture u `app/`:

```text
app/
├── _layout.tsx            Stack; otvaranje baze i migracije
├── (tabs)/
│   ├── _layout.tsx        donja traka
│   ├── index.tsx          Početna: „Start workout”, zadnji treninzi, tjedni sažetak
│   ├── history.tsx        Povijest: popis treninga po datumu
│   └── settings.tsx       Postavke: jedinice, tema, sigurnosna kopija
├── workout/
│   ├── active.tsx         Aktivni trening: vježbe, unos serija, prethodni rezultat, odmor
│   └── [id].tsx           Detalji treninga: vježbe, serije, volumen; uređivanje
└── exercise/
    ├── select.tsx         Odabir vježbe (modal): pretraga, filtar, nova vježba
    └── [id].tsx           Napredak vježbe: grafovi, rekordi, prethodni rezultati
```

## 8. Struktura koda i baza u praksi

```text
app/                       ekrani (odj. 7)
src/
├── components/            zajedničke komponente (npr. unos serije, stepper +/−)
├── hooks/                 hookovi nad repozitorijima
├── db/
│   ├── schema.ts          Drizzle shema
│   ├── client.ts          otvaranje baze
│   └── repositories/      upiti po području (vježbe, treninzi, statistika)
└── lib/
    ├── calculations.ts    izračuni (odj. 6)
    └── units.ts           kg ↔ lb
drizzle/                   generirane migracije, u gitu
drizzle.config.ts          dialect: sqlite, driver: expo
```

**Tijek promjene sheme:** izmjena `src/db/schema.ts` → `npx drizzle-kit generate` → commit nove migracije iz `drizzle/`. Pri pokretanju aplikacija migracije primjenjuje hookom `useMigrations` (`drizzle-orm/expo-sqlite/migrator`). Da bi Metro učitao `.sql` datoteke, treba `babel-plugin-inline-import` i ekstenziju `sql` u `metro.config.js`. CI ponovno pokreće `drizzle-kit generate` i javlja grešku ako nastane nova datoteka, jer to znači da migracija nije commitana.

## 9. Testiranje

| Razina | Što | Alat |
| --- | --- | --- |
| Unit | izračuni, pretvorba jedinica | Jest |
| Podatkovni sloj | repozitoriji: upis, brisanje, prethodni rezultat, agregacije | Jest nad `better-sqlite3` (samo `devDependency`; expo-sqlite ne radi u Node.js). Repozitoriji primaju `db` kao parametar, pa testovi predaju bazu u memoriji s istom shemom i migracijama. **Prijedlog** |
| Komponente | unos serije, stepper, popisi | React Native Testing Library |
| Ručno | N1, N2 i N4 na pravom Android uređaju i u Expo Go na iOS-u | kontrolni popis prije izdanja |
| Korisnici | najmanje 5 korisnika izvan tima zabilježi trening bez pomoći (faza 5) | promatranje, broj dodira |

## 10. Automatizacija

| Kada | Što |
| --- | --- |
| Commit | husky + lint-staged (ESLint, Prettier nad promijenjenim datotekama), commitlint (Conventional Commits) |
| Pull request | CI: lint, `tsc --noEmit`, Jest, `npx expo install --check`, provjera migracija |
| Oznaka `vX.Y.Z` | GitHub Actions + `eas build --profile preview` (APK) → GitHub Release; treba `EXPO_TOKEN` |
| Mjesečno | `npx expo install --fix` ručno; Dependabot samo za GitHub Actions i sigurnosna upozorenja |

Besplatni EAS plan ima ograničen broj buildova, pa se APK gradi samo za izdanja.

## 11. Tehnički plan po iteracijama

| Kontrolna točka | Datum | Tehnički rezultat | Verzija |
| --- | --- | --- | --- |
| M2 | 4.12.2026. | Expo projekt, CI, lint, Drizzle postavke, shema v1, prototip (baza + jedan graf) | |
| M3 | 18.12.2026. | katalog vježbi, aktivni trening s brzim unosom, izračun volumena, povijest | `v0.1.0` |
| M4 | 15.1.2027. | grafovi, 1RM, osobni rekordi, Should funkcije; nakon toga nema novih funkcija | `v0.2.0` |
| M5 | 22.1.2027. | ispravci nakon testiranja s korisnicima | `v0.3.0` |
| M6 | 29.1.2027. | završna verzija | `v1.0.0` |

## 12. Tehnički rizici

| Rizik | Mjere |
| --- | --- |
| Tim ne poznaje Expo i React Native | Expo tutorial za sve u fazi 2; prototip prije M2; rad u parovima |
| Unos nije dovoljno brz (N1) | wireframeovi testirani s 2–3 osobe prije implementacije; mjerenje dodira |
| Gubitak podataka pri promjeni sheme (N3) | migracije od prvog dana, CI provjera, testovi repozitorija; izvoz kao sigurnosna kopija (Could) |
| Potreban modul izvan Expo SDK-a | koristiti samo pakete koji rade u Expo Go; inače development build, a iOS ostaje bez testiranja |
| Ograničenje EAS buildova | APK samo na oznakama verzija |

## 13. Otvorena tehnička pitanja

- Testiranje repozitorija: `better-sqlite3` ili mock (odj. 9)
- 1RM za 1 ponavljanje: Epley daje težina × 1,033; prikazati stvarnu težinu?
- Tjelesne vježbe (zgibovi, sklekovi): težina 0 daje volumen 0; treba li dodatno opterećenje ili prikaz samo ponavljanja?
- Format sigurnosne kopije (JSON cijele baze ili CSV po tablicama), ako se radi
